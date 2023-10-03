import pandas as pd
import time
import os


# THIS HAS BEEN UPDATED TO LSOA ZONING
def centroids_col_max(name, run_fresh):
    """Create a column matrix of zone OD pairs"""

    print(time.strftime("%H:%M:%S - %Y", time.localtime()))
    print("Creating OD column matrix:")
    if run_fresh:
        #zone_id	zone_name	zone_system	latitude	longitude
        zone_origin = pd.read_csv("lookups/North_LSOA_centroids.csv")
        print('-- Loaded:', len(zone_origin), 'Origin centroids')
        # Remove un-needed columns from LSOA centroids
        del zone_origin['zone_name']
        del zone_origin['zone_system']

        zone_origin["key"] = 1
        zone_destination = zone_origin.rename(
            columns={"zone_id": "LSOA Destination ID", "longitude": "Destination Longitude",
                     "latitude": "Destination Latitude"})
        zone_origin = zone_origin.rename(
            columns={"zone_id": "LSOA Origin ID", "longitude": "Origin Longitude", "latitude": "Origin Latitude"})

        col_matrix = pd.merge(zone_origin, zone_destination, on="key")
        print('-- Created:', len(col_matrix), 'potential trips.')

        del col_matrix["key"]
        print('-- Saving now:', time.strftime("%H:%M:%S - %Y", time.localtime()))
        col_matrix.to_csv("lookups/%s.csv" % name)

    else:
        print("-- File exists, loading now.")
        col_matrix = pd.read_csv("lookups/%s.csv" % name)
    print(time.strftime("%H:%M:%S - %Y", time.localtime()), "\nDone \n")

    return col_matrix


# THIS HAS BEEN UPDATED TO LSOA ZONING
def journey_time_modes(col_matrix, bus_matrix, rail_matrix, car_matrix, run_fresh):
    """Selecting between rail and bus JTs based on utility coefficient factors"""

    if run_fresh:
        print("Combining mode journey times into a single matrix, selecting optimal mode per trip")
        print('--', time.strftime("%H:%M:%S", time.localtime()))
        cost_coefficients = pd.read_excel("lookups/utility_coefficients.xlsx", index_col=0)

        col_matrix = col_matrix[["LSOA Origin ID", "LSOA Destination ID"]]
        # rail_matrix now also contains PT(bus) to rail split, as percentage of additive JT
        rail_matrix = rail_matrix.rename(columns={"o": "LSOA Origin ID", "d": "LSOA Destination ID", "jt": "rail_jt",
                                                  "bus_pct": "bus_percent_of_jt", "rail_pct": "rail_percent_of_jt"})
        car_matrix = car_matrix.rename(columns={"o": "LSOA Origin ID", "d": "LSOA Destination ID",
                                                "pop_weighted_jt": "car_jt"})
        bus_matrix = bus_matrix.rename(columns={"o": "LSOA Origin ID", "d": "LSOA Destination ID", "jt": "bus_jt"})
        # Assign bus_jt matrix as the non_rail_PT_jt matrix
        non_rail_pt_matrix = bus_matrix

        # merge all transport modes into single matrix
        print('-- Merging all modes into a single matrix')
        col_matrix = pd.merge(col_matrix, car_matrix, how="left", on=["LSOA Origin ID", "LSOA Destination ID"])
        col_matrix = pd.merge(col_matrix, rail_matrix, how="left", on=["LSOA Origin ID", "LSOA Destination ID"])
        col_matrix = pd.merge(col_matrix, non_rail_pt_matrix, how="left", on=["LSOA Origin ID", "LSOA Destination ID"])
        col_matrix = col_matrix.fillna(value=300)

        # replace bus entries with a flat 10000 value to select only rail
        # calculate effective trip cost for selection of optimal mode
        print('-- Calculating effective trip costs')
        col_matrix["rail_bus_commute_value"] = (cost_coefficients.loc["rail"]["commute"] * col_matrix["rail_jt"] *
                                                col_matrix['rail_percent_of_jt']) + \
                                               (cost_coefficients.loc["bus"]["commute"] * col_matrix['rail_jt'] *
                                                col_matrix['bus_percent_of_jt'])

        col_matrix["car_commute_value"] = cost_coefficients.loc["car"]["commute"] * col_matrix["car_jt"]

        col_matrix["bus_commute_value"] = cost_coefficients.loc["bus"]["commute"] * col_matrix["bus_jt"]

        col_matrix["rail_bus_other_value"] = (cost_coefficients.loc["rail"]["other"] * col_matrix["rail_jt"] *
                                              col_matrix['rail_percent_of_jt']) + \
                                             (cost_coefficients.loc["bus"]["other"] * col_matrix['rail_jt'] *
                                              col_matrix['bus_percent_of_jt'])

        col_matrix["bus_other_value"] = cost_coefficients.loc["bus"]["other"] * col_matrix["bus_jt"]
        col_matrix["car_other_value"] = cost_coefficients.loc["car"]["other"] * col_matrix["car_jt"]

        # select optimal transport mode based on calculated commute values (above)
        print('-- Selecting optimal modes from trip costs', col_matrix.columns)
        col_matrix["pt_commute_jt"] = col_matrix["bus_jt"]
        col_matrix.loc[(col_matrix["rail_bus_commute_value"] < col_matrix["bus_commute_value"]), "pt_commute_jt"] \
            = col_matrix["rail_jt"]
        col_matrix.loc[(col_matrix["rail_bus_commute_value"] < col_matrix["bus_commute_value"]), "rail choice"] \
            = "RAIL"

        col_matrix["pt_other_jt"] = col_matrix["bus_jt"]
        col_matrix.loc[(col_matrix["rail_bus_other_value"] < col_matrix["bus_other_value"]), "pt_other_jt"] \
            = col_matrix["rail_jt"]

        jt_matrix = col_matrix[["LSOA Origin ID", "LSOA Destination ID", "pt_commute_jt", "pt_other_jt", "car_jt"]]

        print('-- Saving journey time matrix')
        jt_matrix.to_csv("jt_matrix.csv")
    else:
        print('-- jt_matrix already exists, loading now.')
        jt_matrix = pd.read_csv('jt_matrix.csv')
    print(time.strftime("%H:%M:%S", time.localtime()))
    print("Done \n")
    return jt_matrix


