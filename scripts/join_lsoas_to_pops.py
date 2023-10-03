"""
Join LSOA codes to LSOA populations to be used in compiled_workbooks for LSOA task

Inputs:
    - LSOA populations
    - List of LSOAs in TRSE work

Outputs:
    - LSOAs within TRSE work joined with LSOA level population data

"""
#### Imports ####
import pandas as pd
import os

os.chdir(r'Y:\PBA\Analysis\10 PBA TRSE Task 4 for james\TRSE Task 4')

# Load data
lsoa_data_path = 'supporting data.xlsx'

lsoa_pops = pd.read_excel(lsoa_data_path, sheet_name='pop')
lsoa_car_access = pd.read_excel(lsoa_data_path, sheet_name='Car access')
lsoa_pt_access = pd.read_excel(lsoa_data_path, sheet_name='PT access')
lsoa_green_spaces = pd.read_excel(lsoa_data_path, sheet_name='Green spaces')

trse_lsoa_codes = pd.read_csv('trse_lsoa_codes.csv')

# Filter supporting data sheets to contain only LSAOs that are present within TRSE work.
lsoa_pops = lsoa_pops.loc[lsoa_pops['LSOA11CD'].isin(trse_lsoa_codes['trse_lsoa_codes'])]
lsoa_car_access = lsoa_car_access.loc[lsoa_car_access['LSOA code (2011)'].isin(trse_lsoa_codes['trse_lsoa_codes'])]
lsoa_pt_access = lsoa_pt_access.loc[lsoa_pt_access['LSOA11CD'].isin(trse_lsoa_codes['trse_lsoa_codes'])]
lsoa_green_spaces = lsoa_green_spaces.loc[lsoa_green_spaces['LSOA11CD'].isin(trse_lsoa_codes['trse_lsoa_codes'])]

# Export datasets
lsoa_pops.to_excel('trse_lsoa_pop_info.xlsx', index=False)
lsoa_car_access.to_excel('trse_lsoa_car_access_info.xlsx', index=False)
lsoa_pt_access.to_excel('trse_lsoa_pt_access_info.xlsx', index=False)
lsoa_green_spaces.to_excel('trse_lsoa_green_spaces.xlsx', index=False)
