"""
Script to compile a lookup from LSOA11 codes to LAD11 codes to Region(17) names
  for TRSE accessibility analysis work.

"""

import pandas as pd

trse_lsoa_codes = pd.read_csv(r'Y:\PBA\Analysis\10 PBA TRSE Task 4 for james\TRSE Task 4'
                              r'\trse_lsoa_codes.csv')
lsoa_lad_lookup = pd.read_csv(r'Y:\Data Strategy\Data\Accessibility Analysis\import'
                              r'\PCD11_OA11_LSOA11_MSOA11_LAD11_EW_LU_aligned_v2.csv')
ladnm_region_lookup = pd.read_csv(r'Y:\Data Strategy\GIS Shapefiles\Merged_LAD_December_2011_Clipped_GB'
                                  r'\GB_LAD_Region.csv')

trse_lsoa_lad_region_lookup = trse_lsoa_codes

# Remove any LSOA that is not part of trse accessibility lsoa analysis
lsoa_lad_lookup = lsoa_lad_lookup.loc[lsoa_lad_lookup['LSOA11CD'].isin(trse_lsoa_codes['trse_lsoa_codes'])]

# Remove irrelevant columns
lsoa_lad_lookup = lsoa_lad_lookup[['LSOA11CD', 'LAD11CD', 'LAD11NM']]
# Drop duplicates
lsoa_lad_lookup.drop_duplicates('LSOA11CD', keep='first', inplace=True)

# Join lsoa_lad info onto the TRSE LSOAs
final_lookup = pd.merge(left=trse_lsoa_codes,
                        right=lsoa_lad_lookup,
                        how='left',
                        left_on='trse_lsoa_codes',
                        right_on='LSOA11CD')


# Join region names onto lookup using LAD11NM & Cmlad11nm
final_lookup = pd.merge(left=final_lookup,
                        right=ladnm_region_lookup,
                        how='left',
                        left_on='LAD11NM',
                        right_on='Cmlad11nm')

# Format final lookup
final_lookup['Rgn17nm'] = final_lookup['Rgn17nm'].str.lower()

final_lookup = final_lookup[['LSOA11CD', 'LAD11CD', 'Rgn17nm']]

# Export lookup
final_lookup.to_excel(r'Y:\PBA\Analysis\10 PBA TRSE Task 4 for james\TRSE Task 4'
                      r'\lsoa11cd_lad11cd_region17nm_lookup.xlsx',
                      index=False)