# THIS HAS BEEN CREATED TO HANDLE CONVERSION FROM NoRMS NoHAM JTs into LSOA NoHAM JTs
def noham_norms_jt_to_lsoa_jt(pop_centres, norms2018_to_lsoa, car_jt_matrix, run_fresh, north_only):
    """Function to convert NoHAM car JT matrix from NoRMS to LSOA zoning"""

    if run_fresh:
        print('Converting car_jt matrix from NoRMS to LSOA')
        print('--', time.strftime("%H:%M:%S - %Y", time.localtime()))

        if north_only:
            print('-- Creating lsoa_car_jt_matrix from NoRMS jt matrix using only Northern LSOAs')
            print('-- initial lookup length:', len(norms2018_to_lsoa))
            # Load northern LSOA IDs
            north_only_lsoa = pd.read_csv(r'lookups\North_LSOA_centroids.csv')
            north_only_lsoa = north_only_lsoa[['zone_id']]  # Select only lsoa id column for northern LSOAs

            # Leave only Northern lsoas within the norms2018_to_lsoa lookup
            norms2018_to_lsoa = norms2018_to_lsoa.loc[norms2018_to_lsoa['lsoa_zone_id'].isin(
                north_only_lsoa['zone_id'])]
            print('-- Final lookup length:', len(norms2018_to_lsoa))
            del north_only_lsoa  # Delete to save RAM

        pop_centres = pop_centres[['LSOA Origin ID', 'LSOA Destination ID']]

        # Join on NoRMS -- > LSOA zone conversion & weighting info for Origins
        pop_centres_with_norms2018 = pd.merge(pop_centres,
                                              norms2018_to_lsoa,
                                              how='left',
                                              left_on='LSOA Origin ID',
                                              right_on='lsoa_zone_id')
        print('-- Number of remaining trips', len(pop_centres_with_norms2018))

        # Rename and format columns
        pop_centres_with_norms2018.rename(columns={"norms2018_zone_id": "NoRMS Origin ID",
                                                   "norms2018_to_lsoa": "O_norms_to_lsoa",
                                                   "lsoa_to_norms2018": "O_lsoa_to_norms"},
                                          inplace=True)

        pop_centres_with_norms2018.drop(labels="lsoa_zone_id",
                                        inplace=True, axis=1)

        # Join NoRMS --> LSOA zone conversion & weighting info for Destinations
        print('-- Joining NoRMS->LSOA zone conversion & weighting info')
        pop_centres_with_norms2018 = pd.merge(pop_centres_with_norms2018,
                                              norms2018_to_lsoa,
                                              how="left",
                                              left_on="LSOA Destination ID",
                                              right_on="lsoa_zone_id")
        # Rename and format columns
        pop_centres_with_norms2018.rename(columns={"norms2018_zone_id": "NoRMS Destination ID",
                                                   "norms2018_to_lsoa": "D_norms_to_lsoa",
                                                   "lsoa_to_norms2018": "D_lsoa_to_norms"},
                                          inplace=True)

        # norms to lsoa weights are not needed. Drop to save RAM
        pop_centres_with_norms2018.drop(labels=['D_norms_to_lsoa', 'O_norms_to_lsoa'],
                                        inplace=True,
                                        axis=1)

        pop_centres_with_norms2018.drop(labels="lsoa_zone_id",
                                        inplace=True, axis=1)

        # Add LSOA/NoRMS level OD_pair code

        #print(len(pop_centres_with_norms2018))
        print('-- Creating LSOA od code')
        pop_centres_with_norms2018['LSOA Origin ID'] = pop_centres_with_norms2018['LSOA Origin ID']+'_' + \
                                                       pop_centres_with_norms2018['LSOA Destination ID']

        pop_centres_with_norms2018.rename(columns={'LSOA Origin ID': 'lsoa_OD_code'},
                                          inplace=True)
        print('-- Creating NoRMS od code')
        pop_centres_with_norms2018['NoRMS Origin ID'] = pop_centres_with_norms2018['NoRMS Origin ID'].astype(str)+'_' +\
                                                        pop_centres_with_norms2018['NoRMS Destination ID'].astype(str)

        pop_centres_with_norms2018.rename(columns={'NoRMS Origin ID': 'norms_OD_code'},
                                          inplace=True)
        #print(pop_centres_with_norms2018.columns)

        # Create OD pair codes for NoRMS zoned JTs, then join JTs onto pop_centres using norms_OD_codes.
        norms_car_jt = car_jt_matrix
        norms_car_jt['norms_od_code'] = norms_car_jt['o'].astype(str) + '_' + norms_car_jt['d'].astype(str)
        norms_car_jt.drop(labels=['o', 'd'],
                          inplace=True,
                          axis=1)

        print('-- Merging NoHAM jt onto NoRMS-LSOA data')
        # Merge NoHAM jt data to LSOA-NoRMS with weighting df
        pop_centres_with_norms2018 = pd.merge(pop_centres_with_norms2018,
                                              norms_car_jt,
                                              how='outer',
                                              left_on='norms_OD_code',
                                              right_on='norms_od_code')
        # Rename and format columns
        pop_centres_with_norms2018.rename(columns={"jt": "norms_jt"},
                                          inplace=True),

        pop_centres_with_norms2018.drop(labels=['norms_od_code'],
                                        inplace=True,
                                        axis=1)

        # For all trips, work out the weighted journey times
        print('-- Calculating population weighted journey times')
        pop_centres_with_norms2018['pop_weighted_jt'] = pop_centres_with_norms2018['O_lsoa_to_norms'] * \
                                                        pop_centres_with_norms2018['D_lsoa_to_norms'] * \
                                                        pop_centres_with_norms2018['norms_jt']

        # Group the trips by LSOA OD code - if LSOA straddles multiple zones, the
        #     combination of pop_weighted_jts are averaged to obtain final
        #     LSOA -> LSOA zone journey times.
        print('-- Grouping by lsoa od codes')
        grouped_pop_centres = pop_centres_with_norms2018.groupby('lsoa_OD_code').agg({"pop_weighted_jt": 'mean'})

        # Reformat and save
        print('-- Reformatting data')
        grouped_pop_centres['OD_code'] = grouped_pop_centres.index  # OD_code is index from .groupby above.
        grouped_pop_centres[['o', 'd']] = grouped_pop_centres['OD_code'].str.split('_', expand=True)
        grouped_pop_centres = grouped_pop_centres[['o', 'd', 'pop_weighted_jt']]

        # Save & export data
        save_name = 'lsoa_car_jt_matrix.csv'
        print('-- Saving %s' % save_name)

        if north_only:
            save_name = 'NORTH_ONLY_' + save_name
        path = os.path.join('inputs', save_name)

        grouped_pop_centres.to_csv(path, index=False)

        print(time.strftime("%H:%M:%S", time.localtime()))
        print('Done \n')
        return grouped_pop_centres
    else:
        print('-- File exists, loading LSOA zoned car_jt matrix.')
        file_name = 'lsoa_car_jt_matrix.csv'
        if north_only:
            file_name = 'NORTH_ONLY_'+file_name
        path = os.path.join('inputs', file_name)
        lsoa_car_jt = pd.read_csv(path)
        print('Done \n')
        return lsoa_car_jt
