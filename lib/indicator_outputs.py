# add indicators from list
import pandas as pd


# OBSOLETE - Now load walking data from workbook with function below.
def walking_data(run_fresh):
    """Compile static walking data for all schemes"""

    print("Producing walking data:")

    if run_fresh:
        # LSOA zone ids
        lsoa_amenities = pd.read_csv("inputs/lsoa_zones.csv")

        lsoa_to_norms = pd.read_csv("lookups/norms2018_to_lsoa_correspondence.csv").rename(
            columns={"norms2018_zone_id": "NoRMS Origin ID"})
        # Contains info on pop & pct of population to reach amenity
        emp = pd.read_excel("lookups/Amenity_compiled.xlsx", "EMP")
        fe = pd.read_excel("lookups/Amenity_compiled.xlsx", "FE")
        gp = pd.read_excel("lookups/Amenity_compiled.xlsx", "GPs")
        Hosp = pd.read_excel("lookups/Amenity_compiled.xlsx", "Hosp")

        emp = emp[["LSOA_code", "Empl_pop", "5000EmpWalk15pct"]].rename(columns={"LSOA_code": "lsoa_zone_id"})
        fe = fe[["LSOA_code", "FE_pop", "FEWalk15pct"]].rename(columns={"LSOA_code": "lsoa_zone_id"})
        gp = gp[["LSOA_code", "GP_pop", "GPWalk15pct"]].rename(columns={"LSOA_code": "lsoa_zone_id"})
        Hosp = Hosp[["LSOA_code", "Hosp_pop", "HospWalk15pct"]].rename(columns={"LSOA_code": "lsoa_zone_id"})

        lsoa_amenities = pd.merge(lsoa_amenities, emp, how="left", on="lsoa_zone_id")
        lsoa_amenities = pd.merge(lsoa_amenities, fe, how="left", on="lsoa_zone_id")
        lsoa_amenities = pd.merge(lsoa_amenities, gp, how="left", on="lsoa_zone_id")
        lsoa_amenities = pd.merge(lsoa_amenities, Hosp, how="left", on="lsoa_zone_id")

        # merge with lsoa_to_norms
        walking_averages = pd.merge(lsoa_to_norms, lsoa_amenities, how="left", on="lsoa_zone_id")
        walking_averages = walking_averages.drop_duplicates()
        weighted_pop = walking_averages.copy()

        weighted_pop["Empl_pop_adjusted"] = weighted_pop["Empl_pop"] * weighted_pop["lsoa_to_norms2018"]
        weighted_pop["FE_pop_adjusted"] = weighted_pop["FE_pop"] * weighted_pop["lsoa_to_norms2018"]
        weighted_pop["GP_pop_adjusted"] = weighted_pop["GP_pop"] * weighted_pop["lsoa_to_norms2018"]
        weighted_pop["Hosp_pop_adjusted"] = weighted_pop["Hosp_pop"] * weighted_pop["lsoa_to_norms2018"]

        weighted_pop = weighted_pop.groupby("NoRMS Origin ID", as_index=False).sum()
        weighted_pop = weighted_pop[["NoRMS Origin ID", "norms2018_to_lsoa", "Empl_pop_adjusted", "FE_pop_adjusted",
                                          "GP_pop_adjusted", "Hosp_pop_adjusted"]]
        weighted_pop = weighted_pop.rename(columns={"norms2018_to_lsoa": "scale_factor"})
        weighted_pop["scale_factor"] = weighted_pop["scale_factor"] * 100

        walking_averages = pd.merge(walking_averages, weighted_pop, how="left", on="NoRMS Origin ID")

        walking_averages["5000EmpWalk15pct"] = walking_averages["5000EmpWalk15pct"] * walking_averages["Empl_pop"]\
                                           / (walking_averages["Empl_pop_adjusted"] * weighted_pop["scale_factor"])
        walking_averages["FEWalk15pct"] = walking_averages["FEWalk15pct"] * walking_averages["FE_pop"]\
                                      / (walking_averages["FE_pop_adjusted"] * weighted_pop["scale_factor"])
        walking_averages["GPWalk15pct"] = walking_averages["GPWalk15pct"] * walking_averages["GP_pop"]\
                                      / (walking_averages["GP_pop_adjusted"] * weighted_pop["scale_factor"])
        walking_averages["HospWalk15pct"] = walking_averages["HospWalk15pct"] * walking_averages["Hosp_pop"]\
                                        / (walking_averages["Hosp_pop_adjusted"] * weighted_pop["scale_factor"])

        walking_averages = walking_averages[["NoRMS Origin ID", "5000EmpWalk15pct", "FEWalk15pct", "GPWalk15pct",
                                             "HospWalk15pct"]]
        walking_averages = walking_averages.groupby("NoRMS Origin ID", as_index=False).sum()

        walking_averages.to_csv("inputs/amenity_walking_data.csv")
    else:
        walking_averages = pd.read_csv("inputs/amenity_walking_data.csv")
    print("Done \n")
    return walking_averages


