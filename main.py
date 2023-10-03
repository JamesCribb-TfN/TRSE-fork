from lib import amenity_processing, matrix_processing, indicator_outputs

import pandas as pd
import time

"""Main script that runs through the creation of indicators."""

# year options: 2018, 2042, 2052
# run code options: IGU, JPI, JPJ, K1P, K1Q, KZI, KZJ, KZV, KZW
run_code, run_year = "K1Q", "2052"
run_fresh = True

matrix_name = "LSOA_zoned_OD_pop_centre_column_matrix"
# Create LSOA zoned OD matrix with O & D Lat, Long coordinates
pop_centres = matrix_processing.centroids_col_max(matrix_name, run_fresh)

# Update rail_jt with Bus & Rail JT
rail_jt_name = "inputs/NoRMS_JT_" + run_code + "_" + run_year + ".csv"
car_jt_name = "inputs/NoHAM_JT_" + run_code + "_" + run_year + ".csv"
bus_jt_name = "inputs/north_run_final(so_far)_bus_jt_matrix.csv"

rail_jt_matrix = pd.read_csv(rail_jt_name)
car_jt_matrix = pd.read_csv(car_jt_name)
bus_jt_matrix = pd.read_csv(bus_jt_name)
non_rail_pt_jt_matrix = pd.read_csv("inputs/NoHAM_JT_" + "IGU" + "_" + "2018" + ".csv")  # modified car currently used as proxy

print("Starting journey times @ %s" % time.strftime("%H:%M:%S - %Y", time.localtime()))
journey_times = matrix_processing.journey_time_modes(pop_centres, bus_jt_matrix, rail_jt_matrix, car_jt_matrix, non_rail_pt_jt_matrix)

print("Starting amenity compile @ %s" % time.strftime("%H:%M:%S - %Y", time.localtime()))
amenity_occupancy = amenity_processing.amenities_compile("lsoa_amenities", run_fresh)

print("Starting zone conversion @ %s" % time.strftime("%H:%M:%S - %Y", time.localtime()))
norms_amenities = amenity_processing.zone_conversion(amenity_occupancy, run_fresh)

print("Starting walking data @ %s" % time.strftime("%H:%M:%S - %Y", time.localtime()))
walking_averages = indicator_outputs.walking_data(run_fresh)

print("Starting amenity journey times @ %s" % time.strftime("%H:%M:%S - %Y", time.localtime()))
amenity_accessibility = amenity_processing.amenity_journey_times(journey_times, norms_amenities)

print("Starting accessibility percent @ %s" % time.strftime("%H:%M:%S - %Y", time.localtime()))
percentage_accessibility = amenity_processing.accessibility_percent(amenity_accessibility)

print("Starting indicator representation @ %s" % time.strftime("%H:%M:%S - %Y", time.localtime()))
processed_amenities = indicator_outputs.indicator_representation(amenity_accessibility, walking_averages,
                                                                 percentage_accessibility, run_code, run_year)
