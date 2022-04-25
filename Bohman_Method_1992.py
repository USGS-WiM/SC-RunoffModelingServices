import requests
import ast
import numpy as np
# import matplotlib.pyplot as plt

# Retrieve the 2-year 2-hour rainfall amount, in inches, from the the NOAA Precipitation Frequency Data Server
# https://hdsc.nws.noaa.gov/hdsc/pfds/pfds_map_cont.html?bkmrk=sc
def getRI2(lat, lon):
    # lat, lon are the coordinates of the drainage point

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

    # Extract value corresponding to 2-hr duration storms and 2-year average recurrence interval
    result_2hr_2yr = results[5][1]

    # Return the 2-year 2-hour rainfall amount (inches)
    return result_2hr_2yr

# Compute flood hydrographs for urban watersheds based on the Bohman 1992 method
# Report: https://doi.org/10.3133/wri924040
def computeUrbanFloodHydrographBohman1992(lat, lon, region3PercentArea, region4PercentArea, region3Qp, region4Qp, A, L, S, TIA):
    # lat, lon: coordinates of the drainage point (float)
    # region3PercentArea: percent area of the basin that is in Region_3_Urban_2014_5030: Piedmont-upper Coastal Plain (%, float)
    # region4PercentArea: percent area of the basin that is in Region_4_Urban_2014_5030: lower Coastal Plain (%, float)
    # region3Qp: flow statistic for the AEP of interest (ex. "UPK50AEP") in Region_3_Urban_2014_5030 (cubic feet per second, float)
    # region4Qp: flow statistic for the AEP of interest (ex. "UPK50AEP") in Region_4_Urban_2014_5030 (cubic feet per second, float)
    # A: drainage area (square miles, float)
    # L: main channel length (miles, float)
    # S: main channel slope (feet per mile, float)
    # TIA: total impervious area (%, float)

    # Check that Region_3_Urban_2014_5030 or Region_4_Urban_2014_5030 has some area
    if region3PercentArea + region4PercentArea == 0:
        raise Exception("No area in Region_3_Urban_2014_5030 or Region_4_Urban_2014_5030.")

    # Calculate the fraction area of each region
    region3FractionArea = region3PercentArea / 100.0
    region4FractionArea = region4PercentArea / 100.0

    RI2 = getRI2(lat, lon) # 2-year 2-hour rainfall amount (%)
    LT = 20.2 * ((L/S**0.5)**0.623) * (TIA ** -0.919) * (RI2 ** 1.129) # Average basin lag time (hours), Equation 5
    weightedQp = (region3Qp * region3FractionArea) + (region4Qp * region4FractionArea) # Weighted peak flow (cubic feet per second)

    region3VR = 0.001525 * (A ** -1.038) * (weightedQp ** 1.013) * (LT ** 1.030) # Average runoff volume (inches), Equation 6
    region4VR = 0.001648 * (A ** -1.038) * (weightedQp ** 1.013) * (LT ** 1.030) # Average runoff volume (inches), Equation 7
    weightedVR = (region3VR * region3FractionArea) + (region4VR * region4FractionArea) # Weighted average runoff volume for an urban basin (inches)
    
    region3F = 0.967 * (A ** -0.038) * (weightedQp ** 0.013) * (LT ** 0.030) # Lag-time correction factor, Equation 10
    region4F = 0.934 * (A ** -0.038) * (weightedQp ** 0.013) * (LT ** 0.030) # Lag-time correction factor, Equation 11
    weightedF = (region3F * region3FractionArea) + (region4F * region4FractionArea) # Weighted lag-time correction factor

    LTA = weightedF * LT # Adjusted lag time

    ## Table 10: Time and discharge ratios of the urban dimensionless hydrographs for the Piedmont-upper Coastal Plain and lower Coastal Plain regions
    # tD: time (hours)
    # LT: lag time (hours) 
    # Time ratio: tD / LT
    timeRatio = np.arange(0.05,2.55,0.05)
    # QtD: discharge at time t (cubic feet per second)
    # Qp: peak discharge (cubic feet per second)
    # Discharge ratio: QtD / Qp
    region3DischargeRatioList =    [0.07, 0.10, 0.15, 0.21, 0.28,
                                    0.37, 0.47, 0.58, 0.69, 0.79,
                                    0.87, 0.93, 0.97, 1.00, 0.97,
                                    0.94, 0.89, 0.83, 0.77, 0.71,
                                    0.65, 0.59, 0.54, 0.49, 0.44,
                                    0.40, 0.37, 0.34, 0.31, 0.28,
                                    0.26, 0.24, 0.22, 0.20, 0.19,
                                    0.17, 0.16, 0.15, 0.14, 0.13,
                                    0.12, 0.11, 0.11, 0.10, 0.09,
                                    0.09, 0.08, 0.07, 0.07, 0.06]
    region3DischargeRatio = np.asarray(region3DischargeRatioList)
    region4DischargeRatioList =    [0.00, 0.08, 0.12, 0.19, 0.28,
                                    0.39, 0.51, 0.64, 0.75, 0.85,
                                    0.93, 0.97, 1.00, 0.99, 0.97,
                                    0.94, 0.90, 0.86, 0.81, 0.76,
                                    0.71, 0.66, 0.62, 0.57, 0.53,
                                    0.49, 0.46, 0.42, 0.39, 0.36,
                                    0.33, 0.31, 0.28, 0.26, 0.24,
                                    0.22, 0.21, 0.19, 0.18, 0.17,
                                    0.16, 0.14, 0.13, 0.13, 0.12,
                                    0.11, 0.10, 0.10, 0.09, 0.08]
    region4DischargeRatio = np.asarray(region4DischargeRatioList)

    # Determine the region with the largest percentage of drainage in order to use that region's discharge ratio values
    if region3PercentArea > region4PercentArea:
        dischargeRatio = region3DischargeRatio
    else:
        dischargeRatio = region4DischargeRatio

    # Calculate coordinates for the urban flood hydrograph
    timeCoordinates = timeRatio * LTA
    dischargeCoordinates = dischargeRatio * weightedQp

    # Show the scatter plot of the rural flood hydrograph (for testing)
    # plt.scatter(timeCoordinates, dischargeCoordinates)
    # plt.show()

    ## Check limitations

    warningMessage = ""
    # Check limitations of Runoff Volume method on page 54
    warningMessageVR = "One or more of the parameters is outside the suggested range; runoff volume was estimated with unknown errors. "
    if A < 0.18 or A > 9.05:
        warningMessage += warningMessageVR
    if weightedQp < 33.1 or weightedQp > 1144:
        warningMessage += warningMessageVR
    if LT < 0.27 or LT > 3.10:
        warningMessage += warningMessageVR

    # Check limitations of urban hydrograph method on page 65
    warningMessageUH = "One or more of the parameters is outside the suggested range; urban hydrograph was estimated with unknown errors. "
    if A < 0.18 or A > 41.0:
        warningMessage += warningMessageUH
    if TIA < 10.0 or TIA > 51.0:
        warningMessage += warningMessageUH
    if (L/S**0.5) < 0.0493 or (L/S**0.5) > 0.875:
        warningMessage += warningMessageUH
    if RI2 < 1.95 or RI2 > 2.56:
        warningMessage += warningMessageUH

    warningMessage += "These methods are not applicable in basins with large rural sub-basins or areas with extreme contrasts in level of urbanization. "

    return weightedVR, timeCoordinates.tolist(), dischargeCoordinates.tolist(), warningMessage