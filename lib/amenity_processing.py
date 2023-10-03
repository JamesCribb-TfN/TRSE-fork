import pandas as pd
import time
import os


# THIS HAS BEEN UPDATED TO LSOA ZONING
def amenities_compile(name, run_fresh):
    """create an amenities occupancy lookup for LSOA zones"""

    print("Compiling amenities:")
    print('--', time.strftime("%H:%M:%S", time.localtime()))
    if run_fresh:

        # load and format
        lsoa_amenities = pd.read_csv("inputs/uncompiled_OTP_geo_LSOA_amenities.csv")
        lsoa_amenities.rename(columns={"LSOA11CD": "lsoa_zone_id",
                                       "PrimarySchools": "PSPT15n",
                                       "SecondarySchools": "SSPT15n",
                                       "FurtherEducation": "FEPT15n",
                                       "Hospitals": "HospPT15n",
                                       "GPs": "GPPT15n"})

        print('-- Loading amenity lookups:', time.strftime("%H:%M:%S - %Y", time.localtime()))
        print('---- Employment centres')
        emp = pd.read_excel("lookups/Amenity_compiled.xlsx", "EMP")
        print('---- Primary schools')
        ps = pd.read_excel("lookups/Amenity_compiled.xlsx", "PS")
        print('---- Secondary schools')
        ss = pd.read_excel("lookups/Amenity_compiled.xlsx", "SS")
        print('---- Further education')
        fe = pd.read_excel("lookups/Amenity_compiled.xlsx", "FE")
        print('---- GPs')
        gp = pd.read_excel("lookups/Amenity_compiled.xlsx", "GPs")
        print('---- Hospitals')
        Hosp = pd.read_excel("lookups/Amenity_compiled.xlsx", "Hosp")
        print('---- Town access')
        Town = pd.read_excel("lookups/Amenity_compiled.xlsx", "Town")
        print('-- Amenities loaded. Compiling into single dataset:', time.strftime("%H:%M:%S - %Y", time.localtime()))

        # discard data
        emp = emp[["LSOA_code", "Empl_pop"]].rename(columns={"LSOA_code": "lsoa_zone_id"})
        ps = ps[["LSOA_code", "PS_pop"]].rename(columns={"LSOA_code": "lsoa_zone_id"})
        ss = ss[["LSOA_code", "SS_pop"]].rename(columns={"LSOA_code": "lsoa_zone_id"})
        fe = fe[["LSOA_code", "FE_pop"]].rename(columns={"LSOA_code": "lsoa_zone_id"})
        gp = gp[["LSOA_code", "GP_pop"]].rename(columns={"LSOA_code": "lsoa_zone_id"})
        Hosp = Hosp[["LSOA_code", "Hosp_pop"]].rename(columns={"LSOA_code": "lsoa_zone_id"})
        Town = Town[["LSOA_code", "Town_pop"]].rename(columns={"LSOA_code": "lsoa_zone_id"})

        # merge
        lsoa_amenities = pd.merge(lsoa_amenities, emp, how="left", on="lsoa_zone_id")
        lsoa_amenities = pd.merge(lsoa_amenities, ps, how="left", on="lsoa_zone_id")
        lsoa_amenities = pd.merge(lsoa_amenities, ss, how="left", on="lsoa_zone_id")
        lsoa_amenities = pd.merge(lsoa_amenities, fe, how="left", on="lsoa_zone_id")
        lsoa_amenities = pd.merge(lsoa_amenities, gp, how="left", on="lsoa_zone_id")
        lsoa_amenities = pd.merge(lsoa_amenities, Hosp, how="left", on="lsoa_zone_id")
        lsoa_amenities = pd.merge(lsoa_amenities, Town, how="left", on="lsoa_zone_id")

        # formatting
        lsoa_amenities = lsoa_amenities[["lsoa_zone_id", "5000EmpPT15n", "PSPT15n", "SSPT15n", "FEPT15n", "GPPT15n",
                                         "HospPT15n", "TownPT15n", "Empl_pop", "PS_pop", "SS_pop", "FE_pop", "GP_pop",
                                         "Hosp_pop", "Town_pop"]]

        # save (for next time...) and export
        print('-- Saving amenities')
        lsoa_amenities.to_csv("inputs/%s.csv" % name)

    else:
        # not first run - load compiled lookup
        print('-- Amenities file exists, loading now.')
        lsoa_amenities = pd.read_csv("inputs/%s.csv" % name)
    print(time.strftime("%H:%M:%S - %Y", time.localtime()))
    print("Done\n")
    return lsoa_amenities


