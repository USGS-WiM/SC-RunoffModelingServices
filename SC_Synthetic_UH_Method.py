import requests
import ast
import numpy as np
from Rainfall_Data_Curves import rainfall_data_curves
import math

# Extracts data from curve number GIS layer, then computes Runoff Weighted CN or Area Weighted CN
# Corresponds to "Data for CN Determination" sheet in spreadsheet
def weightedCurveNumber(lat, lon, P24hr, weightingMethod):
    # P24hr: 24-hour Rainfall Depth (P), in inches; comes from rainfallData function for corresponding AEP
    # weightingMethod: "runoff" or "area"

    # Placeholder data-- waiting on GIS data to be published
    curveNumberData = [
        {
            "CN": 55,
            "Area": 50.0
        },
        {
            "CN": 78,
            "Area": 50.0
        }
    ]

    if weightingMethod == "runoff":
        weighted_CN = runoffWeightedCN(curveNumberData, P24hr)
    elif (weightingMethod == "area"):
        weighted_CN =  areaWeightedCN(curveNumberData, P24hr)

    WS_retention_S = 1000.0 / weighted_CN - 10
    initial_abstraction_Ia = 0.2 * WS_retention_S

    return weighted_CN, WS_retention_S, initial_abstraction_Ia

# Calculates Runoff Weighted Curve Number
# Corresponds to "Runoff Weighted CN Calculator" sheet in spreadsheet
def runoffWeightedCN(curveNumberData, P24hr):
    #curveNumberData (example): [
    #     {
    #         "CN": 55,
    #         "Area": 50.0
    #     },
    #     {
    #         "CN": 78,
    #         "Area": 50.0
    #     }
    # ]
    # P24hr: 24-hour Rainfall Depth (P), in inches; comes from rainfallData function for corresponding AEP

    total_areaQCN24hr = 0.0 # Sum of Area * Q_CN
    total_area = 0.0
    for row in curveNumberData:
        total_area += row["Area"]
        S = 1000.0 / row["CN"] - 10 if row["CN"] > 0 else 0 # Watershed Retention
        Ia = 0.2 * S # Initial Abstraction
        QCN24hr = ((P24hr-Ia)**2)/(P24hr + 0.8 * S) if row["CN"] > 0 else 0 # 24-hr Q_CN
        areaQCN24hr = row["Area"] * QCN24hr # Area * Q_CN
        total_areaQCN24hr += areaQCN24hr 
    Q_CN = total_areaQCN24hr / total_area # 24-hour Runoff Depth
    runoff_weighted_CN = 1000.0 / (10 + 5*P24hr + 10*Q_CN - 10*(Q_CN**2 + 1.25*P24hr*Q_CN)**0.5) if 1000 / (10 + 5*P24hr + 10*Q_CN - 10*(Q_CN**2 + 1.25*P24hr*Q_CN)**0.5)>0 else 0

    return runoff_weighted_CN

# Calculates Area Weighted Curve Number
# Corresponds to "Area Weighted CN Calculator" sheet in spreadsheet
def areaWeightedCN(curveNumberData, P24hr):
    #curveNumberData (example): [
    #     {
    #         "CN": 55,
    #         "Area": 50.0
    #     },
    #     {
    #         "CN": 78,
    #         "Area": 50.0
    #     }
    # ]
    # P24hr: 24-hour Rainfall Depth (P), in inches; comes from rainfallData function for corresponding AEP

    total_areaCN = 0.0 # Sum of Area * CN
    total_area = 0.0
    for row in curveNumberData:
        total_area += row["Area"]
        total_areaCN += row["Area"] * row["CN"] 
    area_weighted_CN = total_areaCN / total_area

    return area_weighted_CN

# Extracts data from PRF GIS layer 
# Corresponds to "PRF Calculator" sheet in spreadsheet
def PRFData(lat, lon):
    

    # Placeholder data-- waiting on GIS data to be published
    PRFData = [
        {
            "PRF": 180,
            "Area": 50.0
        },
        {
            "PRF": 300,
            "Area": 50.0
        }
    ]

    # Calculate Watershed PRF and Shape Parameter, n (also called Gamma_n)
    total_watershed_area = 0.0
    total_product = 0.0
    for row in PRFData:
        total_watershed_area += row["Area"]
        total_product += row["PRF"] * row["Area"]
    PRF = total_product / total_watershed_area

    return PRF