# THIS FUNCTION REPLACES walking_data ABOVE
# noinspection PyTypeChecker
def lift_walking_data(run_fresh):
    """Lift LSOA walking data from Accessibility working dataset on Y: """

    print('Producing walking data.')

    if run_fresh:  # Data has not been lifted. Get now.

        # Only walking data available from working book is:
        #     LSOA_code:     col A
        #     EmpWalk15pct:  col K
        #     FEWalk15pct:   col AP
        #     GPWalk15pct:   col AX
        #     HospWalk15pct: col BF
        #     -- Only parse these cols to save space & time.
        working_book_path = r'Y:\PBA\Accessibility analysis\workbooks\Accessibiltiy working dataset original.xlsx'
        working_book = pd.read_excel(io=working_book_path,
                                     sheet_name='Data',
                                     usecols='A,K,AP,AX,BF')

        working_book.rename(columns={'LSOA_code': 'LSOA Origin ID'},
                            inplace=True)

        # Working book is already in required format. Save as compiled extract for loading if run_fresh=False.
        working_book.to_csv(r'inputs\lsoa_amenity_walking_data.csv', index=False)
        print('\nDone')
        return working_book
    else:
        # run_fresh=False, load existing dataset.
        lsoa_amenity_walking_data = pd.read_csv(r'inputs\lsoa_amenity_walking_data.csv')
        print('\nDone')
        return lsoa_amenity_walking_data


