#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep 26 19:49:10 2019

@author: peabody
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from stravalib.client import Client
pd.set_option('display.max_columns', 500)

TOKEN = '0897e1b892446cd959c47a8e06af0de55d49f15c'

client = Client(access_token=TOKEN)

activities = client.get_activities(limit=100)
                                   
sample = list(activities)[0]

d = sample.to_dict()
example_activity = d['map']['id'].replace('a','')

activity_segments = client.get_activity(example_activity, include_all_efforts=True).segment_efforts

segment_id_list = []

for segment in activity_segments:
    segment_id_list.append(segment.segment.id)
    
