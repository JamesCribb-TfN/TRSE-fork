import pandas as pd
import time


# Function called 1st within workbook_compile() - THIS HAS BEEN UPDATED TO LSOA ZONING
def input_long_format(run_code, year):
    """Select and convert target data from wide to long format."""

    file_name = "working_book_amenity_indicators_" + run_code + "_" + year  # + "_rail_only"
    lsoa_file, la_file, ca_file = pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

    la_lsoa = pd.read_csv(r'lookups\lads20_to_lsoa_correspondence.csv')
    la_lsoa.rename(columns={'lads20_zone_id': 'LA_id'}, inplace=True)
    ca_lsoa = pd.read_csv(r'lookups\ca_sectors_to_lsoa_correspondence.csv')
    ca_lsoa.rename(columns={'ca_sectors_zone_id': 'CA_id'}, inplace=True)

    for zone_type in ["", "LA", "CA"]:  # Options are: "LSOA", "LA" and "CA"
        if zone_type == "LA" or zone_type == "CA":
            zone_naming = zone_type
            zone_type = zone_type + "_"
        else:
            zone_naming = "LSOA Zone ID"

        print('---- Processing: %sData' % zone_type)
        data = pd.read_excel("workbooks/%s.xlsx" % file_name, "%sData" % zone_type)

        # Current workbooks in outputs for LA & CA are stored as LA/CA rather than LA_id/CA_id
        # LSOA zoned files are already saved as LSOA Zone ID
        # This section can likely be replaced by adding this to indicator_representation function
        # TODO: Above comment.
        # if zone_type == 'LA_':
        #    data.rename(columns={'LA': 'LA_id'}, inplace=True)
        # elif zone_type == 'CA_':
        #    data.reanme(columns={'CA': 'CA_id'}, inplace=True)

        # Rename for now to test functionality of script - Remove after.
        data.rename(columns={'NoRMS Zone ID': 'LSOA Zone ID'},
                    inplace=True)
        # print(data.columns)

        accessibility = pd.read_excel("workbooks/%s.xlsx" % file_name, "%sAccessibility" % zone_type, skiprows=1)
        # print('test1', accessibility.columns)
        indicators = pd.read_excel("workbooks/%s.xlsx" % file_name, "%sIndicators" % zone_type)
        transformed_indicators = pd.read_excel("workbooks/%s.xlsx" % file_name, "%sIndicators_trans" % zone_type)

        output_name = zone_type + "_" + run_code + "_" + year + ".csv"
        indicators.to_csv("assurance/indicators_%s" % output_name)
        accessibility.to_csv("assurance/accessibility_%s" % output_name)
        transformed_indicators.to_csv("assurance/transformed_indicators_%s" % output_name)

        # TODO: Below comment.
        # Debugging - remove after.
        if zone_type == "":
            accessibility.rename(columns={'NoRMS Zone ID': 'LSOA Zone ID'}, inplace=True)
            # print('test2', accessibility.columns)
            accessibility['LSOA Zone ID'] = accessibility['LSOA Zone ID'].astype(str)  # Convert from int(NoRMS)to LSOA
            indicators.rename(columns={'NoRMS Zone ID': 'LSOA Zone ID'}, inplace=True)
            indicators['LSOA Zone ID'] = indicators['LSOA Zone ID'].astype(str)
            transformed_indicators.rename(columns={'NoRMS Zone ID': 'LSOA Zone ID'}, inplace=True)
            transformed_indicators['LSOA Zone ID'] = transformed_indicators['LSOA Zone ID'].astype(str)
        # elif zone_type == 'CA_':
        # accessibility['CA'] = accessibility['CA'].astype(str)
        # indicators['CA'] = indicators['CA'].astype(str)
        # transformed_indicators['CA'] = transformed_indicators['CA'].astype(str)

        data = pd.melt(data,
                       id_vars=zone_naming,
                       var_name="data",
                       value_vars=["5000EmpPT45n", "5000EmpCar45n", "PSPT45n", "PSCar45n", "SSPT45n",
                                   "SSCar45n", "FEPT45n", "FECar45n", "5000EmpPT60n", "5000EmpCar60n", "PSPT60n",
                                   "PSCar60n", "SSPT60n", "SSCar60n", "FEPT60n", "FECar60n"],
                       value_name="data_value")

        accessibility = pd.melt(accessibility,
                                id_vars=zone_naming,
                                var_name="data",
                                value_vars=["Employment score", "Education score", "Health score", "Services score",
                                            "Transport access score", "Total score", "Employment", "Education",
                                            "Health", "Services", "Transport access", "Total"],
                                value_name="data_value")

        indicators = pd.melt(indicators,
                             id_vars=zone_naming,
                             var_name="data",
                             value_vars=["Population", "1 - PTCoverage", "1- 5000EmpPT30",
                                         "1- 5000EmpCar30", "1- 5000EmpPT45", "1- 5000EmpCar45",
                                         "5000EmpPTCar30Gap", "5000EmpPTCar45Gap",
                                         "5000EmpPTCarTimeGap / 100", "1 - 5000EmpPT45n",
                                         "1 - 5000EmpCar45n", "5000EmpPTCarDestGap / N", "Emp total",
                                         "1- PSPT30pct", "1- PSCar30pct", "PSPTCar30Gap",
                                         "PSPTCarTimeGap / 100", "1 - PSPT15pct", "LN(N+1-PSPT45n)",
                                         "LN(N+1-PSCar45n)", "PSPTCarDestGap / N", "PEdu total",
                                         "1- SSPT30pct", "1- SSCar30pct", "SSPTCar30Gap",
                                         "SSPTCarTimeGap / 100", "1 - SSPT15pct", "LN(N+1-SSPT45n)",
                                         "LN(N+1-SSCar45n)", "SSPTCarDestGap / N", "SEdu total",
                                         "1- FEPT30pct", "1- FECar30pct", "FEPTCar30Gap",
                                         "FEPTCarTimeGap / 100", "1 - FEPT15pct", "LN(N+1-FEPT45n)",
                                         "LN(N+1-FECar45n)", "FEPTCarDestGap / N", "FEdu total",
                                         "1 - GPPT30pct", "1 - GPCar30pct", "GPPTCar30Gap",
                                         "GPPTCarTimeGap / 100", "GP total", "1 - HospPT30pct",
                                         "1 - HospCar30pct", "HospPTCar30Gap", "HospPTCarTimeGap",
                                         "Hosp total", "1 - TownPT30pct", "1 - TownCar30pct",
                                         "TownPTCar30Gap", "TownPTCarTimeGap / 100", "1 - TownPT15pct",
                                         "1 - 5000EmpPT60n", "1 - 5000EmpCar60n", "1 - PSPT60n",
                                         "1 - PSCar60n", "1 - SSPT60n", "1 - SSCar60n", "1 - FEPT60n",
                                         "1 - FECar60n"],
                             value_name="data_value")

        transformed_indicators = pd.melt(transformed_indicators,
                                         id_vars=zone_naming,
                                         var_name="data",
                                         value_vars=["Emp rank", "Edu rank", "Health rank", "Services rank",
                                                     "Transport access rank"],
                                         value_name="data_value")

        zone_compiled = pd.concat([data, accessibility, indicators, transformed_indicators], axis=0)

        if zone_naming == "LSOA Zone ID":
            zone_compiled = zone_compiled.rename(columns={"LSOA Zone ID": "lsoa_zone_id", "data": "lsoa_data",
                                                          "data_value": "lsoa_data_value"})
            lsoa_file = zone_compiled
        elif zone_naming == "LA":
            zone_compiled = zone_compiled.rename(columns={"LA": "LA_id", "data": "LA_data",
                                                          "data_value": "LA_data_value"})
            la_file = zone_compiled
        elif zone_naming == "CA":
            zone_compiled = zone_compiled.rename(columns={"CA": "CA_id", "data": "CA_data",
                                                          "data_value": "CA_data_value"})
            ca_file = zone_compiled

        # long_file = pd.concat([long_file, zone_compiled], axis = 0)
    # print(la_lsoa.columns)
    # print(ca_lsoa.columns)
    la_lsoa = la_lsoa[["lsoa_zone_id", "LA_id"]]
    ca_lsoa = ca_lsoa[["lsoa_zone_id", "CA_id"]]

    # print('ca_lsoa DATA TYPES\n\n', ca_lsoa.dtypes)
    # print('ca_lsoa DATA TYPES\n\n', la_lsoa.dtypes)

    # print('Part1 -- ', ca_lsoa['CA_id'].unique(), 'with len', len(ca_lsoa['CA_id'].unique()), ca_lsoa.dtypes)

    #  FIX FOR MERGE NOT WORKING -- EVERY TYPE IS OBJECT APART FROM CA_id (Int64)
    ca_lsoa['CA_id'] = ca_lsoa['CA_id'].astype(str)
    # print('Part1.5 -- ', ca_lsoa['CA_id'].unique(), 'with len', len(ca_lsoa['CA_id'].unique()), ca_lsoa.dtypes)

    template = la_lsoa.merge(ca_lsoa, how="left", on="lsoa_zone_id")

    # print('TEMPLATE DTYPES\n\n', template.dtypes)
    # print('\n\nPArt 2 ----', template['CA_id'].unique(), '\n\n', template.dtypes)
    # template['CA_id'] = template['CA_id'].astype(int)

    # print('template test\n', template.dtypes)
    long_file = lsoa_file.merge(template, how="left", on="lsoa_zone_id")
    # print('long file 1\n', long_file.dtypes)
    long_file = long_file.merge(la_file, how="left", left_on=["LA_id", "lsoa_data"], right_on=["LA_id", "LA_data"])
    # print('long_file', long_file.dtypes)
    # print(long_file['CA_id'].unique(), len(long_file['CA_id'].unique()))
    # print('ca_file_og', ca_file.dtypes)
    # ca_file['CA_id'] = ca_file['CA_id'].astype(str)
    # print('ca_file_altered', ca_file.dtypes)
    long_file = long_file.merge(ca_file, how="left", left_on=["CA_id", "lsoa_data"], right_on=["CA_id", "CA_data"])

    # remember to apply multiplier
    # percentages may be left

    # repeat for CA when developed

    long_file["run_code"] = run_code  # + "_rail_only"
    long_file["year"] = year

    return long_file