# THIS HAS BEEN UPDATED TO WORK WITH LSOA ZONING (BELOW)
# name conversions
def indicator_representation(processed_matrix, walking_averages, percentage_matrix, run_code, run_year):
    """Compile and reformat all indicators necessary"""

    print("Producing final indicators:")
    # employment
    #processed_matrix.to_csv("test_commutes.csv")

    '''
    Everything within the rename columns below has to be taken over for the next step of analysis. 
    In other words - MAKE SURE ALL COLUMNS LISTED HERE, MAKE IT TO THIS STAGE!!!!
    '''
    # READ THE NOTE WRITTEN ABOVE HERE!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

    processed_matrix = processed_matrix.rename(columns={"pt_commute_jt5000EmpPT15nmin": "5000EmpPTt",
                                                        "pt_commute_jt5000EmpPT15n_45": "5000EmpPT45n",
                                                        "car_jt5000EmpPT15nmin": "5000EmpCart",
                                                        "car_jt5000EmpPT15n_45": "5000EmpCar45n"})
                                                        ##"pt_commute_jt5000EmpPT15n_60": "5000EmpPT60n",
                                                        ##"car_jt5000EmpPT15n_60": "5000EmpCar60n"})
    #changed 30 to 45

    # education
    processed_matrix = processed_matrix.rename(columns={"pt_other_jtPSPT15nmin": "PSPTt",
                                                        "pt_other_jtPSPT15n_45": "PSPT45n",
                                                        "car_jtPSPT15nmin": "PSCart",
                                                        "car_jtPSPT15n_45": "PSCar45n",
                                                        "pt_other_jtSSPT15nmin": "SSPTt",
                                                        "pt_other_jtSSPT15n_45": "SSPT45n",
                                                        "car_jtSSPT15nmin": "SSCart",
                                                        "car_jtSSPT15n_45": "SSCar45n",
                                                        "pt_other_jtFEPT15nmin": "FEPTt",
                                                        "pt_other_jtFEPT15n_45": "FEPT45n",
                                                        "car_jtFEPT15nmin": "FECart",
                                                        "car_jtFEPT15n_45": "FECar45n"})
                                                        #"pt_other_jtPSPT15n_60": "PSPT60n",
                                                        #"car_jtPSPT15n_60": "PSCar60n",
                                                        #"pt_other_jtSSPT15n_60": "SSPT60n",
                                                        #"car_jtSSPT15n_60": "SSCar60n",
                                                        #"pt_other_jtFEPT15n_60": "FEPT60n",
                                                        #"car_jtFEPT15n_60": "FECar60n"})

    # health
    processed_matrix = processed_matrix.rename(columns={"pt_other_jtGPPT15nmin": "GPPTt",
                                                        "car_jtGPPT15nmin": "GPCart",
                                                        "pt_other_jtHospPT15nmin": "HospPTt",
                                                        "car_jtHospPT15nmin": "HospCart"})

    # town
    processed_matrix = processed_matrix.rename(columns={"car_jtTownPT15nmin": "TownCart",
                                                        "pt_other_jtTownPT15nmin": "TownPTt"})

    # adding walking and percentage data
    processed_matrix = pd.merge(processed_matrix, walking_averages, how="left", on="LSOA Origin ID")
    processed_matrix = pd.merge(processed_matrix, percentage_matrix, how="left", on="LSOA Origin ID")

    # refining and outputting
    '''
    Probably need to look at utilising some LSOA lookups here rather than NoRMS, i.e.
    norms_ca --> lsoa_ca
    norms_internal --> lsoa_internal
    '''

    lsoa_ca = pd.read_csv("lookups/CA zones.csv")
    lsoa_internal = pd.read_csv("lookups/ca_sectors_to_lsoa_correspondence.csv")
    lsoa_internal.rename(columns={'ca_sectors_zone_id': 'ca_sector'}, inplace=True)
    lsoa_ca = lsoa_ca.rename(columns={"ca_sector_zone_id": "ca_sector", "gor": "Region"})
    lsoa_internal = pd.merge(lsoa_internal, lsoa_ca, how="left", on="ca_sector")
    lsoa_internal = lsoa_internal.rename(columns={"lsoa_zone_id": "LSOA Origin ID"})

    processed_matrix = processed_matrix.merge(lsoa_internal, how="left", on="LSOA Origin ID")
    processed_matrix = processed_matrix[processed_matrix["north"] == 1]

    processed_matrix["100EmpPT15pct"] = "unused"
    processed_matrix["500EmpPT15pct"] = "unused"

    processed_matrix = processed_matrix[["LSOA Origin ID",  "Region", "Empl_pop",  "5000EmpPT30pct",
                                         "5000EmpCar30pct", "5000EmpPT45pct", "5000EmpCar45pct", "100EmpPT15pct",
                                         "500EmpPT15pct", "5000EmpWalk15pct", "5000EmpPTt", "5000EmpCart",
                                         "5000EmpPT45n", "5000EmpCar45n", "PS_pop", "PSPT30pct", "PSCar30pct",
                                         "PSPT15pct", "PSPTt", "PSCart", "PSPT45n", "PSCar45n", "SS_pop", "SSPT30pct",
                                         "SSCar30pct", "SSPT15pct", "SSPTt",  "SSCart", "SSPT45n", "SSCar45n", "FE_pop",
                                         "FEPT30pct", "FECar30pct", "FEWalk15pct", "FEPTt", "FECart", "FEPT45n",
                                         "FECar45n", "GP_pop", "GPPT30pct", "GPCar30pct", "GPWalk15pct", "GPPTt",
                                         "GPCart", "Hosp_pop", "HospPT30pct", "HospCar30pct", "HospPT60pct",
                                         "HospCar60pct", "HospWalk15pct", "HospPTt", "HospCart", "Town_pop",
                                         "TownPT30pct", "TownCar30pct", "TownPT15pct", "TownPTt", "TownCart"]]
                                         #"5000EmpPT60n", "5000EmpCar60n", "PSPT60n", "PSCar60n", "SSPT60n", "SSCar60n",
                                         #"FEPT60n", "FECar60n"]]

    # insert zone aggregation here
    lsoa_to_lad(processed_matrix, run_code, run_year)
    lsoa_to_cad(processed_matrix, run_code, run_year)

    # select an upper limit on amenities to avoid saturation
    a_cap = 200

    processed_matrix.loc[(processed_matrix["PSPT45n"] > a_cap), "PSPT45n"] = a_cap
    processed_matrix.loc[(processed_matrix["SSPT45n"] > a_cap), "SSPT45n"] = a_cap
    processed_matrix.loc[(processed_matrix["FEPT45n"] > a_cap), "FEPT45n"] = a_cap
    processed_matrix.loc[(processed_matrix["PSCar45n"] > a_cap), "PSCar45n"] = a_cap
    processed_matrix.loc[(processed_matrix["SSCar45n"] > a_cap), "SSCar45n"] = a_cap
    processed_matrix.loc[(processed_matrix["FECar45n"] > a_cap), "FECar45n"] = a_cap
    processed_matrix.loc[(processed_matrix["5000EmpPT45n"] > a_cap), "5000EmpPT45n"] = a_cap
    processed_matrix.loc[(processed_matrix["5000EmpCar45n"] > a_cap), "5000EmpCar45n"] = a_cap

    output_name = "amenity_indicators_" + run_code + "_" + run_year + ".csv"
    print('Saving: %s' % output_name)
    processed_matrix.to_csv("outputs/%s" % output_name)

    print("Done \n")