# THIS IS NOW OUTDATED. USE THE TEST FUNCTION BELOW
def amenity_journey_times(jt_matrix, amenity_matrix):
    """two components, selects lowest jt for a zone from all other zones, and selects total number within a distance"""

    print("Performing intrazonal and interzonal journey time selection and calculation:")

    # CODE BELOW IS NEVER REFERENCED AGAIN - NEEDED??????????????
    #zone_lookup = pd.read_csv("lookups/North_LSOA_centroids.csv")
    #zone_lookup = zone_lookup[["NoRMS ID"]]

    # if amenity within zone, i.e. create diagonal from next lowest halving
    # delete diagonal elements if no intra zone
    amenity_matrix = amenity_matrix.rename(columns={"lsoa_zone_id": "LSOA Origin ID"})
    paired_matrix = pd.merge(amenity_matrix, jt_matrix, on="LSOA Origin ID")

    # No longer need jt_matrix, delete (save on RAM)
    print('-- Deleting jt_matrix after merge')
    del jt_matrix

    for amenity in ["5000EmpPT15n", "PSPT15n", "SSPT15n", "FEPT15n", "GPPT15n", "HospPT15n", "TownPT15n"]:

        print('----', amenity)

        paired_matrix["amenity_loc"] = "inter"
        paired_matrix.loc[(paired_matrix[amenity] > 0), "amenity_loc"] = "intra"
        paired_matrix.loc[(paired_matrix["LSOA Origin ID"] == paired_matrix["LSOA Destination ID"]), "pt_commute_jt"] \
            = 10000
        paired_matrix.loc[(paired_matrix["LSOA Origin ID"] == paired_matrix["LSOA Destination ID"]), "pt_other_jt"] \
            = 10000

        # select lowest journey time, select from zone lookup and create new matrix from?
        # set intra to very high, run selection, if intra and columns identical select minimum
        jt_type = "pt_other_jt"
        if amenity == "5000EmpPT15n":
            jt_type = "pt_commute_jt"

        amenity_choice_car = paired_matrix[["LSOA Origin ID", "car_jt", "LSOA Destination ID"]].reset_index()
        amenity_choice_pt = paired_matrix[["LSOA Origin ID", jt_type, "LSOA Destination ID"]].reset_index()

        amenity_choice_car = amenity_choice_car.rename(columns={"car_jt": "car_jt" + amenity})
        amenity_choice_pt = amenity_choice_pt.rename(columns={jt_type: jt_type + amenity})

        # this needs to be applied to destination, not paired
        amenity_lookup = paired_matrix[["LSOA Origin ID", amenity]].drop_duplicates(keep="first")
        amenity_lookup = amenity_lookup.rename(columns={"LSOA Origin ID": "LSOA Destination ID"})
        print('---- Performing amenity choice merges')
        amenity_choice_pt = amenity_choice_pt.merge(amenity_lookup, how="left", on="LSOA Destination ID")
        amenity_choice_car = amenity_choice_car.merge(amenity_lookup, how="left", on="LSOA Destination ID")

        amenity_choice_car.loc[(amenity_choice_car[amenity] == 0), "car_jt" + amenity] = 10000
        amenity_choice_pt.loc[(amenity_choice_pt[amenity] == 0), jt_type + amenity] = 10000

        print('---- Calculating #Amenities accessible ')
        amenity_choice_car["car_jt" + amenity + "min"] = amenity_choice_car.groupby(["LSOA Origin ID"])[
            "car_jt" + amenity].transform("min")
        amenity_choice_car["car_jt" + amenity + "_30"] = (amenity_choice_car["car_jt" + amenity] < 30).astype(int)
        amenity_choice_car["car_jt" + amenity + "_45"] = (amenity_choice_car["car_jt" + amenity] < 45).astype(int)
        amenity_choice_car["car_jt" + amenity + "_60"] = (amenity_choice_car["car_jt" + amenity] < 60).astype(int)
        amenity_choice_car["car_jt" + amenity + "_90"] = (amenity_choice_car["car_jt" + amenity] < 90).astype(int)

        amenity_choice_car = amenity_choice_car.groupby(["LSOA Origin ID", "car_jt" + amenity + "min"],
                                                        as_index=False)[["car_jt" + amenity + "_30", "car_jt" + amenity
                                                                         + "_45", "car_jt" + amenity + "_60",  "car_jt"
                                                                         + amenity + "_90"]].sum().reset_index(
                                                                                                              drop=True)

        amenity_choice_pt[jt_type + amenity + "min"] = amenity_choice_pt.groupby(["LSOA Origin ID"])[
            jt_type + amenity].transform("min")
        amenity_choice_pt[jt_type + amenity + "_30"] = (amenity_choice_pt[jt_type + amenity] < 30).astype(int)
        amenity_choice_pt[jt_type + amenity + "_45"] = (amenity_choice_pt[jt_type + amenity] < 45).astype(int)
        amenity_choice_pt[jt_type + amenity + "_60"] = (amenity_choice_pt[jt_type + amenity] < 60).astype(int)
        amenity_choice_pt[jt_type + amenity + "_90"] = (amenity_choice_pt[jt_type + amenity] < 90).astype(int)

        amenity_choice_pt = amenity_choice_pt.groupby(["LSOA Origin ID", jt_type + amenity + "min"],
                                                      as_index=False)[[jt_type + amenity + "_30", jt_type + amenity +
                                                                       "_45", jt_type + amenity + "_60", jt_type +
                                                                       amenity + "_90"]].sum().reset_index(drop=True)

        # TODO: Look to drop "pt_commute_jt", "pt_other_jt", "car_jt" here?
        #print('Dropping cols: LSOA Destination ID, pt_commute_jt, pt_other_jt, car_jt')
        #paired_matrix.drop(['LSOA Destination ID', 'pt_commute_jt', 'pt_other_jt', 'car_jt'], axis=1, inplace=True)

        try:
            # paired_matrix will not always have un-named columns, try remove each one.
            paired_matrix.drop('Unnamed: 0_x', axis=1, inplace=True)
            print('Dropped Unnamed: 0_x')
        except:
            print('Unnamed: 0_x could not be dropped')
        try:
            paired_matrix.drop('Unnamed: 0_y', axis=1, inplace=True)
            print('Dropped Unnamed: 0_y')
        except:
            print('Unnamed: 0_y could not be dropped')

        #print(len(paired_matrix), paired_matrix.columns)
        #print(len(amenity_choice_pt), amenity_choice_pt.columns)
        #print(len(amenity_choice_car), amenity_choice_car.columns)
        print('Paired matrix size -- (', len(paired_matrix), ',', len(paired_matrix.columns), ')')
        print('attempting merge 1')
        paired_matrix = pd.merge(paired_matrix, amenity_choice_pt, how="left", on="LSOA Origin ID").reset_index()
        print(paired_matrix.columns)
        paired_matrix = paired_matrix.drop("index", axis=1)
        print('attempting merge 2')
        paired_matrix = pd.merge(paired_matrix, amenity_choice_car, how="left", on="LSOA Origin ID").reset_index()
        print(paired_matrix.columns)
        paired_matrix = paired_matrix.drop("index", axis=1)
        paired_matrix.loc[(paired_matrix["amenity_loc"] == "intra"),
                          "car_jt" + amenity + "min"] = paired_matrix["car_jt" + amenity + "min"]/2
        paired_matrix.loc[(paired_matrix["amenity_loc"] == "intra"),
                          jt_type + amenity + "min"] = paired_matrix[jt_type + amenity + "min"]/2

    # select lowest journey time, select from zone lookup and create new matrix from?
    paired_matrix = paired_matrix.drop(["LSOA Destination ID", "pt_commute_jt", "pt_other_jt", "car_jt"], axis=1)
    #paired_matrix = paired_matrix.drop(["pt_commute_jt", "pt_other_jt", "car_jt"], axis=1)

    paired_matrix = paired_matrix.drop_duplicates(keep="first")  # now need to remove the destination column,
    # the actual jt columns

    # repeat for all amenities
    # use commute journey times for emp, other for all other

    # output and name them as their corresponding indicators
    print("Done \n")
    return paired_matrix


