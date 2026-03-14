"""
===============================================================================
File: ripe_funcs.py
Description: Functions and scripts for retrieving and preprocessing data
             from the RIPE Atlas API.

This module provides utilities to:
  - Query RIPE Atlas measurements via the API
  - Download and store measurement results
  - Preprocess and clean measurement data
  - Support batch processing for multiple probes or measurements
  - Some plotting graphs features

Author: Pavel Izyumov
Email: izyumov.ps@phystech.edu
Date: 2026-03-14
License: MIT License (or specify another license)

Dependencies:
  - requests
  - pandas
  - time
  - numpy
  - matplotlib

Usage Examples:
    from ripe_funcs import plot_cdf, get_probe_info

    # Get Probe's metadata
    clean_data = get_probe_info(pdr_id = 1234)
===============================================================================
"""

#process data
import pandas as pd
import numpy as np
# visual
import matplotlib.pyplot as plt
import requests
# во избежание временного бана за частые запросы 
import time

def plot_cdf(data, xname):
    plt.rcParams["figure.figsize"] = [7.50, 3.50]
    plt.rcParams["figure.autolayout"] = True

    #data = df_tr[df_tr.hop_1_rtt_mean.notna()].hop_1_rtt_mean.values
    count, bins_count = np.histogram(data, bins=20)
    pdf = count / sum(count)
    cdf = np.cumsum(pdf)
    plt.plot(bins_count[1:], cdf, label="CDF")
    plt.xlabel(xname)
    #plt.legend()
    plt.grid()
    plt.show()

# Function to calculate missing values by column
def missing_values_table(df):
    # Total missing values
    mis_val = df.isnull().sum()
    
    # Percentage of missing values
    mis_val_percent = 100 * df.isnull().sum() / len(df)
    
    # Make a table with the results
    mis_val_table = pd.concat([mis_val, mis_val_percent], axis=1)
    
    # Rename the columns
    mis_val_table_ren_columns = mis_val_table.rename(
    columns = {0 : 'Missing Values', 1 : '% of Total Values'})
    
    # Sort the table by percentage of missing descending
    mis_val_table_ren_columns = mis_val_table_ren_columns[
        mis_val_table_ren_columns.iloc[:,1] != 0].sort_values(
    '% of Total Values', ascending=False).round(1)
    
    # Print some summary information
    print ("Your selected dataframe has " + str(df.shape[1]) + " columns.\n"      
        "There are " + str(mis_val_table_ren_columns.shape[0]) +
            " columns that have missing values.")
        
    # Return the dataframe with missing information
    return mis_val_table_ren_columns

def get_mean_rtt_drom_res(answer):
    if 'result' not in answer.keys():
        # error
        return None
    results = answer['result']
    rtt_arr = []
    for res in results:
        # error
        if 'rtt' not in res.keys():
            continue
        rtt_arr.append(res['rtt'])
    if len(rtt_arr)==0:
        return None
    return np.mean(rtt_arr)

def get_probe_info(id_probe):
    '''
    Return ('asn_v4' - ASN_code for IPv4, 'country_code', 'is_anchor' - is it anchor ?)
    '''
    if id_probe in [2044, 3308, 2330, 2631, 3036, 3395, 3763, 4113, 4435, 4809, 3274, 3192]:
        time.sleep(20)
    time.sleep(3)
    #print('Get info for:', id_probe)
    req = 'https://atlas.ripe.net/api/v2/probes/' + str(id_probe)
    respond = requests.get(url=req)
    respond = respond.json()
    

    if 'geometry' in respond:
        loc = respond['geometry']['coordinates']
        long = loc[0]
        lat = loc[1]
    else:
        long = None
        lat = None
    for i in range(len(respond['tags'])):
        if respond['tags'][i]['name'][:-1]=='system: V':
            eq_type = respond['tags'][i]['name']
            break
        elif respond['tags'][i]['name'][8:]=='Software':
            eq_type = 'Software'
            break
        else:
            # вроде если ни то ни то, то это якоря
            eq_type = 'Anchor' #respond['tags'][1]['name']

    return (respond['asn_v4'], respond['country_code'], respond['is_anchor'], eq_type, long, lat) #respond['tags'][1]['name'])

def get_data_by_api(req):
    respond = requests.get(url=req)
    respond = respond.json()
    return pd.DataFrame(respond)


def get_probe_info2(list_id):
    '''
    Return info about probes by list of ids

    return info about first 100 probes
    '''    
    req = 'https://atlas.ripe.net/api/v2/probes/' 

    params = {'id__in': ','.join(map(str, list_id))  }

    headers = {'Content-Type': 'application/json'}

    response = requests.get(req, params=params, headers=headers)

    if response.status_code == 200:
        probe_info = response.json()
        
        # Create a Pandas DataFrame from the probe information
        df = pd.DataFrame(probe_info['results'])
        
        # Display the DataFrame
        return df
    else:
        print(f'Error: {response.status_code}')
        return None
    
def get_asn_name(id):
    req = 'https://www.peeringdb.com/api/as_set/' + str(id)  
    respond = requests.get(url=req)
    if len(respond.content)>0 and 'data' in respond.json():
        res = respond.json()['data'][0][str(id)]
    else:
        res = 'Other'
    return res

def get_network_type_by_asn(asn):
    '''
    Get network tyme from PeeringDB by ASN
    '''
    time.sleep(2)
    # PeeringDB API base URL
    base_url = "https://peeringdb.com/api/net"

    # Make a GET request to PeeringDB API for the specified ASN
    response = requests.get(f"{base_url}?asn={asn}")

    #  проверим что ответ пришел
    if response.status_code == 200:
        data = response.json()
        # проверим что ответ не пустой
        if 'data' in data and data['data'] and 'info_type' in  data['data'][0]:
            network_type = data['data'][0]['info_type']
            return network_type
        else:
            #print(f"No data found for ASN {asn}")
            return None
    else:
        print(f"Error: Unable to fetch data. Status code: {response.status_code}")
        return None
    
def get_type(respond):
    '''
    get hardware version from list of tags
    used for dataframe from get_probe_info2
    '''
    for i in range(len(respond)):
        if 'name' in respond[i] and respond[i]['name'][:-1]=='system: V':
            eq_type = respond[i]['name']
            break
        elif respond[i]['name'][8:]=='Software':
            eq_type = 'Software'
            break
        else:
            # вроде если ни то ни то, то это якоря
            eq_type = 'Anchor' #respond['tags'][1]['name']
    return eq_type
    
def get_probe_info_by_list_of_probes(prb_ids):
    dfs = []
    chunks = len(prb_ids) // 100 +1
    for i in range(chunks):
        sub = prb_ids[i*100:100*(i+1)]
        df = get_probe_info2(sub)
        df['long'] = df.apply(lambda x: x['geometry']['coordinates'][0] if 'coordinates' in x['geometry']  else None, axis=1)
        df['lat'] = df.apply(lambda x: x['geometry']['coordinates'][1] if 'coordinates' in x['geometry']  else None, axis=1)
        df['system'] = df.apply(lambda x: get_type(x.tags), axis=1)
        dfs.append(df)
        time.sleep(3)
    res = pd.concat(dfs)  
    res = res[['id', 'asn_v4', 'country_code', 'is_anchor', 'system', 'long', 'lat']]
    res = res.rename({'id': 'prb_id', 'asn_v4': 'ASN'}, axis=1)
    return res