# THIS HAS BEEN UPDATED FROM NORMS_TO_LAD TO LSOA_TO_LAD
def lsoa_to_lad(norms_matrix, run_code, run_year):
    """Compile and reformat all indicators necessary for local authorities"""
    '''This function needs re-writing to be in terms of LSOA --> LAD'''

    lsoa_lads = pd.read_csv("lookups/lads20_to_lsoa_correspondence.csv").rename(
        columns={"lsoa_zone_id": "LSOA Origin ID", "lads20_zone_id": "LA"})
    authority_matrix = norms_matrix.merge(lsoa_lads, how="left", on="LSOA Origin ID")

    #print(authority_matrix.columns)

    # non percentage conversions
    for indicator in ["Empl_pop", "5000EmpPT45n", "5000EmpCar45n", "PS_pop", "PSPT45n", "PSCar45n", "SS_pop",
                                         "SSPT45n", "SSCar45n", "FE_pop", "FEPT45n", "FECar45n", "GP_pop",
                                         "Hosp_pop", "Town_pop", "TownPTt", "TownCart"]:#, "5000EmpPT60n",
                                         #"5000EmpCar60n", "PSPT60n", "PSCar60n", "SSPT60n", "SSCar60n", "FEPT60n",
                                         #"FECar60n"]:
        authority_matrix[indicator] = authority_matrix[indicator] * authority_matrix["lsoa_to_lads20"]

    # for journey times

    weighted_pop = authority_matrix.copy()

    for adjustment in ["Empl_pop", "PS_pop", "SS_pop", "FE_pop", "GP_pop", "Hosp_pop", "Town_pop"]:
        weighted_pop[adjustment + "_adjusted"] = weighted_pop[adjustment] * weighted_pop["lsoa_to_lads20"]

    weighted_pop = weighted_pop.groupby("LA", as_index=False).sum()
    weighted_pop = weighted_pop[["LA", "Empl_pop_adjusted", "PS_pop_adjusted", "SS_pop_adjusted", "FE_pop_adjusted",
                                 "GP_pop_adjusted", "Hosp_pop_adjusted", "Town_pop_adjusted"]]
    authority_matrix = pd.merge(authority_matrix, weighted_pop, how="left", on="LA")

    #emp
    for indicator in ["5000EmpPTt", "5000EmpCart", "5000EmpPT30pct", "5000EmpCar30pct", "5000EmpPT45pct",
                      "5000EmpCar45pct", "5000EmpWalk15pct"]:
        authority_matrix[indicator] = authority_matrix[indicator] * authority_matrix["Empl_pop"] \
                                               / (authority_matrix["Empl_pop_adjusted"])
    #ps
    for indicator in ["PSPTt", "PSCart", "PSPT30pct", "PSCar30pct", "PSPT15pct"]:
        authority_matrix[indicator] = authority_matrix[indicator] * authority_matrix["PS_pop"] \
                                               / (authority_matrix["PS_pop_adjusted"])
    #ss
    for indicator in ["SSPTt", "SSCart", "SSPT30pct", "SSCar30pct", "SSPT15pct"]:
        authority_matrix[indicator] = authority_matrix[indicator] * authority_matrix["SS_pop"] \
                                               / (authority_matrix["SS_pop_adjusted"])
    #fe
    for indicator in ["FEPTt", "FECart", "FEPT30pct", "FECar30pct", "FEWalk15pct"]:
        authority_matrix[indicator] = authority_matrix[indicator] * authority_matrix["FE_pop"] \
                                               / (authority_matrix["FE_pop_adjusted"])
    #gp
    for indicator in ["GPPTt", "GPCart", "GPPT30pct", "GPCar30pct", "GPWalk15pct"]:
        authority_matrix[indicator] = authority_matrix[indicator] * authority_matrix["GP_pop"] \
                                               / (authority_matrix["GP_pop_adjusted"])
    #Hosp
    for indicator in ["HospPTt", "HospCart", "HospPT30pct", "HospCar30pct", "HospPT60pct", "HospCar60pct",
                      "HospWalk15pct"]:
        authority_matrix[indicator] = authority_matrix[indicator] * authority_matrix["Hosp_pop"] \
                                               / (authority_matrix["Hosp_pop_adjusted"])
    #town
    for indicator in ["TownPTt", "TownCart", "TownPT30pct", "TownCar30pct", "TownPT15pct"]:
        authority_matrix[indicator] = authority_matrix[indicator] * authority_matrix["Town_pop"] \
                                               / (authority_matrix["Town_pop_adjusted"])

    # grouping
    authority_matrix.to_csv("LA check.csv")
    authority_matrix = authority_matrix.groupby(["LA", "Region"], as_index=False).sum()
    #finalising and applying cap

    authority_matrix["100EmpPT15pct"] = "unused"
    authority_matrix["500EmpPT15pct"] = "unused"

    authority_matrix = authority_matrix[["LA", "Region", "Empl_pop",  "5000EmpPT30pct",
                                         "5000EmpCar30pct", "5000EmpPT45pct", "5000EmpCar45pct", "100EmpPT15pct",
                                         "500EmpPT15pct", "5000EmpWalk15pct", "5000EmpPTt", "5000EmpCart",
                                         "5000EmpPT45n", "5000EmpCar45n", "PS_pop", "PSPT30pct", "PSCar30pct",
                                         "PSPT15pct", "PSPTt", "PSCart", "PSPT45n", "PSCar45n", "SS_pop", "SSPT30pct",
                                         "SSCar30pct", "SSPT15pct", "SSPTt",  "SSCart", "SSPT45n", "SSCar45n", "FE_pop",
                                         "FEPT30pct", "FECar30pct", "FEWalk15pct", "FEPTt", "FECart", "FEPT45n",
                                         "FECar45n", "GP_pop", "GPPT30pct", "GPCar30pct", "GPWalk15pct", "GPPTt",
                                         "GPCart", "Hosp_pop", "HospPT30pct", "HospCar30pct", "HospPT60pct",
                                         "HospCar60pct", "HospWalk15pct", "HospPTt", "HospCart", "Town_pop",
                                         "TownPT30pct", "TownCar30pct", "TownPT15pct", "TownPTt", "TownCart"]] #,
                                         #"5000EmpPT60n", "5000EmpCar60n", "PSPT60n", "PSCar60n", "SSPT60n", "SSCar60n",
                                         #"FEPT60n", "FECar60n"]]

    # select an upper limit on amenities to avoid saturation
    a_cap = 500

    for indicator in ["PSPT45n", "SSPT45n", "FEPT45n", "PSCar45n", "SSCar45n", "FECar45n", "5000EmpPT45n",
                      "5000EmpCar45n"]:
        authority_matrix.loc[(authority_matrix[indicator] > a_cap), indicator] = a_cap

    for indicator in ["5000EmpPT30pct", "5000EmpCar30pct", "5000EmpPT45pct", "5000EmpCar45pct", "5000EmpWalk15pct",
                      "PSPT30pct", "PSCar30pct", "PSPT15pct", "SSPT30pct", "SSCar30pct",
                      "SSPT15pct", "FEPT30pct", "FECar30pct", "FEWalk15pct", "GPPT30pct",
                      "GPCar30pct", "GPWalk15pct", "HospPT30pct", "HospCar30pct", "HospPT60pct", "HospCar60pct",
                      "HospWalk15pct", "TownPT30pct", "TownCar30pct", "TownPT15pct"]:
        authority_matrix.loc[(authority_matrix[indicator] > 1), indicator] = 1

    output_name = "LA_amenity_indicators_" + run_code + "_" + run_year + ".csv"
    print('Saving: %s' % output_name)
    authority_matrix.to_csv("outputs/%s" % output_name)

    return None