# Calculates the Gamma n value for a given PRF value
# Corresponds to "PRF Calculator" sheet in spreadsheet
def gammaN(PRF):
    # PRF: Peak Rate Factor, output from PRFData function or user input

    # Corresponds to "UH Parameters" table
    UHParametersPRFGammaN = [
        {
            "PRF": 50,
            "Gamma_n": 1.05
        },
        {
            "PRF": 100,
            "Gamma_n": 1.25
        },
        {
            "PRF": 156,
            "Gamma_n": 1.50
        },
        {
            "PRF": 237,
            "Gamma_n": 2.00
        },
        {
            "PRF": 298,
            "Gamma_n": 2.50
        },
        {
            "PRF": 349,
            "Gamma_n": 3.00
        },
        {
            "PRF": 393,
            "Gamma_n": 3.50
        },
        {
            "PRF": 433,
            "Gamma_n": 4.00
        },
        {
            "PRF": 470,
            "Gamma_n": 4.50
        },
        {
            "PRF": 484,
            "Gamma_n": 4.70
        },
        {
            "PRF": 504,
            "Gamma_n": 5.00
        },
        {
            "PRF": 566,
            "Gamma_n": 6.00
        }
    ]

    Gamma_n = None
    for index, PRFGamma_n_pair in enumerate(UHParametersPRFGammaN):
        if PRF < PRFGamma_n_pair["PRF"]:
            Gamma_n = UHParametersPRFGammaN[index-1]["Gamma_n"]+((PRFGamma_n_pair["Gamma_n"]-UHParametersPRFGammaN[index-1]["Gamma_n"])/(PRFGamma_n_pair["PRF"]-UHParametersPRFGammaN[index-1]["PRF"]
    ))*(PRF-UHParametersPRFGammaN[index-1]["PRF"])
            break

    return Gamma_n

# Retrieve rainfall data from the NOAA Precipitation Frequency Data Server
# https://hdsc.nws.noaa.gov/hdsc/pfds/pfds_map_cont.html?bkmrk=sc
# Corresponds to "Rainfall Data" sheet in spreadsheet
def rainfallData(lat, lon):

    # Request data from NOAA
    requestURL = "https://hdsc.nws.noaa.gov/cgi-bin/hdsc/new/cgi_readH5.py?lat={}&lon={}".format(lat, lon)
    response = requests.get(requestURL)
    if response.status_code == 200:
        response_content = response.content.decode('utf-8')
    else:
        raise Exception("Request to NOAA data server failed")

    # Extract the results from the response
    data_string = response_content[response_content.index("quantiles = ")+len("quantiles = "):response_content.index("upper")-2] # String of data
    data_lists = ast.literal_eval(data_string) # Convert string to list of lists
    results = [list(map(float, sublist)) for sublist in data_lists] # Convert string values to floating point

    # Precipitation frequency estimates (inches) by duration of storms (hours): 1, 2, 3, 6, 12, 24
    # Columns correspond to average recurrence interval (years): 1, 2, 5, 10, 25, 50, 100, 200, 500, 1000
    results_1hr = results[4]
    results_2hr = results[5]
    results_3hr = results[6]
    results_6hr = results[7]
    results_12hr = results[8]
    results_24hr = results[9]
    # Save values of interest: these values coorespond to Names in the Spreadsheet for the SC Synethic Unit Hydrograph Method
    # Variable naming schema: ex. P50_12 refers to the precipitation frequency estimate (inches) for 12-hour storms with an average recurrence interval of 50 years (AEP 2%)
    P10_1 = results_1hr[3]
    P10_2 = results_2hr[3]
    P10_3 = results_3hr[3]
    P10_6 = results_6hr[3]
    P10_12 = results_12hr[3]
    P10_24 = results_24hr[3]
    
    P25_1 = results_1hr[4]
    P25_2 = results_2hr[4]
    P25_3 = results_3hr[4]
    P25_6 = results_6hr[4]
    P25_12 = results_12hr[4]
    P25_24 = results_24hr[4]
    
    P50_1 = results_1hr[5]
    P50_2 = results_2hr[5]
    P50_3 = results_3hr[5]
    P50_6 = results_6hr[5]
    P50_12 = results_12hr[5]
    P50_24 = results_24hr[5]

    P100_1 = results_1hr[6]
    P100_2 = results_2hr[6]
    P100_3 = results_3hr[6]
    P100_6 = results_6hr[6]
    P100_12 = results_12hr[6]
    P100_24 = results_24hr[6]
    
    # Variable naming schema: ex. P2_24_5 refers to the precipitation frequency estimate (inches) for 24-hour storms with an average recurrence interval of 5 years (AEP 20%)
    P2_24_1 = results_24hr[0]
    P2_24_2 = results_24hr[1]
    P2_24_5 = results_24hr[2]
    P2_24_10 = results_24hr[3]
    P2_24_25 = results_24hr[4]
    P2_24_50 = results_24hr[5]
    P2_24_100 = results_24hr[6]

    return P10_1,P10_2,P10_3,P10_6,P10_12,P10_24,P25_1,P25_2,P25_3,P25_6,P25_12,P25_24,P50_1,P50_2,P50_3,P50_6,P50_12,P50_24,P100_1,P100_2,P100_3,P100_6,P100_12,P100_24,P2_24_1,P2_24_2,P2_24_5,P2_24_10,P2_24_25,P2_24_50,P2_24_100