# Function called 3rd within workbooks_compile() - THIS HAS BEEN UPDATED TO LSOA ZONING
def input_long_difference(run_code_a, year_a, run_code_b, year_b):
    """Select and convert target data from wide to long format."""

    file_name_a = "working_book_amenity_indicators_" + run_code_a + "_" + year_a  # "_rail_only"
    file_name_b = "working_book_amenity_indicators_" + run_code_b + "_" + year_b  # "_rail_only"
    lsoa_file, la_file, ca_file = pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
    la_lsoa = pd.read_csv(r'lookups\lads20_to_lsoa_correspondence.csv').rename(columns={'lads20_zone_id': 'LA_id'})
    ca_lsoa = pd.read_csv(r'lookups\ca_sectors_to_lsoa_correspondence.csv').rename(columns={'ca_sectors_zone_id':
                                                                                                'CA_id'})

    for zone_type in ["", "LA", "CA"]:  # Options are: "LSOA", "LA" and "CA"
        if zone_type == "LA" or zone_type == "CA":
            zone_naming = zone_type
            zone_type = zone_type + "_"
        else:
            zone_naming = "LSOA Zone ID"

        accessibility_a = pd.read_excel("workbooks/%s.xlsx" % file_name_a, "%sAccessibility" % zone_type, skiprows=1)
        accessibility_b = pd.read_excel("workbooks/%s.xlsx" % file_name_b, "%sAccessibility" % zone_type, skiprows=1)

        accessibility_a = pd.melt(accessibility_a,
                                  id_vars=zone_naming,
                                  var_name="data",
                                  value_vars=["Employment score", "Education score", "Health score", "Services score",
                                              "Transport access score", "Total score", "Employment", "Education",
                                              "Health", "Services", "Transport access", "Total"],
                                  value_name="data_value_a")
        accessibility_b = pd.melt(accessibility_b,
                                  id_vars=zone_naming,
                                  var_name="data",
                                  value_vars=["Employment score", "Education score", "Health score", "Services score",
                                              "Transport access score", "Total score", "Employment", "Education",
                                              "Health", "Services", "Transport access", "Total"],
                                  value_name="data_value_b")

        data_a = pd.read_excel("workbooks/%s.xlsx" % file_name_a, "%sData" % zone_type)
        data_b = pd.read_excel("workbooks/%s.xlsx" % file_name_b, "%sData" % zone_type)

        data_a = pd.melt(data_a,
                         id_vars=zone_naming,
                         var_name="data",
                         value_vars=["5000EmpPT45n", "5000EmpCar45n", "PSPT45n", "PSCar45n", "SSPT45n",
                                     "SSCar45n", "FEPT45n", "FECar45n", "5000EmpPT60n", "5000EmpCar60n", "PSPT60n",
                                     "PSCar60n", "SSPT60n", "SSCar60n", "FEPT60n", "FECar60n"],
                         value_name="data_value_a")

        data_b = pd.melt(data_b,
                         id_vars=zone_naming,
                         var_name="data",
                         value_vars=["5000EmpPT45n", "5000EmpCar45n", "PSPT45n", "PSCar45n", "SSPT45n",
                                     "SSCar45n", "FEPT45n", "FECar45n", "5000EmpPT60n", "5000EmpCar60n", "PSPT60n",
                                     "PSCar60n", "SSPT60n", "SSCar60n", "FEPT60n", "FECar60n"],
                         value_name="data_value_b")

        accessibility_a = pd.concat([accessibility_a, data_a], axis=0)
        accessibility_b = pd.concat([accessibility_b, data_b], axis=0)

        # merging and difference here
        zone_compiled = accessibility_a.merge(accessibility_b, how="left", on=[zone_naming, "data"])
        zone_compiled["data_value"] = zone_compiled["data_value_a"] - zone_compiled["data_value_b"]

        zone_compiled = zone_compiled[[zone_naming, "data", "data_value"]]

        if zone_naming == "LSOA Zone ID":
            zone_compiled = zone_compiled.rename(columns={"LSOA Zone ID": "lsoa_zone_id", "data": "lsoa_data",
                                                          "data_value": "lsoa_data_value"})
            lsoa_file = zone_compiled
        elif zone_naming == "LA":
            zone_compiled = zone_compiled.rename(columns={"LA": "LA_id", "data": "LA_data",
                                                          "data_value": "LA_data_value"})
            la_file = zone_compiled
        elif zone_naming == "CA":
            zone_compiled = zone_compiled.rename(columns={"CA": "CA_id", "data": "CA_data",
                                                          "data_value": "CA_data_value"})
            ca_file = zone_compiled

    la_lsoa = la_lsoa[["lsoa_zone_id", "LA_id"]]
    ca_lsoa = ca_lsoa[["lsoa_zone_id", "CA_id"]]
    template = la_lsoa.merge(ca_lsoa, how="left", on="lsoa_zone_id")
    long_file = lsoa_file.merge(template, how="left", on="lsoa_zone_id")
    long_file = long_file.merge(la_file, how="left", left_on=["LA_id", "lsoa_data"], right_on=["LA_id", "LA_data"])
    long_file = long_file.merge(ca_file, how="left", left_on=["CA_id", "lsoa_data"], right_on=["CA_id", "CA_data"])

    run_code = run_code_a + "-" + run_code_b  # "_rail_only"
    long_file["run_code"] = run_code  # "_rail_only"
    long_file["year"] = year_a

    return long_file


