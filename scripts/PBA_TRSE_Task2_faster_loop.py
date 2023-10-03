# -*- coding: utf-8 -*-
"""
Created on Thu Apr 13 12:16:45 2023

@author: Signalis
"""

# -*- coding: utf-8 -*-
"""
Created on Tue Mar 21 13:51:00 2023

@author: Signalis

Before running this script, ensure the following are updated: 

    L59 - a1_jt file path
    L60 - a2_jt file path
    L71 - OTP response file path
    L63 - Results save path

"""

#### Imports ####

import pandas as pd
import math
import tqdm
import time
import os


#### Functions ####

def path(a, b, x):
    f = a * math.sin(b * x)
    return f


def jt_correction(p, q, r, step_no):
    A = (p + q)  # root or /2 or leave?

    if A == 0:
        A = 1

    B = math.pi / r

    step = r / step_no

    t = 0

    for i in range(step_no):
        x1 = step * i
        x2 = step * (i + 1)
        y1 = path(A, B, x1)
        y2 = path(A, B, x2)
        delta_l = math.sqrt((y2 - y1) ** 2 + (x2 - x1) ** 2)
        t = t + delta_l

    return t


#### Global Variables ####
step_size = 8  # For pt_sin_correction
save_results_path = r'Y:\PBA\Analysis\Data(copy)\OTP data'
max_JT = 45  # minutes

a1_jt_path = r'Y:\PBA\Analysis\Data(copy)\OTP data\final_rest_of_north(pen_run)_a1_jt.csv'
a2_jt_path = r'Y:\PBA\Analysis\Data(copy)\OTP data\final_rest_of_north(pen_run)_a2_jt.csv'


run_codes = ['K1Q 2052',
             'K1P 2042',
             'KZV 2042',
             'KZW 2052',
             'KZJ 2052',
             'JPJ 2052',
             'JPI 2042',
             'KZI 2042']
             # 'IGU 2018']