# Retrieve the rainfall distribution curve number from the NOAA Atlas 14 Rainfall Distributions
# The available rainfall distribution curve letters in this map service are NOAA A, NOAA B, NOAA C, and NOAA D
# Note: Type II and Type II Rainfall Distribution Curves are also possible but will be provided as a manual selection option in the user interface
# Corresponds to "Rainfall Data" and "SC Rainfall Distribution Map" sheets in spreadsheet
def rainfallDistributionCurve(lat, lon): 

    # Use map service to query the coordinate point with the NOAA Atlast 14 rainfall distributions map service
    requestURL = "https://gis.streamstats.usgs.gov/arcgis/rest/services/runoffmodeling/SC_rainfallcurve/MapServer/0/query?geometry={}%2C{}&geometryType=esriGeometryPoint&returnGeometry=false&f=pjson".format(lon,lat)
    response = requests.get(requestURL)
    if response.status_code != 200:
        raise Exception("Request to rainfall distribution curve map servivce failed")

    # Extract the NOAA rainfall distribution curve letter from the map service response
    response_content = response.json()
    rainfall_distribution_curve_letter = response_content["features"][0]["attributes"]["Rf_Dist"]
    
    # Translate the NOAA rainfall distribution curve letter to the rainfall distribution curve number used in the SC Synthetic UH Method spreadsheet
    # Note: Type II = 2 and Type III = 3 are two other options, but these will be provided as a manual selection option in the user interface
    rainfall_distribution_curve_letter_number = {
        "A": 4,
        "B": 5,
        "C": 6,
        "D": 7
    }
    rainfall_distribution_curve_number = rainfall_distribution_curve_letter_number[rainfall_distribution_curve_letter]

    return rainfall_distribution_curve_letter, rainfall_distribution_curve_number