# Function called 2nd within workbook_compile() - THIS HAS BEEN UPDATED TO LSOA ZONING
def input_long_format_rail_only(run_code, year):
    """Select and convert target data from wide to long format."""

    file_name = "working_book_amenity_indicators_" + run_code + "_" + year  # "_rail_only"
    lsoa_file, la_file, ca_file = pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
    la_lsoa = pd.read_csv(r'lookups\lads20_to_lsoa_correspondence.csv').rename(columns={'lads20_zone_id': 'LA_id'})
    ca_lsoa = pd.read_csv(r'lookups\ca_sectors_to_lsoa_correspondence.csv').rename(columns={'ca_sectors_zone_id':
                                                                                                'CA_id'})

    for zone_type in ["", "LA", "CA"]:  # Options are: "LSOA", "LA" and "CA"
        if zone_type == "LA" or zone_type == "CA":
            zone_naming = zone_type
            zone_type = zone_type + "_"
        else:
            zone_naming = "LSOA Zone ID"

        data = pd.read_excel("workbooks/%s.xlsx" % file_name, "%sData" % zone_type)

        if zone_type == '':
            data.rename(columns={'NoRMS Zone ID': 'LSOA Zone ID'}, inplace=True)

        accessibility = pd.read_excel("workbooks/%s.xlsx" % file_name, "%sAccessibility" % zone_type, skiprows=1)
        indicators = pd.read_excel("workbooks/%s.xlsx" % file_name, "%sIndicators" % zone_type)
        transformed_indicators = pd.read_excel("workbooks/%s.xlsx" % file_name, "%sIndicators_trans" % zone_type)

        output_name = zone_type + "_" + run_code + "_" + year + ".csv"
        indicators.to_csv("assurance/indicators_%s" % output_name)
        accessibility.to_csv("assurance/accessibility_%s" % output_name)
        transformed_indicators.to_csv("assurance/transformed_indicators_%s" % output_name)

        # TODO: Below comment.
        # Debugging - remove after.
        if zone_type == "":
            data.rename(columns={'NoRMS Zone ID': 'LSOA Zone ID'}, inplace=True)
            accessibility.rename(columns={'NoRMS Zone ID': 'LSOA Zone ID'}, inplace=True)
            # print('test2', accessibility.columns)
            accessibility['LSOA Zone ID'] = accessibility['LSOA Zone ID'].astype(str)  # Convert from int(NoRMS)to LSOA
            indicators.rename(columns={'NoRMS Zone ID': 'LSOA Zone ID'}, inplace=True)
            indicators['LSOA Zone ID'] = indicators['LSOA Zone ID'].astype(str)
            transformed_indicators.rename(columns={'NoRMS Zone ID': 'LSOA Zone ID'}, inplace=True)
            transformed_indicators['LSOA Zone ID'] = transformed_indicators['LSOA Zone ID'].astype(str)

        data = pd.melt(data,
                       id_vars=zone_naming,
                       var_name="data",
                       value_vars=["5000EmpPT45n", "5000EmpCar45n", "PSPT45n", "PSCar45n", "SSPT45n",
                                   "SSCar45n", "FEPT45n", "FECar45n", "5000EmpPT60n", "5000EmpCar60n", "PSPT60n",
                                   "PSCar60n", "SSPT60n", "SSCar60n", "FEPT60n", "FECar60n"],
                       value_name="data_value")

        accessibility = pd.melt(accessibility,
                                id_vars=zone_naming,
                                var_name="data",
                                value_vars=["Employment score", "Education score", "Health score", "Services score",
                                            "Transport access score", "Total score", "Employment", "Education",
                                            "Health", "Services", "Transport access", "Total"],
                                value_name="data_value")

        indicators = pd.melt(indicators,
                             id_vars=zone_naming,
                             var_name="data",
                             value_vars=["Population", "1 - PTCoverage", "1- 5000EmpPT30",
                                         "1- 5000EmpCar30", "1- 5000EmpPT45", "1- 5000EmpCar45",
                                         "5000EmpPTCar30Gap", "5000EmpPTCar45Gap",
                                         "5000EmpPTCarTimeGap / 100", "1 - 5000EmpPT45n",
                                         "1 - 5000EmpCar45n", "5000EmpPTCarDestGap / N", "Emp total",
                                         "1- PSPT30pct", "1- PSCar30pct", "PSPTCar30Gap",
                                         "PSPTCarTimeGap / 100", "1 - PSPT15pct", "LN(N+1-PSPT45n)",
                                         "LN(N+1-PSCar45n)", "PSPTCarDestGap / N", "PEdu total",
                                         "1- SSPT30pct", "1- SSCar30pct", "SSPTCar30Gap",
                                         "SSPTCarTimeGap / 100", "1 - SSPT15pct", "LN(N+1-SSPT45n)",
                                         "LN(N+1-SSCar45n)", "SSPTCarDestGap / N", "SEdu total",
                                         "1- FEPT30pct", "1- FECar30pct", "FEPTCar30Gap",
                                         "FEPTCarTimeGap / 100", "1 - FEPT15pct", "LN(N+1-FEPT45n)",
                                         "LN(N+1-FECar45n)", "FEPTCarDestGap / N", "FEdu total",
                                         "1 - GPPT30pct", "1 - GPCar30pct", "GPPTCar30Gap",
                                         "GPPTCarTimeGap / 100", "GP total", "1 - HospPT30pct",
                                         "1 - HospCar30pct", "HospPTCar30Gap", "HospPTCarTimeGap",
                                         "Hosp total", "1 - TownPT30pct", "1 - TownCar30pct",
                                         "TownPTCar30Gap", "TownPTCarTimeGap / 100", "1 - TownPT15pct",
                                         "1 - 5000EmpPT60n", "1 - 5000EmpCar60n", "1 - PSPT60n",
                                         "1 - PSCar60n", "1 - SSPT60n", "1 - SSCar60n", "1 - FEPT60n",
                                         "1 - FECar60n"],
                             value_name="data_value")

        transformed_indicators = pd.melt(transformed_indicators,
                                         id_vars=zone_naming,
                                         var_name="data",
                                         value_vars=["Emp rank", "Edu rank", "Health rank", "Services rank",
                                                     "Transport access rank"],
                                         value_name="data_value")

        zone_compiled = pd.concat([data, accessibility, indicators, transformed_indicators], axis=0)

        if zone_naming == "LSOA Zone ID":
            zone_compiled = zone_compiled.rename(columns={"LSOA Zone ID": "lsoa_zone_id", "data": "lsoa_data",
                                                          "data_value": "lsoa_data_value"})
            lsoa_file = zone_compiled
        elif zone_naming == "LA":
            zone_compiled = zone_compiled.rename(columns={"LA": "LA_id", "data": "LA_data",
                                                          "data_value": "LA_data_value"})
            la_file = zone_compiled
        elif zone_naming == "CA":
            zone_compiled = zone_compiled.rename(columns={"CA": "CA_id", "data": "CA_data",
                                                          "data_value": "CA_data_value"})
            ca_file = zone_compiled

        # long_file = pd.concat([long_file, zone_compiled], axis = 0)
    la_lsoa = la_lsoa[["lsoa_zone_id", "LA_id"]]
    ca_lsoa = ca_lsoa[["lsoa_zone_id", "CA_id"]]
    # Fix for failed merge
    ca_lsoa['CA_id'] = ca_lsoa['CA_id'].astype(str)
    template = la_lsoa.merge(ca_lsoa, how="left", on="lsoa_zone_id")
    long_file = lsoa_file.merge(template, how="left", on="lsoa_zone_id")
    long_file = long_file.merge(la_file, how="left", left_on=["LA_id", "lsoa_data"], right_on=["LA_id", "LA_data"])
    long_file = long_file.merge(ca_file, how="left", left_on=["CA_id", "lsoa_data"], right_on=["CA_id", "CA_data"])

    # remember to apply multiplier
    # percentages may be left

    # repeat for CA when developed

    long_file["run_code"] = run_code  # "_rail_only"
    long_file["year"] = year

    return long_file