for code in run_codes:
    run_code, run_year = code.split(' ')
    print(run_code, run_year)

    # Auto-create filename
    save_results_filename = '_'.join((str(max_JT),
                                      'mins_max_time_',
                                      'rest_of_north(pen_run)BUS_WALK_rail_jt',
                                      run_code,
                                      run_year,
                                      '.csv'))

    #### Load Data ####

    ## Rail data
    rail_dir = r'Y:\PBA\Accessibility analysis\inputs'
    rail_fn = 'NoRMS_JT_' + run_code + '_' + run_year + '.csv'

    print('Loading rail JTs:', rail_fn)

    # Load the rail JT data
    rail_jt = pd.read_csv(os.path.join(rail_dir, rail_fn))

    # Rail JTs contain info for pairs where o==d. For our TRSE analysis we want
    #   journeys that require train travel. Hence, remove inter-zone trips
    rail_jt = rail_jt.loc[rail_jt['o'] != rail_jt['d']]

    #### Pre-Processing ####

    # Load LSOA to NoRMSid Lookup
    LSOAid_to_NoRMSid = pd.read_csv(r'Y:\PBA\Analysis\Zones\LSOAid_to_NoRMSid_in_LSOAs.csv')

    # NB: There will always be more Origins than Destinations as destinations must
    #     contain a NoRMS centroid (station)

    '''
    For the results we have, we must work out the JT from every LSOA to those LSOAs
        that contain a NoRMS centroid... (a1 trips)

    We must then also work out the JT from every relevant NoRMS containing LSOA as 
        a Origins to any LSOA that they may reach (a2 trips)

    To clarify: a1 matrix will have every LSOA as O, but only LSOAs with NoRMS as D
                a2 matrix will have only LSOAs with NoRMS as O, but every LSOA as D
                L matrix is matrix of Rail JT
    '''

    # NB: a1 & a2 JT matrices are made by Y:\PBA\Analysis\create_a1_2_jt_matrix.py
    print('\nLoading a1, a2 JT matrices.')

    # Load a1 & a2 JT matrices
    a1_jts = pd.read_csv(a1_jt_path)
    a2_jts = pd.read_csv(a2_jt_path)

    # The a1 & a2 matrices will have NaN for routes where no PT could be used in
    # reasonable time period, as opposed to an OTP run error. As such, we should
    # remove them here.
    a1_jts = a1_jts[a1_jts['JT'].isna() == False]
    a2_jts = a2_jts[a2_jts['JT'].isna() == False]

    '''
    From call with Adam (24/03) 'The TRSE analysis dataset excludes any journey if
                                 a leg of that journey has a JT exceeding 60 mins'

        Given this, we can remove any a1, a2 & NoRMS journeys IF the JT > 60 mins
    '''

    # Remove trips if the JT exceeds 60 minutes.
    a1_jts = a1_jts[a1_jts['JT_mins'] <= max_JT]
    a2_jts = a2_jts[a2_jts['JT_mins'] <= max_JT]
    rail_jt = rail_jt[rail_jt['jt'] <= max_JT]

    # Remove any rail_jts of 0
    rail_jt = rail_jt[rail_jt['jt'] != 0]

    # Load NoRMS stations & corresponding LSOAs
    LSOA_to_NoRMS_centres = pd.read_csv(r'Y:\PBA\Analysis\Zones\LSOAid_to_NoRMSid_in_LSOAs.csv')

    # Join the NoRMS ids to a1 destination LSOA ids (add station IDs to LSOAs)
    a1_jts = pd.merge(how='left',
                      left=a1_jts,
                      right=LSOA_to_NoRMS_centres[['LSOA11CD', 'ZoneID']],
                      right_on='LSOA11CD',
                      left_on='Destination')

    # Re-formatting a1_jt.
    a1_jts.drop(columns=['LSOA11CD'], inplace=True)
    a1_jts.rename(columns={'ZoneID': 'a1_D_NoRMS_ID'}, inplace=True)

    # Set destination as index for a1_jts
    a1_jts.set_index(['Origin'], drop=False,
                     inplace=True)

    # Join NoRMS ids to a2 Origin LSOA ids (add station IDs to LSOAs)
    a2_jts = pd.merge(how='left',
                      left=a2_jts,
                      right=LSOA_to_NoRMS_centres[['LSOA11CD', 'ZoneID']],
                      right_on='LSOA11CD',
                      left_on='Origin')

    # Re-formatting a2_jt
    a2_jts.drop(columns=['LSOA11CD'], inplace=True)
    a2_jts.rename(columns={'ZoneID': 'a2_O_NoRMS_ID'}, inplace=True)

    # Store data in a list, before making into a DF later
    df_data = []

    # Add all possible train journeys to trips to train stations
    trips = pd.merge(left=a1_jts,
                     right=rail_jt,
                     how='left',
                     left_on='a1_D_NoRMS_ID',
                     right_on='o')

    # Check that NaN's have not been introduced into the df. If so, it's bcos
    #  a segment of JT exceeded the max_JT specified at the top.
    trips = trips.dropna()

    if trips.empty:
        # Only NaNs returned = No trips within desired JT. Assess next origin
        print('trips is empty!!!111!!!')
        # continue

    # Re-formatting
    trips = trips[['Origin', 'Destination', 'JT', 'JT_mins',
                   'a1_D_NoRMS_ID', 'd', 'jt']]

    trips.rename(columns={'JT': 'a1_JT',
                          'JT_mins': 'a1_JT_mins',
                          'Origin': 'a1_Origin',
                          'Destination': 'a1_Destination',
                          'd': 'a2_O_NoRMS_ID',
                          'jt': 'a1_a2_NoRMS_jt'},
                 inplace=True)

    trips.reset_index(drop=True, inplace=True)

    # Add all possible LSOAs reachable from a2_Origin NoRMS stations
    trips = trips.merge(how='left',
                        right=a2_jts,
                        left_on='a2_O_NoRMS_ID',
                        right_on='a2_O_NoRMS_ID')

    # Check that NaN's have not been introduced into the df. If so, it's bcos
    #  a segment of JT exceeded the max_JT specified at the top.
    trips = trips.dropna()

    if trips.empty:
        # Only NaNs were left = No trip in maximum time. Assess next origin_id
        print('trips 2 are empty!!!222')
        # continue

    # Re-formatting
    trips.rename(columns={'Origin': 'a2_Origin',
                          'Destination': 'a2_Destination',
                          'JT': 'a2_JT',
                          'JT_mins': 'a2_JT_mins'},
                 inplace=True)

    trips.reset_index(drop=True, inplace=True)

    # We now have a DF of complete possible trips for a given a1 Origin.
    # Set a1_Origin & a2_Destination as index to find variations for a given
    # a1_O and a2_D journey utilising .loc[].

    # trips.set_index(['a2_Destination'], drop=False,
    #                   inplace=True)

    print('Assessing:', f'{len(trips):,d}', time.strftime("%H:%M:%S - %Y", time.localtime()))
    sin_corrected_jts = []
    for a1_jt, a2_jt, NoRMS_jt in tqdm.tqdm(zip(trips['a1_JT_mins'], trips['a2_JT_mins'], trips['a1_a2_NoRMS_jt'])):
        # Calculate & store sin_corrected JT
        sin_corrected_jts.append(jt_correction(a1_jt, a2_jt, NoRMS_jt, step_size))

    print(time.strftime("%H:%M:%S - %Y", time.localtime()))

    # Add sin corrected JTs
    trips['sin_corrected_jt'] = sin_corrected_jts

    # Calculate percentage of trip by mode
    trips['addative_jt'] = trips['a1_JT_mins'] + trips['a2_JT_mins'] + trips['a1_a2_NoRMS_jt']
    trips['bus_percent'] = (trips['a1_JT_mins'] + trips['a2_JT_mins']) / trips['addative_jt']
    trips['rail_percent'] = trips['a1_a2_NoRMS_jt'] / trips['addative_jt']

    trips['od_code'] = trips['a1_Origin'] + '_' + trips['a2_Destination']

    print('grpby', time.strftime("%H:%M:%S - %Y", time.localtime()))
    best_trips = trips[['od_code', 'sin_corrected_jt']].groupby('od_code').min()
    print('done', time.strftime("%H:%M:%S - %Y", time.localtime()))

    # merge on bus_percent, rail_percent
    best_trips['od_code'] = best_trips.index
    best_trips.reset_index(inplace=True, drop=True)

    print('merge', time.strftime("%H:%M:%S - %Y", time.localtime()))
    best_trips = best_trips.merge(how='left',
                                  right=trips[['od_code', 'bus_percent',
                                               'rail_percent',
                                               'sin_corrected_jt']],
                                  left_on=['od_code', 'sin_corrected_jt'],
                                  right_on=['od_code', 'sin_corrected_jt'])
    print('merge done', time.strftime("%H:%M:%S - %Y", time.localtime()))

    # Formatting
    best_trips[['o', 'd']] = best_trips['od_code'].str.split('_', expand=True)

    best_trips.rename(columns={'sin_corrected_jt': 'jt',
                               'bus_percent': 'bus_pct',
                               'rail_percent': 'rail_pct'},
                      inplace=True)

    best_trips = best_trips[['o', 'd', 'jt', 'bus_pct', 'rail_pct']]

    result_origins = list(best_trips['o'].unique())
    result_destinations = list(best_trips['d'].unique())

    print('Trip information stored for', f'{len(best_trips):,d}', 'journeys.',
          '\nIncluding:', len(result_origins), 'origin zones.', '\nIncluding:',
          len(result_destinations), 'destination zones.')

    # =============================================================================
    # print('Saving:\n', save_results_filename)
    # best_trips.to_csv(os.path.join(save_results_path,
    #                             save_results_filename),
    #                index=False)
    # =============================================================================
    print('\nScript complete @:', time.strftime("%H:%M:%S - %Y", time.localtime()))
