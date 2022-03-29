import math
from coefficient_table import crossCorrelationCoefficientTable
from hydrologic_region_table import hydrologicRegionsTable

#Returns cross-correlation coefficients between residuals for combinations of different estimation methods
#Values come from Table 6 https://pubs.usgs.gov/sir/2020/5142/sir20205142.pdf
def getCrossCorrelationCoefficient(regressionRegionCode, code1, code2):
    #regressionRegionCode is the string code for the Regression Region, ex. "GC1829"
    #code1, code2 ares the string codes that describes the flow statistic for the estimation methods, ex. "ACPK0_2AEP", which represents "Active Channel Width 0.2-percent AEP flood"

    if code1 == code2:
        raise ValueError("codes must all be unique")

    #Determine hydrologic region that contains this Regression Region
    hydrologicRegionName = None
    for hydrologicRegion, regressionRegionCodes in hydrologicRegionsTable.items():
        if regressionRegionCode in regressionRegionCodes:
            hydrologicRegionName = hydrologicRegion
    if hydrologicRegionName == None:
        raise ValueError("regressionRegionCode not valid")

    #Determine method for each code: "BC" (basin characteristic), "AC" (active channel), "BF" (bankfull width), or "RS" (remote sensing)
    methodCode1 = code1[:2]
    methodCode2 = code2[:2]
    if methodCode1 == "PK":
        methodCode1 = "BC"
    if methodCode2 == "PK":
        methodCode2 = "BC"
    validMethodCodes = ["BC", "AC", "BF", "RS"]
    if methodCode1 not in validMethodCodes or methodCode2 not in validMethodCodes:
        raise ValueError("Method in code not valid")
    if methodCode1 == methodCode2:
        raise ValueError("Method in codes must all be unique")

    #Determine AEP: a string to describe the peak-flow discharge with annual exceedance probability, ex. "Q42.9"
    isDigitsCode1 = [x.isdigit() for x in code1]
    firstDigitIndexCode1 = isDigitsCode1.index(True)
    lastDigitIndexCode1 = len(isDigitsCode1) - isDigitsCode1[::-1].index(True) - 1
    
    isDigitsCode2 = [x.isdigit() for x in code2]
    firstDigitIndexCode2 = isDigitsCode2.index(True)
    lastDigitIndexCode2 = len(isDigitsCode2) - isDigitsCode2[::-1].index(True) - 1

    if code1[firstDigitIndexCode1:lastDigitIndexCode1+1] == code2[firstDigitIndexCode2:lastDigitIndexCode2+1]:
        AEP = "Q" + code1[firstDigitIndexCode1:lastDigitIndexCode1+1].replace("_", ".") 
    else:
        raise ValueError("AEP value must be the same for all flow statistics")

    #Return the coefficient from the table
    try:
        coefficient = crossCorrelationCoefficientTable[hydrologicRegionName][methodCode1 + "," + methodCode2][AEP]
    except:
        try:
            coefficient = crossCorrelationCoefficientTable[hydrologicRegionName][methodCode2 + "," + methodCode1][AEP]
        except:
            raise Exception("Coefficient could not be determined")
    finally: 
        return coefficient

#Check if the weighted estimate is within the bounds of input values
def getWeightingErrorMessage(Z, x1, x2, x3 = None):
    #Z is weighted estimate in log units
    #x1, x2, x3 are input estimates in log units
    if x3 == None:
        x3 = x1
    if ((Z < min(x1, x2, x3)) | (Z > max(x1, x2, x3))):
        return "Weighted value is outside the range of input values. "
    else:
        return None

def weightEst2(x1, x2, SEP1, SEP2, regressionRegionCode, code1, code2):
    #x1, x2 are input estimates
	#SEP1, SEP2 are input SEPs in log units
	#regressionRegionCode is the string code for the Regression Region, ex. "GC1829"
    #code1, code2 are the string codes that describes the flow statistic for the estimation methods, ex. "ACPK0_2AEP", which represents "Active Channel Width 0.2-percent AEP flood"

    x1 = math.log10(x1)
    x2 = math.log10(x2)

    r12 = getCrossCorrelationCoefficient(regressionRegionCode, code1, code2)

    if((SEP1 <= 0) | (SEP2 <= 0)):
        raise ValueError("All SEP values must be greater than zero")

    S12 = r12*(SEP1*SEP2) 

    a1 = (SEP2**2 - S12) / (SEP1**2 + SEP2**2 - 2*S12)
    a2 = 1-a1

    Z = a1*x1 + a2*x2 #EQ 11
    SEPZ = ((SEP1**2*SEP2**2 - S12**2) / (SEP1**2 + SEP2**2 - 2*S12))**0.5 #EQ 12

    warningMessage = getWeightingErrorMessage(Z, x1, x2)

    CI = 1.64 * SEPZ #Confidence interval
    PIL = 10 ** (Z - CI) #Prediction Interval-Lower 
    PIU = 10 ** (Z + CI) #Prediction Interval-Upper
    Z = 10 ** Z #delog the Z value

    return((Z, SEPZ, CI, PIL, PIU, warningMessage)) #Returns weighted estimate Z, associated SEP, and warning messages about results validity