def SCSyntheticUnitHydrograph(lat, lon, AEP, CNModificationMethod, Area, Tc, RainfallDistributionCurve, PRF, CN, S, Ia):
    P10_1,P10_2,P10_3,P10_6,P10_12,P10_24,P25_1,P25_2,P25_3,P25_6,P25_12,P25_24,P50_1,P50_2,P50_3,P50_6,P50_12,P50_24,P100_1,P100_2,P100_3,P100_6,P100_12,P100_24,P2_24_1,P2_24_2,P2_24_5,P2_24_10,P2_24_25,P2_24_50,P2_24_100 = rainfallData(lat,lon)

    if AEP == 10:
        rainfall_depths = [P10_1,P10_2,P10_3,P10_6,P10_12,P10_24]
    elif AEP == 4:
        rainfall_depths = [P25_1,P25_2,P25_3,P25_6,P25_12,P25_24]
    elif AEP == 2:
        rainfall_depths = [P50_1,P50_2,P50_3,P50_6,P50_12,P50_24]
    elif AEP == 1:
        rainfall_depths = [P100_1,P100_2,P100_3,P100_6,P100_12,P100_24]

    storm_duration = [1, 2, 3, 6, 12, 24]
    

    # Adjust CN when D < 24-hr
    CN_adjusted_for_rainfall_duration = []
    S_values = []
    Ia_values = []
    if CNModificationMethod == "McCuen":
        for rainfall_depth, D in zip(rainfall_depths, storm_duration):
            Gamma_D_hr = 10+0.00256*((98-CN)**(5.0/3.0))*(24-D)**0.5
            S_D_hr = 1000.0 / CN - Gamma_D_hr
            S_values.append(S_D_hr)
            Ia_D_hr = 0.2 * S_D_hr
            Q_CN_D_hr = ((rainfall_depth-0.2*S_D_hr)**2)/(rainfall_depth+0.8*S_D_hr)
            CN_adjusted_for_rainfall_duration.append(Q_CN_D_hr)
            Ia_values.append(0.2*(1000/Q_CN_D_hr-10))
    elif CNModificationMethod == "Merkel":
        for rainfall_depth, D in zip(rainfall_depths, storm_duration):
            Gamma_D_hr = 10+0.00256*((98-CN)**(5.0/3.0))*(24-D)**0.5
            S_D_hr = 1000.0 / CN - Gamma_D_hr
            S_values.append(S_D_hr)
            Q_CN_24_hr =((rainfall_depth-Ia)**2)/(rainfall_depth+0.8*S)
            P_Ia_Q_CN = rainfall_depth - Ia - Q_CN_24_hr
            Infiltration_Rate_24_hr = P_Ia_Q_CN / 24.0
            Infiltration_1_hr = D * Infiltration_Rate_24_hr
            Infiltration_1_hr_Plus_Ia = Infiltration_1_hr + Ia
            Runoff_1_hr = rainfall_depth - Infiltration_1_hr_Plus_Ia
            Q_CN_D_hr = 1000 / (10 + 5*rainfall_depth + 10*Runoff_1_hr - 10*(Runoff_1_hr**2 + 1.25*rainfall_depth*Runoff_1_hr)**0.5)
            if Q_CN_D_hr < 0:
                Q_CN_D_hr = 0
            CN_adjusted_for_rainfall_duration.append(Q_CN_D_hr)
            Ia_values.append(0.2*(1000/Q_CN_D_hr-10))

    # P(t) Distribution
    runoff_volume_Q_CN = []
    Q_CN_t_values = []
    burst_duration = 6 # minutes

    summations = []
    peak_runoff_Qp = []
    time_of_peak_runoff = [] 

    for rainfall_depth, D, Ia_value, S_value in zip(rainfall_depths, storm_duration, Ia_values, S_values):
        times = np.arange(0,(D*60)+burst_duration,burst_duration).tolist()
        # print(times)
        index = 0
        for time in times:
            P_P1 = rainfall_data_curves[RainfallDistributionCurve][D][index]
            P_t = P_P1 * rainfall_depth
            Numerator = max(P_t-Ia_value,0)
            Q_CN_t = Numerator*Numerator/(P_t+0.8*S_value)
            Q_CN_t_values.append(Q_CN_t)
            index += 1
    
        # print("")
        # print(Q_CN_t_values)
        runoff_volume_Q_CN.append(Q_CN_t_values[-1])
        Inc_QCN_values = []
        index = 0
        for Q_CN_t_value in Q_CN_t_values:
            # print(Q_CN_t_value)
            if index > 0:
                Inc_QCN_values.append(Q_CN_t_value - Q_CN_t_values[index-1])
            index += 1 

        # Q_AEP_D-hour sheet
        Gamma_n = gammaN(PRF)
        AdjTc = burst_duration*(math.floor((Tc+burst_duration/2.0)/burst_duration))
        UH_Tp = burst_duration*(math.floor((0.6*AdjTc+burst_duration)/burst_duration))
        UH_Qp =(PRF*Area*60.0)/(UH_Tp*640.0)
        burst_increments = Inc_QCN_values
        # print(burst_increments)
        # print(burst_increments)
        # print(burst_increments[0])
        UH = []
        times = np.arange(0,2*24*60,burst_duration).tolist()
        for time in times:
            UH.append(UH_Qp*((time/UH_Tp)*math.exp(1.0-time/UH_Tp))**(Gamma_n-1.0))
        # print(UH)
        bursts = []
        number_of_bursts = D * 10
        for number_burst in np.arange(number_of_bursts):
            this_burst = []
            for idx in np.arange(number_burst):
                this_burst.append(0.0)
            for UH_value in UH:
                this_burst.append(UH_value * burst_increments[number_burst])
            bursts.append(this_burst)
        summation = [0.0] * len(times) 
        index = 0
        for time in times:
            for burst in bursts:
                summation[index] += burst[index]
            index += 1 
        summations.append(summation)
        peak_runoff_Qp.append(max(summation))
        index_max = np.argmax(summation)
        time_of_peak_runoff.append(times[index_max])

    print(peak_runoff_Qp)
    print(time_of_peak_runoff)

    runoff_results_table = {
        "storm_duration": storm_duration,
        "rainfall_depth": rainfall_depths,
        "CN_adjusted_for_rainfall_duration": CN_adjusted_for_rainfall_duration,
        "runoff_volume_Q_CN": runoff_volume_Q_CN,
        "peak_runoff_Qp": peak_runoff_Qp,
        "time_of_peak_runoff": time_of_peak_runoff
    }

    hydrograph_ordinates_table = {
        "time": np.arange(0,(2*24*60)+burst_duration,burst_duration).tolist(),
        "flow_1_hour": summations[0],
        "flow_2_hour": summations[1],
        "flow_3_hour": summations[2],
        "flow_6_hour": summations[3],
        "flow_12_hour": summations[4],
        "flow_24_hour": summations[5]
    }

    return runoff_results_table, hydrograph_ordinates_table