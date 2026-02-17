# -*- coding: utf-8 -*-
"""
Created on Mon Feb 16 11:15:59 2026

@author: alice
"""

# This script calculates the probability distribution of public charger placements

import pandas as pd
import matplotlib.pyplot as plt
import random
import os

# Read file with aadt data per DeSO
aadt=pd.read_csv(os.path.join('Data', 'deso_aadt_input.csv'), index_col=2, sep=';')

# These shares are based on public charger data from Chargefinder, in 2023
share_city=0.65
weight_large_city=0.56  
aadt.loc[aadt['CITY'] != 'No','Probability'] = 0
aadt.loc[:,'Probability']=[el/aadt.loc[:,'max_aadtfordon'].sum() for el in aadt.loc[:,'max_aadtfordon']]  

# Set probability based on city or rural
def city(el):
    if el == 'Large':
        return weight_large_city
    elif el == 'Medium':
        return 1-weight_large_city
    else:
        return 0

# Calculate final weight and normalize probabilities
aadt['Probability City']=[city(el) for el in aadt['CITY']]
aadt['Probability City']=[el/aadt['Probability City'].sum() for el in aadt['Probability City']]
aadt['Probability City']=aadt['Probability City']*share_city
aadt['Probability']=aadt['Probability']*(1-share_city)
aadt['Final Probability']=aadt['Probability'] + aadt['Probability City']
aadt = aadt[['Final Probability']]

# Save probabilities file
file_path = os.path.join('Data', 'aadt_deso.csv')
aadt.to_csv(file_path, index=True)