def weightEst3(x1, x2, x3, SEP1, SEP2, SEP3, regressionRegionCode, code1, code2, code3):
    #x1, x2, x3 are input estimates
	#SEP1, SEP2, SEP3 are input SEPs in log units
    #regressionRegionCode is the string code for the Regression Region, ex. "GC1829"
    #code1, code2, code3 are the string codes that describes the flow statistic for the estimation methods, ex. "ACPK0_2AEP", which represents "Active Channel Width 0.2-percent AEP flood"

    x1 = math.log10(x1)
    x2 = math.log10(x2)
    x3 = math.log10(x3)

    r12 = getCrossCorrelationCoefficient(regressionRegionCode, code1, code2)
    r13 = getCrossCorrelationCoefficient(regressionRegionCode, code1, code3)
    r23 = getCrossCorrelationCoefficient(regressionRegionCode, code2, code3)

    if((SEP1 <= 0) | (SEP2 <= 0) | (SEP3 <= 0)):
        raise ValueError("All SEP values must be greater than zero")

    S12 = r12*(SEP1*SEP2) 
    S13 = r13*(SEP1*SEP3)
    S23 = r23*(SEP2*SEP3)

    A = SEP1**2 + SEP3**2 - 2*S13
    B = SEP3**2 + S12 - S13 - S23
    C = SEP2**2 + SEP3**2 - 2*S23

    a1 = (C*(SEP3**2 - S13) - B*(SEP3**2 - S23)) / (A*C - B**2) #EQ 6
    a2 = (A*(SEP3**2 - S23) - B*(SEP3**2 - S13)) / (A*C - B**2) #EQ 7
    a3 = 1 - a1 - a2 #EQ 8

    Z = a1*x1 + a2*x2 + a3*x3 #EQ 5

    SEPZ = ((a1*SEP1)**2 + (a2*SEP2)**2 + (a3*SEP3)**2 + 2*a1*a2*S12 + 2*a1*a3*S13 + 2*a2*a3*S23)**0.5 #EQ 10
    warningMessage = getWeightingErrorMessage(Z, x1, x2, x3)

    CI = 1.64 * SEPZ #Confidence interval
    PIL = 10 ** (Z - CI) #Prediction Interval-Lower 
    PIU = 10 ** (Z + CI) #Prediction Interval-Upper
    Z = 10 ** Z #delog the Z value

    return((Z, SEPZ, CI, PIL, PIU, warningMessage)) #Returns weighted estimate Z, associated SEP, and warning messages about results validity

def weightEst4(x1, x2, x3, x4, SEP1, SEP2, SEP3, SEP4, regressionRegionCode, code1, code2, code3, code4):
    #x1, x2, x3, x4 are input estimates
	#SEP1, SEP2, SEP3, SEP4 are input SEPs in log units
    #regressionRegionCode is the string code for the Regression Region, ex. "GC1829"
    #code1, code2, code3, code4 are the string codes that describes the flow statistic for the estimation methods, ex. "ACPK0_2AEP", which represents "Active Channel Width 0.2-percent AEP flood"

    xValues = [x1, x2, x3, x4]
    SEPValues = [SEP1, SEP2, SEP3, SEP4]
    codeValues = [code1, code2, code3, code4]

    maxSEPIndex = SEPValues.index(max(SEPValues))

    xValues.pop(maxSEPIndex)
    SEPValues.pop(maxSEPIndex)
    codeValues.pop(maxSEPIndex)

    Z, SEPZ, CI, PIL, PIU, warningMessage = weightEst3(*xValues, *SEPValues, regressionRegionCode, *codeValues) #Returns weighted estimate Z, associated SEP, and warning messages about results validity

    if warningMessage is None:
        warningMessage = ""
    warningMessage += "Only 3 estimation methods can be weighted; the 3 estimation methods with lowest SEP values were weighted. "

    return((Z, SEPZ, CI, PIL, PIU, warningMessage)) #Returns weighted estimate Z, associated SEP, and warning messages about results validity