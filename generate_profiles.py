# -*- coding: utf-8 -*-
"""
Created on Thu Jan 22 12:00:04 2026

@author: alice
"""

# This script runs models to create charging profiles. For details on the functions used, see functions.py

import os
import pandas as pd
import matplotlib.pyplot as plt
import random
import time
import numpy as np
from scipy.stats import norm
from functions import get_ev_models, update_charging

# Measure time taken for script to run
start=time.time()

# Create results folder, if not already existing
if not os.path.exists('results'):
    os.makedirs('results')

# Select the share of the cars that are electric
share=1
# Select number of days simulated
N=375 # One year 
# Select case: 'smart" or "uncoord"
case='uncoord'
# Give your run an ID
run_id='uncoord_full_electrification'

# Read data sources
deso_travel = pd.read_csv(os.path.join('Data', 'deso_traveldata.csv'), index_col=3)             # The raw data is collected from SCB and curated to match a DeSO model resolution
aadt_travel = pd.read_csv(os.path.join('Data', 'aadt_deso.csv'), index_col=0)                   # See separate script on the creation of this file
ev_models = get_ev_models()                                                                     # See comments on EV model data in the function
home_start = pd.read_csv(os.path.join('Data', f'Home_starts_{case}.csv'), index_col=0)          # The underlying dataset is not publicly available
public_start = pd.read_csv(os.path.join('Data', 'public_starts.csv'), index_col=0)              # The underlying dataset is not publicly available
public_dur = pd.read_csv(os.path.join('Data', 'public_duration.csv'), index_col=0)              # The underlying dataset is not publicly available
public_power = pd.read_csv(os.path.join('Data', 'public_power.csv'), index_col=0)               # The underlying dataset is not publicly available


#Create empty numpy array to store data
full_profile=np.zeros([N*24,len(deso_travel.index)])

#%%


# Estimate the total energy requirement and keep track of iterations
energy = 0
zonenbr = 0

# Create look-up dictionary for the DeSO regions
loc_map = {name: i for i, name in enumerate(aadt_travel.index)}                                 

# Loop through one DeSO at a time
for zone,row in deso_travel.transpose().iloc[:,:].items():
    # Keep track of simulation
    name= str(zone)
    print(f"DeSo {name} pending")
    
    # Collect data
    nbr_cars=int(row['Antal Bilar'])*share                                  # Number of registered cars in DeSO times the electrification share
    all_cars=np.random.choice(list(ev_models.values()), size=nbr_cars)      # Randomly select car models for all registered cars
    km,kmstd=row['Travel (km)'],row['Travel +-']                            # Average and standard deviation of kilometers travelled per day
    batteries=[el['Battery size'] for el in all_cars]                       # Give each car a battery size according to model stats
    cons=[el['Energy consumption'] for el in all_cars]                      # Give each car an energy consumption according to model stats
    
    # Set up home arrays
    SOC=np.random.uniform(50, 100, nbr_cars)                                    # Starting SOC is randomly selected for all EVs
    start_time = np.random.choice(range(24), size=10000000, p=home_start['Probability'])       # Randomly draw set of starting times based on starting time distribution
    home_charging_powers = np.random.choice([3.5, 7.4, 11], size=nbr_cars)      # Randomly select the home charging power of each EV
    
    # Set up public arrays
    location = np.random.choice(aadt_travel.index, size=nbr_cars * N, p=aadt_travel['Final Probability'])       # Randomly decide DeSO where public charging takes place
    dc_pow = np.random.choice(public_power.index, size=nbr_cars * N, p=public_power['Probability']) + 5         # Randomly decide public charging power
    dc_starts = np.random.choice(public_start.index, size=nbr_cars * N, p=public_start['Probability'])          # Randomly decide public charging starting time
    probs = public_dur['Probability'] / public_dur['Probability'].sum()                                         # Normalize
    dc_durations = np.random.choice(public_dur.index, size=nbr_cars * N, p=probs) + 1                           # Randomly decide public charging duration
    
    # Track indices
    start_time_idx, loc_idx = 0, 0
    
    # Simulate one day at a time
    for day in range(N):
        # Calculate energy used and update SOC for all cars
        km_driven = norm.rvs(km, kmstd, size=nbr_cars)          # Driving distance selected randomly
        energy_used = km_driven * cons
        energy+=energy_used.sum()
        energy_left = (SOC * batteries / 100) - energy_used
        SOC = (energy_left / batteries) * 100
        
        # Check charging decision
        charge_check = np.array([update_charging(soc, 'Random charging') for soc in SOC])
        cars_to_charge = np.where(charge_check)[0]
        
        # Iterate all cars where charging happens
        for i in cars_to_charge:
            # If home charging, continue
            if random.random() < 0.97:     
                # Collect starting time
                hour=start_time[start_time_idx] + (24*day)
                start_time_idx += 1
                # Collect power
                charging_power = home_charging_powers[i]
                # Calculate duration and end time of charging session
                duration = int((batteries[i] - energy_left[i]) / charging_power) + 1
                end_time = min(hour + duration, N * 24)
                # Update charging profile
                full_profile[hour:end_time,zonenbr] += charging_power
                # Assume all EVs charge until full battery
                SOC[i]=100  
            # Else, public charging
            else:
                # Select location for charging
                loc_name=location[loc_idx]
                col_idx = loc_map[loc_name]
                # Select charging power
                charging_power=dc_pow[loc_idx]
                # Select start time
                hour=dc_starts[loc_idx] + (24*day)
                # Calculate duration and end time
                duration = dc_durations[loc_idx]
                end_time = min(hour + duration, N * 24)
                # Add to charging profile
                full_profile[hour:end_time,col_idx] += charging_power
                loc_idx += 1
                # Update SOC
                SOC[i] = min(100, SOC[i] + ((charging_power * duration) / batteries[i] * 100))
    zonenbr += 1        # Update iteration tracker
    # full_profile[:,zonenbr]+=charging_profile

#%%    
# Convert to dataframe
df_profile=pd.DataFrame(full_profile)
df_profile.columns=deso_travel.index      
df_profile=df_profile.iloc[240:,:]          #Remove first 10 days due to fluctuations
    
file_path = os.path.join('results', f'{run_id}_full_timeseries.csv')
df_profile.to_csv(file_path, index=False)

# Check the time it took for the script to run
end=time.time()
print('Time elapsed: ' + str(round(end-start,2)) + 's = ' + str(round((end-start)/60,2)) + ' min')