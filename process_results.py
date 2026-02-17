# -*- coding: utf-8 -*-
"""
Created on Tue Feb 17 10:43:29 2026

@author: alice
"""

import pandas as pd
import os
import matplotlib.pyplot as plt

# Identify the result file to process
run_id = 'uncoord_full_electrification'  # Match this to your run_id in main.py
input_file = os.path.join('results', f'{run_id}_full_timeseries.csv')

if not os.path.exists(input_file):
    print(f"Error: {input_file} not found. Run generate_profiles.py first.")
else:
    # Load the results
    df = pd.read_csv(input_file)
    
    # 1. Calculate Statistics for each DeSO
    # (Average, Max, Percentiles 25/50/75/95, and Std Dev)
    stats = df.describe(percentiles=[.25, .50, .75, .95]).transpose()
    stats = stats[['mean', 'max', '25%', '50%', '75%', '95%', 'std']]
    
    # Save statistics to CSV
    stats_path = os.path.join('results', f'{run_id}_stats.csv')
    stats.to_csv(stats_path)
    print(f"Statistics saved to {stats_path}")

    # 2. Calculate Typical Daily Load Curve
    # We group by the hour of the day (0-23)
    # The dataframe index is hourly, so index % 24 gives the hour
    df['Hour'] = [i % 24 for i in range(len(df))]
    daily_curve = df.groupby('Hour').mean()
    
    # Save daily curve to CSV
    curve_path = os.path.join('results', f'{run_id}_daily_curve.csv')
    daily_curve.to_csv(curve_path)
    print(f"Typical daily curve saved to {curve_path}")

    # 3. Optional: Plot the average aggregate load for the whole region
    plt.figure(figsize=(10, 6))
    plt.plot(daily_curve.index, daily_curve.mean(axis=1), label='Mean Aggregate Load')
    plt.title(f'Typical Daily EV Charging Profile ({run_id})')
    plt.xlabel('Hour of Day')
    plt.ylabel('Average Power [kW]')
    plt.grid(True)
    plt.savefig(os.path.join('results', f'{run_id}_daily_plot.png'))
    print("Summary plot saved to results folder.")