# Function called 4th within workbooks_compile() -
def input_long_difference_rail_only(run_code_a, year_a, run_code_b, year_b):
    """Select and convert target data from wide to long format."""

    file_name_a = "working_book_amenity_indicators_" + run_code_a + "_" + year_a  # "_rail_only"
    file_name_b = "working_book_amenity_indicators_" + run_code_b + "_" + year_b  # "_rail_only"
    lsoa_file, la_file, ca_file = pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
    la_lsoa = pd.read_csv(r'lookups\lads20_to_lsoa_correspondence.csv').rename(columns={'lads20_zone_id': 'LA_id'})
    ca_lsoa = pd.read_csv(r'lookups\ca_sectors_to_lsoa_correspondence.csv').rename(columns={'ca_sectors_zone_id':
                                                                                                'CA_id'})

    for zone_type in ["", "LA", "CA"]:  # Options are: "LSOA", "LA" and "CA"
        if zone_type == "LA" or zone_type == "CA":
            zone_naming = zone_type
            zone_type = zone_type + "_"
        else:
            zone_naming = "LSOA Zone ID"

        accessibility_a = pd.read_excel("workbooks/%s.xlsx" % file_name_a, "%sAccessibility" % zone_type, skiprows=1)
        accessibility_b = pd.read_excel("workbooks/%s.xlsx" % file_name_b, "%sAccessibility" % zone_type, skiprows=1)

        accessibility_a = pd.melt(accessibility_a,
                                  id_vars=zone_naming,
                                  var_name="data",
                                  value_vars=["Employment score", "Education score", "Health score", "Services score",
                                              "Transport access score", "Total score", "Employment", "Education",
                                              "Health", "Services", "Transport access", "Total"],
                                  value_name="data_value_a")
        accessibility_b = pd.melt(accessibility_b,
                                  id_vars=zone_naming,
                                  var_name="data",
                                  value_vars=["Employment score", "Education score", "Health score", "Services score",
                                              "Transport access score", "Total score", "Employment", "Education",
                                              "Health", "Services", "Transport access", "Total"],
                                  value_name="data_value_b")

        data_a = pd.read_excel("workbooks/%s.xlsx" % file_name_a, "%sData" % zone_type)
        data_b = pd.read_excel("workbooks/%s.xlsx" % file_name_b, "%sData" % zone_type)

        data_a = pd.melt(data_a,
                         id_vars=zone_naming,
                         var_name="data",
                         value_vars=["5000EmpPT45n", "5000EmpCar45n", "PSPT45n", "PSCar45n", "SSPT45n",
                                     "SSCar45n", "FEPT45n", "FECar45n", "5000EmpPT60n", "5000EmpCar60n", "PSPT60n",
                                     "PSCar60n", "SSPT60n", "SSCar60n", "FEPT60n", "FECar60n"],
                         value_name="data_value_a")

        data_b = pd.melt(data_b,
                         id_vars=zone_naming,
                         var_name="data",
                         value_vars=["5000EmpPT45n", "5000EmpCar45n", "PSPT45n", "PSCar45n", "SSPT45n",
                                     "SSCar45n", "FEPT45n", "FECar45n", "5000EmpPT60n", "5000EmpCar60n", "PSPT60n",
                                     "PSCar60n", "SSPT60n", "SSCar60n", "FEPT60n", "FECar60n"],
                         value_name="data_value_b")

        accessibility_a = pd.concat([accessibility_a, data_a], axis=0)
        accessibility_b = pd.concat([accessibility_b, data_b], axis=0)

        # merging and difference here
        zone_compiled = accessibility_a.merge(accessibility_b, how="left", on=[zone_naming, "data"])
        zone_compiled["data_value"] = zone_compiled["data_value_a"] - zone_compiled["data_value_b"]

        zone_compiled = zone_compiled[[zone_naming, "data", "data_value"]]

        if zone_naming == "LSOA Zone ID":
            zone_compiled = zone_compiled.rename(columns={"LSOA Zone ID": "lsoa_zone_id", "data": "lsoa_data",
                                                          "data_value": "lsoa_data_value"})
            lsoa_file = zone_compiled
        elif zone_naming == "LA":
            zone_compiled = zone_compiled.rename(columns={"LA": "LA_id", "data": "LA_data",
                                                          "data_value": "LA_data_value"})
            la_file = zone_compiled
        elif zone_naming == "CA":
            zone_compiled = zone_compiled.rename(columns={"CA": "CA_id", "data": "CA_data",
                                                          "data_value": "CA_data_value"})
            ca_file = zone_compiled

    la_lsoa = la_lsoa[["lsoa_zone_id", "LA_id"]]
    ca_lsoa = ca_lsoa[["lsoa_zone_id", "CA_id"]]
    template = la_lsoa.merge(ca_lsoa, how="left", on="lsoa_zone_id")
    long_file = lsoa_file.merge(template, how="left", on="lsoa_zone_id")
    long_file = long_file.merge(la_file, how="left", left_on=["LA_id", "lsoa_data"], right_on=["LA_id", "LA_data"])
    long_file = long_file.merge(ca_file, how="left", left_on=["CA_id", "lsoa_data"], right_on=["CA_id", "CA_data"])

    run_code = run_code_a + "-" + run_code_b  # "_rail_only"
    long_file["run_code"] = run_code
    long_file["year"] = year_a

    return long_file