def test_amenity_journey_times(jt_matrix, amenity_matrix):
    """two components, selects lowest jt for a zone from all other zones, and selects total number within a distance"""

    print("Performing intrazonal and interzonal journey time selection and calculation:")

    # CODE BELOW IS NEVER REFERENCED AGAIN - NEEDED??????????????
    #zone_lookup = pd.read_csv("lookups/North_LSOA_centroids.csv")
    #zone_lookup = zone_lookup[["NoRMS ID"]]

    # if amenity within zone, i.e. create diagonal from next lowest halving
    # delete diagonal elements if no intra zone
    amenity_matrix = amenity_matrix.rename(columns={"lsoa_zone_id": "LSOA Origin ID"})

    for amenity in ["5000EmpPT15n", "PSPT15n", "SSPT15n", "FEPT15n", "GPPT15n", "HospPT15n", "TownPT15n"]:

        print('--', amenity)
        print('---- joining amenity matrix to jt_matrix')
        paired_matrix = pd.merge(amenity_matrix, jt_matrix, on="LSOA Origin ID")
        print('---- join complete')

        paired_matrix["amenity_loc"] = "inter"
        paired_matrix.loc[(paired_matrix[amenity] > 0), "amenity_loc"] = "intra"
        paired_matrix.loc[(paired_matrix["LSOA Origin ID"] == paired_matrix["LSOA Destination ID"]), "pt_commute_jt"] \
            = 10000
        paired_matrix.loc[(paired_matrix["LSOA Origin ID"] == paired_matrix["LSOA Destination ID"]), "pt_other_jt"] \
            = 10000

        # select lowest journey time, select from zone lookup and create new matrix from?
        # set intra to very high, run selection, if intra and columns identical select minimum
        jt_type = "pt_other_jt"
        if amenity == "5000EmpPT15n":
            jt_type = "pt_commute_jt"

        amenity_choice_car = paired_matrix[["LSOA Origin ID", "car_jt", "LSOA Destination ID"]].reset_index()
        amenity_choice_pt = paired_matrix[["LSOA Origin ID", jt_type, "LSOA Destination ID"]].reset_index()

        amenity_choice_car = amenity_choice_car.rename(columns={"car_jt": "car_jt" + amenity})
        amenity_choice_pt = amenity_choice_pt.rename(columns={jt_type: jt_type + amenity})

        # this needs to be applied to destination, not paired
        amenity_lookup = paired_matrix[["LSOA Origin ID", amenity]].drop_duplicates(keep="first")
        amenity_lookup = amenity_lookup.rename(columns={"LSOA Origin ID": "LSOA Destination ID"})
        print('---- Performing amenity choice merges')
        amenity_choice_pt = amenity_choice_pt.merge(amenity_lookup, how="left", on="LSOA Destination ID")
        amenity_choice_car = amenity_choice_car.merge(amenity_lookup, how="left", on="LSOA Destination ID")
        print('---- amenity choices joined')

        amenity_choice_car.loc[(amenity_choice_car[amenity] == 0), "car_jt" + amenity] = 10000
        amenity_choice_pt.loc[(amenity_choice_pt[amenity] == 0), jt_type + amenity] = 10000

        print('---- Calculating #Amenities accessible ')
        amenity_choice_car["car_jt" + amenity + "min"] = amenity_choice_car.groupby(["LSOA Origin ID"])[
            "car_jt" + amenity].transform("min")
        amenity_choice_car["car_jt" + amenity + "_30"] = (amenity_choice_car["car_jt" + amenity] < 30).astype(int)
        amenity_choice_car["car_jt" + amenity + "_45"] = (amenity_choice_car["car_jt" + amenity] < 45).astype(int)
        #amenity_choice_car["car_jt" + amenity + "_60"] = (amenity_choice_car["car_jt" + amenity] < 60).astype(int)
        #amenity_choice_car["car_jt" + amenity + "_90"] = (amenity_choice_car["car_jt" + amenity] < 90).astype(int)

        amenity_choice_car = amenity_choice_car.groupby(["LSOA Origin ID", "car_jt" + amenity + "min"],
                                                        as_index=False)[["car_jt" + amenity + "_30", "car_jt" + amenity
                                                                         + "_45"]].sum().reset_index(drop=True)

        amenity_choice_pt[jt_type + amenity + "min"] = amenity_choice_pt.groupby(["LSOA Origin ID"])[
            jt_type + amenity].transform("min")
        amenity_choice_pt[jt_type + amenity + "_30"] = (amenity_choice_pt[jt_type + amenity] < 30).astype(int)
        amenity_choice_pt[jt_type + amenity + "_45"] = (amenity_choice_pt[jt_type + amenity] < 45).astype(int)
        #amenity_choice_pt[jt_type + amenity + "_60"] = (amenity_choice_pt[jt_type + amenity] < 60).astype(int)
        #amenity_choice_pt[jt_type + amenity + "_90"] = (amenity_choice_pt[jt_type + amenity] < 90).astype(int)

        amenity_choice_pt = amenity_choice_pt.groupby(["LSOA Origin ID", jt_type + amenity + "min"],
                                                      as_index=False)[[jt_type + amenity + "_30", jt_type + amenity +
                                                                       "_45"]].sum().reset_index(drop=True)

        # TODO: Look to drop "pt_commute_jt", "pt_other_jt", "car_jt" here? - now reloaded every loop
        print('---- Dropping cols: LSOA Destination ID, pt_commute_jt, pt_other_jt, car_jt')
        paired_matrix.drop(["LSOA Destination ID", "pt_commute_jt", "pt_other_jt", "car_jt"], axis=1, inplace=True)

        #paired_matrix.drop(['LSOA Destination ID', 'pt_commute_jt', 'pt_other_jt', 'car_jt'], axis=1, inplace=True)

        try:
            # paired_matrix will not always have un-named columns, try remove each one.
            paired_matrix.drop('Unnamed: 0_x', axis=1, inplace=True)
            print('---- Dropped Unnamed: 0_x')
        except KeyError:
            print('---- Unnamed: 0_x could not be dropped')
        try:
            paired_matrix.drop('Unnamed: 0_y', axis=1, inplace=True)
            print('---- Dropped Unnamed: 0_y')
        except KeyError:
            print('---- Unnamed: 0_y could not be dropped')
        try:
            paired_matrix.drop('Unnamed: 0', axis=1, inplace=True)
            print('---- Dropped Unnamed: 0')
        except KeyError:
            print('---- Unnamed: 0 could not be dropped')

        #print(len(paired_matrix), paired_matrix.columns)
        #print(len(amenity_choice_pt), amenity_choice_pt.columns)
        #print(len(amenity_choice_car), amenity_choice_car.columns)
        print('---- Paired matrix size -- (', len(paired_matrix), ',', len(paired_matrix.columns), ')')
        print('---- With columns:', list(paired_matrix.columns))
        print('---- attempting merge 1')
        print(amenity_choice_pt.columns)
        #TODO: AT THIS POINT, REMOVE ANY COLUMN THAT IS NOT RELEVANT TO THE CURRENT AMENITY TYPE - MAY NEED
        # TO CREATE A LOOKUP OF RELEVANT COLUMNS PER AMENITY SELECTION.
        paired_matrix = pd.merge(paired_matrix, amenity_choice_pt, how="left", on="LSOA Origin ID").reset_index()

        paired_matrix = paired_matrix.drop("index", axis=1)
        print('---- attempting merge 2')
        paired_matrix = pd.merge(paired_matrix, amenity_choice_car, how="left", on="LSOA Origin ID").reset_index()

        paired_matrix = paired_matrix.drop("index", axis=1)
        paired_matrix.loc[(paired_matrix["amenity_loc"] == "intra"),
                          "car_jt" + amenity + "min"] = paired_matrix["car_jt" + amenity + "min"]/2
        paired_matrix.loc[(paired_matrix["amenity_loc"] == "intra"),
                          jt_type + amenity + "min"] = paired_matrix[jt_type + amenity + "min"]/2

        # Drop duplicates
        paired_matrix = paired_matrix.drop_duplicates(keep="first")

        path = os.path.join('save_ram', amenity+'_paired_matrix.csv')
        print('---- Saving:', path)
        paired_matrix.to_csv(path)
        print('---- deleting:', amenity+'_paired_matrix')
        del paired_matrix

    # select lowest journey time, select from zone lookup and create new matrix from?
    #paired_matrix = paired_matrix.drop(["LSOA Destination ID", "pt_commute_jt", "pt_other_jt", "car_jt"], axis=1)
    #paired_matrix = paired_matrix.drop(["pt_commute_jt", "pt_other_jt", "car_jt"], axis=1)

    #paired_matrix = paired_matrix.drop_duplicates(keep="first")  # now need to remove the destination column,
    # the actual jt columns

    # repeat for all amenities
    # use commute journey times for emp, other for all other

    #TODO: Section that compiles all paired_matrices saved above into a single lookup

    # Load initial amenity data to construct paired matrix through merging.
    paired_matrix = pd.read_csv(r'save_ram\TownPT15n_paired_matrix.csv')

    # Re-construct paired_matrix
    for amenity in ["5000EmpPT15n", "PSPT15n", "SSPT15n", "FEPT15n", "GPPT15n", "HospPT15n"]:  # "TownPT15n"]:

        # Specify filename & load data
        filename = amenity + '_paired_matrix.csv'
        amenity_data = pd.read_csv(os.path.join('save_ram', filename))

        # Identify desired columns (Inc. Origin ID for merge)
        desired_cols = [col for col in amenity_data.columns if ((amenity in col) and (amenity != col))]
        desired_cols.insert(0, 'LSOA Origin ID')

        # Select desired columns
        amenity_data = amenity_data[desired_cols]

        # Merge amenity data onto paired_matrix
        paired_matrix = paired_matrix.merge(how='left',
                                            right=amenity_data,
                                            on='LSOA Origin ID')

    # Save compiled matrix
    paired_matrix.to_csv(r'outputs\paired_matrix.csv')

    # output and name them as their corresponding indicators
    print("Done \n")
    return paired_matrix