# THIS HAS BEEN UPDATED FROM NORMS_TO_CA TO LSOA_TO_CA
def lsoa_to_cad(norms_matrix, run_code, run_year):
    """Compile and reformat all indicators necessary for combined authorities"""

    lsoa_ca = pd.read_csv("lookups/ca_sectors_to_lsoa_correspondence.csv").rename(
        columns={"lsoa_zone_id": "LSOA Origin ID", "ca_sectors_zone_id": "CA"})
    authority_matrix = norms_matrix.merge(lsoa_ca, how="left", on="LSOA Origin ID")

    # non percentage conversions
    for indicator in ["Empl_pop", "5000EmpPT45n", "5000EmpCar45n", "PS_pop", "PSPT45n", "PSCar45n", "SS_pop",
                                         "SSPT45n", "SSCar45n", "FE_pop", "FEPT45n", "FECar45n", "GP_pop",
                                         "Hosp_pop", "Town_pop", "TownPTt", "TownCart"]: #, "5000EmpPT60n",
                                         #"5000EmpCar60n", "PSPT60n", "PSCar60n", "SSPT60n", "SSCar60n", "FEPT60n",
                                         #"FECar60n"]:
        authority_matrix[indicator] = authority_matrix[indicator] * authority_matrix["lsoa_to_ca_sectors"]

    # for journey times

    weighted_pop = authority_matrix.copy()

    for adjustment in ["Empl_pop", "PS_pop", "SS_pop", "FE_pop", "GP_pop", "Hosp_pop", "Town_pop"]:
        weighted_pop[adjustment + "_adjusted"] = weighted_pop[adjustment] * weighted_pop["lsoa_to_ca_sectors"]

    weighted_pop = weighted_pop.groupby("CA", as_index=False).sum()
    weighted_pop = weighted_pop[["CA", "Empl_pop_adjusted", "PS_pop_adjusted", "SS_pop_adjusted", "FE_pop_adjusted",
                                 "GP_pop_adjusted", "Hosp_pop_adjusted", "Town_pop_adjusted"]]
    authority_matrix = pd.merge(authority_matrix, weighted_pop, how="left", on="CA")

    #emp
    for indicator in ["5000EmpPTt", "5000EmpCart", "5000EmpPT30pct", "5000EmpCar30pct", "5000EmpPT45pct",
                      "5000EmpCar45pct", "5000EmpWalk15pct"]:
        authority_matrix[indicator] = authority_matrix[indicator] * authority_matrix["Empl_pop"] \
                                               / (authority_matrix["Empl_pop_adjusted"])
    #ps
    for indicator in ["PSPTt", "PSCart", "PSPT30pct", "PSCar30pct", "PSPT15pct"]:
        authority_matrix[indicator] = authority_matrix[indicator] * authority_matrix["PS_pop"] \
                                               / (authority_matrix["PS_pop_adjusted"])
    #ss
    for indicator in ["SSPTt", "SSCart", "SSPT30pct", "SSCar30pct", "SSPT15pct"]:
        authority_matrix[indicator] = authority_matrix[indicator] * authority_matrix["SS_pop"] \
                                               / (authority_matrix["SS_pop_adjusted"])
    #fe
    for indicator in ["FEPTt", "FECart", "FEPT30pct", "FECar30pct", "FEWalk15pct"]:
        authority_matrix[indicator] = authority_matrix[indicator] * authority_matrix["FE_pop"] \
                                               / (authority_matrix["FE_pop_adjusted"])
    #gp
    for indicator in ["GPPTt", "GPCart", "GPPT30pct", "GPCar30pct", "GPWalk15pct"]:
        authority_matrix[indicator] = authority_matrix[indicator] * authority_matrix["GP_pop"] \
                                               / (authority_matrix["GP_pop_adjusted"])
    #Hosp
    for indicator in ["HospPTt", "HospCart", "HospPT30pct", "HospCar30pct", "HospPT60pct", "HospCar60pct",
                      "HospWalk15pct"]:
        authority_matrix[indicator] = authority_matrix[indicator] * authority_matrix["Hosp_pop"] \
                                               / (authority_matrix["Hosp_pop_adjusted"])
    #town
    for indicator in ["TownPTt", "TownCart", "TownPT30pct", "TownCar30pct", "TownPT15pct"]:
        authority_matrix[indicator] = authority_matrix[indicator] * authority_matrix["Town_pop"] \
                                               / (authority_matrix["Town_pop_adjusted"])

    # grouping

    authority_matrix = authority_matrix.groupby(["CA", "Region"], as_index=False).sum()
    #finalising and applying cap

    authority_matrix["100EmpPT15pct"] = "unused"
    authority_matrix["500EmpPT15pct"] = "unused"

    authority_matrix = authority_matrix[["CA", "Region", "Empl_pop",  "5000EmpPT30pct",
                                         "5000EmpCar30pct", "5000EmpPT45pct", "5000EmpCar45pct", "100EmpPT15pct",
                                         "500EmpPT15pct", "5000EmpWalk15pct", "5000EmpPTt", "5000EmpCart",
                                         "5000EmpPT45n", "5000EmpCar45n", "PS_pop", "PSPT30pct", "PSCar30pct",
                                         "PSPT15pct", "PSPTt", "PSCart", "PSPT45n", "PSCar45n", "SS_pop", "SSPT30pct",
                                         "SSCar30pct", "SSPT15pct", "SSPTt",  "SSCart", "SSPT45n", "SSCar45n", "FE_pop",
                                         "FEPT30pct", "FECar30pct", "FEWalk15pct", "FEPTt", "FECart", "FEPT45n",
                                         "FECar45n", "GP_pop", "GPPT30pct", "GPCar30pct", "GPWalk15pct", "GPPTt",
                                         "GPCart", "Hosp_pop", "HospPT30pct", "HospCar30pct", "HospPT60pct",
                                         "HospCar60pct", "HospWalk15pct", "HospPTt", "HospCart", "Town_pop",
                                         "TownPT30pct", "TownCar30pct", "TownPT15pct", "TownPTt", "TownCart"]]#,
                                         #"5000EmpPT60n", "5000EmpCar60n", "PSPT60n", "PSCar60n", "SSPT60n", "SSCar60n",
                                         #"FEPT60n", "FECar60n"]]

    #select an upper limit on amenities to avoid saturation
    a_cap = 500

    for indicator in ["PSPT45n", "SSPT45n", "FEPT45n", "PSCar45n", "SSCar45n", "FECar45n", "5000EmpPT45n",
                      "5000EmpCar45n"]:
        authority_matrix.loc[(authority_matrix[indicator] > a_cap), indicator] = a_cap

    for indicator in ["5000EmpPT30pct", "5000EmpCar30pct", "5000EmpPT45pct", "5000EmpCar45pct", "5000EmpWalk15pct",
                      "PSPT30pct", "PSCar30pct", "PSPT15pct", "SSPT30pct", "SSCar30pct",
                      "SSPT15pct", "FEPT30pct", "FECar30pct", "FEWalk15pct", "GPPT30pct",
                      "GPCar30pct", "GPWalk15pct", "HospPT30pct", "HospCar30pct", "HospPT60pct", "HospCar60pct",
                      "HospWalk15pct", "TownPT30pct", "TownCar30pct", "TownPT15pct"]:
        authority_matrix.loc[(authority_matrix[indicator] > 1), indicator] = 1

    output_name = "CA_amenity_indicators_" + run_code + "_" + run_year + ".csv"
    print('Saving: %s' % output_name)
    authority_matrix.to_csv("outputs/%s" % output_name)

    return None
