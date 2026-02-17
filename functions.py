# -*- coding: utf-8 -*-
"""
Created on Thu Feb 12 15:20:57 2026

@author: alice
"""

import pandas as pd
import matplotlib.pyplot as plt
import random
import time
import numpy as np
from scipy.stats import norm




def get_ev_models():
    
    """
    Constructs a dictionary of EV models with their corresponding battery sizes and energy consumption.
    This data was collected in 2023 when the model was built. The models selected were the most common EV models in Sweden at the date of collection.
    Updated electric car model shares can be found at https://powercircle.org/statistik/
    Energy consumption data is collected from the US Environment Protection Agency (EPA)
    Battery size data is collected from EV Database, https://ev-database.org
    
    Returns:
    - dict: Keys are EV model codes, values are dicts containing full name, battery size, and energy consumption.
    """
    
    names=['VW ID.4', 'KIA E-niro', 'Tesla Model 3', 'Tesla Model Y', 'Nissan Leaf', 'Volvo XC40 P8', 'Polestar 2', 'Renault Zoe']
    codes=['VW','KIA','Tesla3','TeslaY','Nissan','Volvo','Polestar','Renault']
    # Battery sizes and energy consumption: VW ID.4, KIA E-niro, Tesla Model 3, Tesla Model Y, Nissan Leaf, Volvo XC40 P8, Polestar 2, Renault Zoe
    # In kWh
    battery_size=[77,64.8,57.5, 57.5, 39, 66, 67, 52]
    # In kWh/km
    energy_consumption=[0.193,0.18,0.155,0.174,0.186,0.243,0.193,0.170]
    ev_models1=[]
    for i,car in enumerate(codes):
        temp={'Full name':names[i],'Battery size':battery_size[i],'Energy consumption':energy_consumption[i]}
        ev_models1.append(temp)
    ev_models={}
    for i,car in enumerate(ev_models1):
        ev_models.update({str(codes[i]):car})
    return ev_models


def update_charging(soc,case):
    """
    Determines whether a car should start charging based on current state of charge (SOC)
    and charging behavior case.
    
    Parameters:
    - soc (float): State of charge as a percentage.
    - case (str): Charging policy ("Random charging", "Charge at 80", or "Charge at 30").
    
    Returns:
    - bool: True if the car should charge, False otherwise.
    """
    ...

    if case == 'Random charging':
        if soc <= 30:
            return True
        elif (soc < 80):
            choice=random.choice([True,False])
            return choice
        else:
            return False
    elif case == 'Charge at 80':
        if soc <= 80:
            return True
        else:
            return False
    elif case == 'Charge at 30':
        if soc <= 30:
            return True
        else:
            return False
    else:
        print('Not valid case')