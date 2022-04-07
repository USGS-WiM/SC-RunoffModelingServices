import requests
import ast

def curveNumber(lat, lon):
    return "Hello, World!"

# Retrieve rainfall data from the NOAA Precipitation Frequency Data Server
# https://hdsc.nws.noaa.gov/hdsc/pfds/pfds_map_cont.html?bkmrk=sc
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
    if rainfall_distribution_curve_letter == "A":
        rainfall_distribution_curve_number = 4
    elif rainfall_distribution_curve_letter == "B":
        rainfall_distribution_curve_number = 5
    elif rainfall_distribution_curve_letter == "C":
        rainfall_distribution_curve_number = 6
    elif rainfall_distribution_curve_letter == "D":
        rainfall_distribution_curve_number = 7

    return rainfall_distribution_curve_letter, rainfall_distribution_curve_number