def workbook_compile():
    """Compile multiple accessibility workbooks"""

    workbook_compiled = pd.DataFrame(columns=["lsoa_zone_id", "lsoa_data", "lsoa_data_value", "LA_id", "LA_data",
                                              "LA_data_value", "CA_id", "CA_data", "CA_data_value", "run_code", "year"])
    print('Compiling workbook file:', time.strftime("%H:%M:%S - %Y", time.localtime()))
    for run in ["IGU_2018", "KZI_2042", "KZJ_2052", "JPI_2042", "JPJ_2052", "K1P_2042", "K1Q_2052", "KZV_2042",
                "KZW_2052"]:

        run_code, year = run[0:3], run[4:8]
        print('--', run, 'file:',  "working_book_amenity_indicators_" + run_code + "_" + year,
              time.strftime("%H:%M:%S - %Y", time.localtime()))

        workbook = input_long_format(run_code, year)  # UPDATED TO LSOA
        workbook_compiled = pd.concat([workbook_compiled, workbook], axis=0)
        workbook_rail_only = input_long_format_rail_only(run_code, year)  # UPDATED TO LSOA
        workbook_compiled = pd.concat([workbook_compiled, workbook_rail_only], axis=0)

    print('-- Finished compiling. Now comparing.\n')
    workbook_compiled.to_csv(r'debugs\workbook_compiled.csv')
    # comparisons
    for run_pair in [["KZI_2042", "JPI_2042"], ["KZJ_2052", "JPJ_2052"], ["K1P_2042", "JPI_2042"],
                     ["K1Q_2052", "JPJ_2052"], ["KZV_2042", "JPI_2042"], ["KZW_2052", "JPJ_2052"]]:
        print('--', run_pair, time.strftime("%H:%M:%S - %Y", time.localtime()))
        run_code_a, year_a = run_pair[0][0:3], run_pair[0][4:8]
        run_code_b, year_b = run_pair[1][0:3], run_pair[1][4:8]
        workbook = input_long_difference(run_code_a, year_a, run_code_b, year_b)  # UPDATED TO LSOA
        workbook_compiled = pd.concat([workbook_compiled, workbook], axis=0)
        workbook_rail_only = input_long_difference_rail_only(run_code_a, year_a, run_code_b, year_b)
        #print('workbook rail only', workbook_rail_only.columns)
        #print('workbook compiled', workbook_compiled.columns)
        workbook_rail_only.tocsv(r'outputs\workbook_rail_only.csv')
        workbook_compiled.to_csv(r'outputs\workbook_compiled.csv')
        workbook_compiled = pd.concat([workbook_compiled, workbook_rail_only], axis=0)

    workbook_compiled.to_csv("outputs/accessibility_compiled_workbooks_bus_included.csv")
    return workbook_compiled


workbooks = workbook_compile()
