import numpy as np
# import matplotlib.pyplot as plt

# Compute flood hydrographs for rural watersheds based on the Bohman 1989 method
# Report: https://doi.org/10.3133/wri894087
def computeRuralFloodHydrographBohman1989(regionBlueRidgePercentArea, regionPiedmontPercentArea, regionUpperCoastalPlainPercentArea,
                                            regionLowerCoastalPlain1PercentArea, regionLowerCoastalPlain2PercentArea, Qp, A):
    # regionBlueRidgePercentArea: percent area of the basin that is in Blue Ridge (percent, float)
    # regionPiedmontPercentArea: percent area of the basin that is in Piedmont (percent, float)
    # regionUpperCoastalPlainPercentArea: percent area of the basin that is in Upper Coastal Plain (percent, float)
    # regionLowerCoastalPlain1PercentArea: percent area of the basin that is in Lower Coastal Plain Region 1 (percent, float)
    # regionLowerCoastalPlain2PercentArea: percent area of the basin that is in Lower Coastal Plain Region 2 (percent, float)
    # Qp: area-weighted flow statistic for the AEP of interest (cubic feet per second, float)
    # A: total basin drainage area (square miles, float)

    # Calculate the fraction area of each region
    regionBlueRidgeFractionArea = regionBlueRidgePercentArea / 100.0
    regionPiedmontFractionArea = regionPiedmontPercentArea / 100.0
    regionUpperCoastalPlainFractionArea = regionUpperCoastalPlainPercentArea / 100.0
    regionLowerCoastalPlain1FractionArea = regionLowerCoastalPlain1PercentArea / 100.0
    regionLowerCoastalPlain2FractionArea = regionLowerCoastalPlain2PercentArea / 100.0

    # Calculate Lag Time (LT) based on Table 11 equations
    regionBlueRidgeLT = 3.71 * (A ** 0.265)
    regionPiedmontLT =  2.66 * (A ** 0.460)
    regionUpperCoastalPlainLT = 6.10 * (A ** 0.417)
    regionLowerCoastalPlain1LT = 6.62 * (A ** 0.341)
    regionLowerCoastalPlain2LT = 10.88 * (A ** 0.341)

    # Calculate Runoff Volume (VR) based on Table 13 equations
    regionBlueRidgeVR = 0.003780 * (A ** -0.911) * (Qp ** 0.888) * (regionBlueRidgeLT ** 0.879)
    regionPiedmontVR = 0.002418 * (A ** -0.798) * (Qp ** 0.880) * (regionPiedmontLT ** 0.896)
    regionUpperCoastalPlainVR = 0.003854 * (A ** -0.926) * (Qp ** 0.990) * (regionUpperCoastalPlainLT ** 0.721)
    regionLowerCoastalPlain1VR = 0.002652 * (A ** -0.953) * (Qp ** 0.978) * (regionLowerCoastalPlain1LT ** 0.882)
    regionLowerCoastalPlain2VR = 0.002872  * (A ** -0.953) * (Qp ** 0.978) * (regionLowerCoastalPlain2LT ** 0.882)

    # Weight the regional Runoff Volume (VR) values
    weightedVR = (regionBlueRidgeFractionArea * regionBlueRidgeVR) + \
                 (regionPiedmontFractionArea * regionPiedmontVR) + \
                 (regionUpperCoastalPlainFractionArea * regionUpperCoastalPlainVR) + \
                 (regionLowerCoastalPlain1FractionArea * regionLowerCoastalPlain1VR) + \
                 (regionLowerCoastalPlain2FractionArea * regionLowerCoastalPlain2VR) 
    
    # Calculate the Adjusted Lag Time (LTA) based on Equations 8 through 12
    regionBlueRidgeLTA = 7.21 * (A ** 0.322) * (Qp ** -0.112)
    regionPiedmontLTA = 3.30 * (A ** 0.614) * (Qp ** -0.120)
    regionUpperCoastalPlainLTA = 7.03 * (A ** 0.375) * (Qp ** -0.010)
    regionLowerCoastalPlain1LTA = 6.95 * (A ** 0.348) * (Qp ** -0.022)
    regionLowerCoastalPlain2LTA = 11.7 * (A ** 0.348) * (Qp ** -0.022)

    # Weight the Adjusted Lag Time (LTA) values
    weightedLTA = (regionBlueRidgeFractionArea * regionBlueRidgeLTA) + \
                 (regionPiedmontFractionArea * regionPiedmontLTA) + \
                 (regionUpperCoastalPlainFractionArea * regionUpperCoastalPlainLTA) + \
                 (regionLowerCoastalPlain1FractionArea * regionLowerCoastalPlain1LTA) + \
                 (regionLowerCoastalPlain2FractionArea * regionLowerCoastalPlain2LTA) 

    ## Table 3: Time and discharge ratios of the dimensionless hydrographs for the indicated regions
    # Time ratio: t / LTA
    timeRatio = np.arange(0.15,2.55,0.05)
    # Discharge ratio: Q / Qp
    regionBlueRidgeDischargeRatioList =   [ 0.08, 0.14, 0.22, 0.31, 0.43,
                                            0.56, 0.69, 0.80, 0.89, 0.96,
                                            0.99, 1.00, 0.97, 0.93, 0.88,
                                            0.82, 0.76, 0.71, 0.65, 0.60,
                                            0.56, 0.51, 0.47, 0.44, 0.41,
                                            0.38, 0.35, 0.33, 0.30, 0.28,
                                            0.26, 0.24, 0.23, 0.21, 0.20,
                                            0.19, 0.17, 0.16, 0.15, 0.14,
                                            0.14, 0.13, 0.12, 0.12, 0.11,
                                            0.10, 0.10, 0.09 ]
    regionBlueRidgeDischargeRatio = np.asarray(regionBlueRidgeDischargeRatioList)
    regionPiedmontDischargeRatioList =     [ 0.07, 0.09, 0.11, 0.14, 0.17,
                                            0.21, 0.25, 0.30, 0.37, 0.44,
                                            0.53, 0.61, 0.70, 0.78, 0.86,
                                            0.92, 0.96, 0.99, 1.00, 0.98,
                                            0.96, 0.91, 0.86, 0.80, 0.74,
                                            0.69, 0.63, 0.58, 0.53, 0.49,
                                            0.44, 0.41, 0.37, 0.34, 0.32,
                                            0.29, 0.27, 0.25, 0.23, 0.21,
                                            0.19, 0.1, 0.16, 0.15, 0.13,
                                            0.12, 0.11, 0.10 ]
    regionPiedmontDischargeRatio = np.asarray(regionPiedmontDischargeRatioList)
    regionCoastalPlainDischargeList =     [ 0.07, 0.10, 0.14, 0.18, 0.23,
                                            0.29, 0.35, 0.42, 0.50, 0.57,
                                            0.64, 0.71, 0.78, 0.85, 0.90,
                                            0.94, 0.97, 0.99, 1.00, 0.99,
                                            0.98, 0.95, 0.92, 0.88, 0.84,
                                            0.80, 0.76, 0.72, 0.68, 0.63,
                                            0.59, 0.55, 0.51, 0.48, 0.44,
                                            0.40, 0.37, 0.34, 0.31, 0.28,
                                            0.25, 0.23, 0.20, 0.18, 0.17,
                                            0.15, 0.13, 0.11 ]
    regionCoastalPlainDischargeRatio = np.asarray(regionCoastalPlainDischargeList)

    # Determine the region with the largest percentage of drainage
    percentAreas = [regionBlueRidgePercentArea, regionPiedmontPercentArea, regionUpperCoastalPlainPercentArea + regionLowerCoastalPlain1PercentArea + regionLowerCoastalPlain2PercentArea]
    max_percentArea_index = percentAreas.index(max(percentAreas))
    if max_percentArea_index == 0:
        dischargeRatio = regionBlueRidgeDischargeRatio
    elif max_percentArea_index == 1:
        dischargeRatio = regionPiedmontDischargeRatio
    else: 
        dischargeRatio = regionCoastalPlainDischargeRatio

    # Calculate coordinates for the rural flood hydrograph
    timeCoordinates = timeRatio * weightedLTA
    dischargeCoordinates = dischargeRatio * Qp

    # Show the scatter plot of the rural flood hydrograph (for testing)
    #plt.scatter(timeCoordinates, dischargeCoordinates)
    #plt.show()

    # Check limitations of method from Table 15
    warningMessage = "These methods are not applicable to streams where regulation, urbanization, temporary in-channel storage, or overbank detention storage is significant."
    isWarning = False
    if regionBlueRidgePercentArea > 0:
        if A < 2.83 or A > 455:
            isWarning = True
    if regionPiedmontPercentArea > 0:
        if A < 0.52 or A > 444:
            isWarning = True
    if regionUpperCoastalPlainPercentArea > 0:
        if A < 2.92 or A > 401:
            isWarning = True
    if regionLowerCoastalPlain1PercentArea > 0 or regionLowerCoastalPlain2PercentArea > 0:
        if A < 7.67 or A > 401:
            isWarning = True

    if isWarning:
        warningMessage = "One or more of the parameters may be outside the suggested range. Estimates were extrapolated with unknown errors. " + warningMessage

    ## Note: if Runoff Volume is added to the variables returned, check limitations related to runoff volume in Table 15
    return timeCoordinates.tolist(), dischargeCoordinates.tolist(), warningMessage