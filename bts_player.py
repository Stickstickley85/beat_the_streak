# -*- coding: utf-8 -*-
"""
Created on Wed Nov 27 16:20:11 2019

@author: Stickstickley85
"""
#%%
import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import re


#%%

try:
    player = pd.read_csv(input('which player file do you want to use?: '))
    print('successfully read in the file' )
except:
    print('file does not exist in path')

#%% 
"""
Cleanup the data, dropping unnecessary columns and cleaning up the
home/away field
"""
player = player.drop(columns=['Gtm','Gcar', 'Rslt', 'SB', 'CS', 'OBP', 'SLG', 'RBI'])
player = player.loc[:,'Rk':'BOP']
col = list(player.columns)
col[3] = 'Home_Away'
player.columns = col
home = player.Home_Away.isnull()
ha = []
for h in home:
    if h == True:
        ha.append('Home')
    else:
        ha.append('Away')
player.Home_Away = ha

#%% Drop any rows that dont have data and list some descriptive stats
player = player.dropna()

### Some days had double headers, this adds a time element to differentiate when there are two games with the same date
time = []

for i in player.Date.str.contains(r'(2)',regex=False):
    if i == True:
        time.append('1:00:00 am')
    else:
        time.append('12:00:00 am')

player['GameTime'] = time

season = input('What season is this data from?: ')


player.Date = player.Date.str.replace(r' (1)','', regex=False)
player.Date = player.Date.str.replace(r' (2)','', regex=False)
player.Date = pd.to_datetime(player.Date + ' '+ season +' ' + ' ' + player.GameTime)

player.set_index('Date', inplace=True)

player = player.drop(columns='GameTime')

player.sort_index(ascending=True) 
print(player.describe(),player.info())
print(player.head())
#%% This creates a new column to identify if the batter got at least one hit in the game
player['Flag'] = player['H'] > 0

flag2 = []

for f in player['Flag']:
    if f == True:
        flag2.append(1)
    else:
        flag2.append(0)

player['Flag'] = flag2

player.head()

#%% Here we get a look at which teams the batter has had the most success getting at least one hit against each game
opp = player.groupby('Opp').Flag.agg(['sum','count'])
opp.columns = ['Hits','Games']

opp['success'] = opp['Hits']/opp['Games']

opp_common = opp[opp['Games']>5]
opp_common = opp_common.sort_values('success', ascending=False)
print(opp_common)

#%%This is to help identify how streaky a player is throughout the season
streak = []
for f in range(len(flag2)):
    if flag2[f] == 0:
        streak.append(0)
    else:
        try: streak.append(streak[-1] + 1)
        except: streak.append(0)
player['Streak'] = streak

#%% Here we create several different charts looking at hit success by month then week
player.Flag.loc['2022-04':'2022-09'].resample('M').mean().plot(kind='line')
plt.show()

player.Flag.loc['2022-04':'2022-09'].resample('W').mean().plot(kind='line')
player.Flag.loc['2022-04':'2022-09'].resample('M').mean().plot(kind='line')
player.Rk.loc['2022-04':'2022-09'].resample('W').count().plot(kind='bar')
plt.xlabel('Month')
plt.show()

player.Flag.loc['2022-04':'2022-09'].resample('W').mean().plot(kind='box')
plt.show()

player.Flag.loc['2022-04':'2022-09'].resample('W').mean().plot(kind='hist', bins=10)
plt.show()

print(player.Flag.loc['2022-04':'2022-09'].resample('W').mean().max())
print(player.Flag.loc['2022-04':'2022-09'].resample('W').mean().min())
print(player.Flag.loc['2022-04':'2022-09'].resample('W').mean())
print(player.Flag.loc['2022-04':'2022-09'].resample('M').mean())

#%%
player[player.Streak != 0].Streak.plot(kind='hist')
plt.show()
player['Streak'].plot(kind='line')
plt.xlabel('Month')
plt.show()

#old way print(round(player['Flag'].sum()/player['Flag'].count(),3))
print(round(player.Flag.mean(),3))