# NEEDS CHECKING / NAMES UPDATING
def accessibility_percent(amenity_matrix_copy):
    """Determine whether a zone has access to an amenity within a given journey time"""
    # as not postcode based, currently a flat rate
    # employment
    amenity_matrix = amenity_matrix_copy.copy()
    amenity_matrix["5000EmpPT30pct"] = 0
    amenity_matrix.loc[(amenity_matrix["pt_commute_jt5000EmpPT15nmin"] <= 30), "5000EmpPT30pct"] = 1
    amenity_matrix["5000EmpCar30pct"] = 0
    amenity_matrix.loc[(amenity_matrix["car_jt5000EmpPT15nmin"] <= 30), "5000EmpCar30pct"] = 1
    amenity_matrix["5000EmpPT45pct"] = 0
    amenity_matrix.loc[(amenity_matrix["pt_commute_jt5000EmpPT15nmin"] <= 45), "5000EmpPT45pct"] = 1
    amenity_matrix["5000EmpCar45pct"] = 0
    amenity_matrix.loc[(amenity_matrix["car_jt5000EmpPT15nmin"] <= 45), "5000EmpCar45pct"] = 1

    # these need to be included
    amenity_matrix["100EmpPT15pct"] = 0
    #amenity_matrix.loc[(amenity_matrix["!!!!"] <= 15), "100EmpPT15pct"] = 100
    amenity_matrix["500EmpPT15pct"] = 0
    #amenity_matrix.loc[(amenity_matrix["!!!!"] <= 15), "500EmpPT15pct"] = 100

    # education
    amenity_matrix["PSPT30pct"] = 0
    amenity_matrix.loc[(amenity_matrix["pt_other_jtPSPT15nmin"] <= 30), "PSPT30pct"] = 1
    amenity_matrix["PSCar30pct"] = 0
    amenity_matrix.loc[(amenity_matrix["car_jtPSPT15nmin"] <= 30), "PSCar30pct"] = 1
    amenity_matrix["PSPT15pct"] = 0
    amenity_matrix.loc[(amenity_matrix["pt_other_jtPSPT15nmin"] <= 15), "PSPT15pct"] = 1
    amenity_matrix["SSPT30pct"] = 0
    amenity_matrix.loc[(amenity_matrix["pt_other_jtSSPT15nmin"] <= 30), "SSPT30pct"] = 1
    amenity_matrix["SSCar30pct"] = 0
    amenity_matrix.loc[(amenity_matrix["car_jtSSPT15nmin"] <= 30), "SSCar30pct"] = 1
    amenity_matrix["SSPT15pct"] = 0
    amenity_matrix.loc[(amenity_matrix["pt_other_jtSSPT15nmin"] <= 15), "SSPT15pct"] = 1
    amenity_matrix["FEPT30pct"] = 0
    amenity_matrix.loc[(amenity_matrix["pt_other_jtFEPT15nmin"] <= 30), "FEPT30pct"] = 1
    amenity_matrix["FECar30pct"] = 0
    amenity_matrix.loc[(amenity_matrix["car_jtFEPT15nmin"] <= 30), "FECar30pct"] = 1

    # health
    amenity_matrix["GPPT30pct"] = 0
    amenity_matrix.loc[(amenity_matrix["pt_other_jtGPPT15nmin"] <= 30), "GPPT30pct"] = 1
    amenity_matrix["GPCar30pct"] = 0
    amenity_matrix.loc[(amenity_matrix["car_jtGPPT15nmin"] <= 30), "GPCar30pct"] = 1
    amenity_matrix["HospPT30pct"] = 0
    amenity_matrix.loc[(amenity_matrix["pt_other_jtHospPT15nmin"] <= 30), "HospPT30pct"] = 1
    amenity_matrix["HospCar30pct"] = 0
    amenity_matrix.loc[(amenity_matrix["car_jtHospPT15nmin"] <= 30), "HospCar30pct"] = 1
    amenity_matrix["HospPT60pct"] = 0
    amenity_matrix.loc[(amenity_matrix["pt_other_jtHospPT15nmin"] <= 60), "HospPT60pct"] = 1
    amenity_matrix["HospCar60pct"] = 0
    amenity_matrix.loc[(amenity_matrix["car_jtHospPT15nmin"] <= 60), "HospCar60pct"] = 1

    # town
    amenity_matrix["TownPT30pct"] = 0
    amenity_matrix.loc[(amenity_matrix["pt_other_jtTownPT15nmin"] <= 30), "TownPT30pct"] = 1
    amenity_matrix["TownCar30pct"] = 0
    amenity_matrix.loc[(amenity_matrix["car_jtTownPT15nmin"] <= 30), "TownCar30pct"] = 1
    amenity_matrix["TownPT15pct"] = 0
    amenity_matrix.loc[(amenity_matrix["pt_other_jtTownPT15nmin"] <= 15), "TownPT15pct"] = 1

    amenity_matrix = amenity_matrix[["LSOA Origin ID", "5000EmpPT30pct", "5000EmpCar30pct", "5000EmpPT45pct",
                                     "5000EmpCar45pct", "100EmpPT15pct", "500EmpPT15pct", "PSPT30pct", "PSCar30pct",
                                     "PSPT15pct", "SSPT30pct", "SSCar30pct", "SSPT15pct", "FEPT30pct", "FECar30pct",
                                     "GPPT30pct", "GPCar30pct", "HospPT30pct", "HospCar30pct", "HospPT60pct",
                                     "HospCar60pct", "TownPT30pct", "TownCar30pct", "TownPT15pct"]]

    return amenity_matrix
