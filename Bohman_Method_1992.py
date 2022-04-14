import requests
import ast
import json

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

    return result_2hr_2yr


# Inputs to Runoff Volume for an Urban Basin
# Region: Piedmont-upper Coastal Plan (Region 3), or lower Coastal Plain (Region 4), or both
# A: Drainage area (sq miles)
# AEP of interest
# Qp: peak flow for the AEP of interest (cubic feet per second)
# L: main channel length (miles)
# S: main channel slope (feet per mile)
# TIA: total impervious area (%)
# Lat/lon to compute the RI2: 2-year 2-hour rainfall amount (inches)

def runoffVolumeUrbanBasinBohman1992(lat, lon, estimateScenariosResponse, AEP, A, L, S, TIA):
    # lat, lon: coordinates of the drainage point
    # estimateScenariosResponse: string response from the https://streamstats.usgs.gov/nssservices/scenarios/estimate?regions=SC,NA endpoint
    # AEP: string to represent annual exceedance probability (AEP) of interest (%); options are "50", "20", "10", "4", "2", "1", "0.5", "0.2"
    # A: drainage area (square miles)
    # L: main channel length (miles)
    # S: main channel slope (feet per mile)
    # TIA: total impervious area (%)

    RI2 = getRI2(lat, lon) # 2-year 2-hour rainfall amount (%)
    LT = 20.2 * ((L/S**0.5)**0.623) * (TIA ** -0.919) * (RI2 ** 1.129) # Average basin lag time (hours)

    if AEP not in ["50", "20", "10", "4", "2", "1", "0.5", "0.2"]:
        raise Exception("AEP value not valid")
    AEP = "UPK" + AEP.replace(".", "_") + "AEP"

    estimateScenariosResponseList = json.loads(estimateScenariosResponse)
    for statisticGroup in estimateScenariosResponseList:
        if statisticGroup['statisticGroupName'] == "Urban Peak-Flow Statistics":
            regressionRegions = statisticGroup['regressionRegions']

    region3FractionArea = 0
    region3Qp = 0
    region4FractionArea = 0
    region4Qp = 0

    for regressionRegion in regressionRegions:
        if regressionRegion['code'] == "GC1585": # Region_3_Urban_2014_5030: Piedmont-upper Coastal Plain
            region3FractionArea = regressionRegion['percentWeight'] / 100.0
            results = regressionRegion['results']
            for result in results:
                if result['code'] == AEP:
                    region3Qp = result['value']
        if regressionRegion['code'] == "GC1586": # Region_4_Urban_2014_5030: lower Coastal Plain
            region4FractionArea = regressionRegion['percentWeight'] / 100.0
            results = regressionRegion['results']
            for result in results:
                if result['code'] == AEP:
                    region4Qp = result['value']
    
    weightedQp = (region3Qp * region3FractionArea) + (region4Qp * region4FractionArea)

    region3VR = 0.001525 * (A ** -1.038) * (region3Qp ** 1.013) * (LT ** 1.030) # Average runoff volume (inches)
    region4VR = 0.001648 * (A ** -1.038) * (region4Qp ** 1.013) * (LT ** 1.030) # Average runoff volume (inches)
    
    weightedVR = (region3VR * region3FractionArea) + (region4VR * region4FractionArea)

    print(weightedQp)
    print(weightedVR)

    return weightedQp, weightedVR

def runoffVolumeUrbanBasinBohman1992V2(lat, lon, region3PercentArea, region4PercentArea, region3AEP, region4AEP, A, L, S, TIA):
    # lat, lon: coordinates of the drainage point (float)
    # region3PercentArea: percent area of the basin that is in Region_3_Urban_2014_5030: Piedmont-upper Coastal Plain (float)
    # region4PercentArea: percent area of the basin that is in Region_4_Urban_2014_5030: lower Coastal Plain (float)
    # region3AEP: flow statistic for the AEP of interest (ex. "UPK50AEP") in Region_3_Urban_2014_5030 (float)
    # region4AEP: flow statistic for the AEP of interest (ex. "UPK50AEP") in Region_4_Urban_2014_5030 (float)
    # A: drainage area (square miles)
    # L: main channel length (miles)
    # S: main channel slope (feet per mile)
    # TIA: total impervious area (%)

    RI2 = getRI2(lat, lon) # 2-year 2-hour rainfall amount (%)
    LT = 20.2 * ((L/S**0.5)**0.623) * (TIA ** -0.919) * (RI2 ** 1.129) # Average basin lag time (hours)

    region3FractionArea = region3PercentArea / 100.0
    region4FractionArea = region4PercentArea / 100.0
    
    weightedQp = (region3AEP * region3FractionArea) + (region4AEP * region4FractionArea)

    region3VR = 0.001525 * (A ** -1.038) * (region3AEP ** 1.013) * (LT ** 1.030) # Average runoff volume (inches)
    region4VR = 0.001648 * (A ** -1.038) * (region4AEP ** 1.013) * (LT ** 1.030) # Average runoff volume (inches)
    
    weightedVR = (region3VR * region3FractionArea) + (region4VR * region4FractionArea)

    print(weightedQp)
    print(weightedVR)

    return weightedQp, weightedVR

def main():
    estimateScenariosResponse = '[{"statisticGroupID":31,"statisticGroupName":"Urban Peak-Flow Statistics","regressionRegions":[{"id":637,"name":"Region_4_Urban_2014_5030","code":"GC1586","description":"","statusID":4,"citationID":33,"percentWeight":100.0,"parameters":[{"id":17990,"name":"Drainage Area","description":"Area that drains to a point on a stream","code":"DRNAREA","unitType":{"id":35,"unit":"square miles","abbr":"mi^2"},"value":0.058,"limits":{"max":53.5,"min":0.1}},{"id":17991,"name":"Percent Impervious NLCD2006","description":"Percentage of impervious area determined from NLCD 2006 impervious dataset","code":"LC06IMP","unitType":{"id":11,"unit":"percent","abbr":"%"},"value":4.13,"limits":{"max":34.8,"min":0.02}},{"id":17992,"name":"24 Hour 50 Year Precipitation","description":"Maximum 24-hour precipitation that occurs on average once in 50 years","code":"I24H50Y","unitType":{"id":36,"unit":"inches","abbr":"in"},"value":8.1,"limits":{"max":10.9,"min":6.51}}],"results":[{"id":0,"name":"Urban 50-percent AEP flood","code":"UPK50AEP","description":"Maximum instantaneous flow affected by urbanization that occurs with a 50% annual exceedance probability","value":15.1,"errors":[],"unit":{"id":44,"unit":"cubic feet per second","abbr":"ft^3/s"},"equation":"26.3*DRNAREA^0.5908*10^(0.0173*LC06IMP)*10^(0.0515*I24H50Y)"},{"id":0,"name":"Urban 20-Percent AEP flood","code":"UPK20AEP","description":"Maximum instantaneous flow affected by urbanization that occurs with a 20% annual exceedance probability","value":26.8,"errors":[],"unit":{"id":44,"unit":"cubic feet per second","abbr":"ft^3/s"},"equation":"40.6*DRNAREA^0.5958*10^(0.0125*LC06IMP)*10^(0.0623*I24H50Y)"},{"id":0,"name":"Urban 10-percent AEP flood","code":"UPK10AEP","description":"Maximum instantaneous flow affected by urbanization that occurs with a 10% annual exceedance probability","value":35.7,"errors":[],"unit":{"id":44,"unit":"cubic feet per second","abbr":"ft^3/s"},"equation":"51.8*DRNAREA^0.6004*10^(0.0101*LC06IMP)*10^(0.0666*I24H50Y)"},{"id":0,"name":"Urban 4-percent AEP flood","code":"UPK4AEP","description":"Maximum instantaneous flow affected by urbanization that occurs with a 4% annual exceedance probability","value":48.0,"errors":[],"unit":{"id":44,"unit":"cubic feet per second","abbr":"ft^3/s"},"equation":"67.1*DRNAREA^0.6067*10^(0.0075*LC06IMP)*10^(0.0708*I24H50Y)"},{"id":0,"name":"Urban 2-percent AEP flood","code":"UPK2AEP","description":"Maximum instantaneous flow affected by urbanization that occurs with a 2% annual exceedance probability","value":57.6,"errors":[],"unit":{"id":44,"unit":"cubic feet per second","abbr":"ft^3/s"},"equation":"78.4*DRNAREA^0.6111*10^(0.0058*LC06IMP)*10^(0.0738*I24H50Y)"},{"id":0,"name":"Urban 1-percent AEP flood","code":"UPK1AEP","description":"Maximum instantaneous flow affected by urbanization that occurs with a 1% annual exceedance probability","value":67.7,"errors":[],"unit":{"id":44,"unit":"cubic feet per second","abbr":"ft^3/s"},"equation":"90.5*DRNAREA^0.6154*10^(0.0043*LC06IMP)*10^(0.0762*I24H50Y)"},{"id":0,"name":"Urban 0.5-percent AEP flood","code":"UPK0_5AEP","description":"Maximum instantaneous flow affected by urbanization that occurs with a 0.5% annual exceedance probability","value":78.3,"errors":[],"unit":{"id":44,"unit":"cubic feet per second","abbr":"ft^3/s"},"equation":"103*DRNAREA^0.6201*10^(0.0029*LC06IMP)*10^(0.0785*I24H50Y)"},{"id":0,"name":"Urban 0.2-percent AEP flood","code":"UPK0_2AEP","description":"Maximum instantaneous flow affected by urbanization that occurs with a 0.2% annual exceedance probability","value":92.2,"errors":[],"unit":{"id":44,"unit":"cubic feet per second","abbr":"ft^3/s"},"equation":"119*DRNAREA^0.6261*10^(0.0012*LC06IMP)*10^(0.0813*I24H50Y)"}],"disclaimer":"One or more of the parameters is outside the suggested range. Estimates were extrapolated with unknown errors. "}],"links":[{"rel":"Citations","href":"https://streamstats.usgs.gov/nssservices/citations?regressionregions=637","method":"GET"}]}]'
    runoffVolumeUrbanBasinBohman1992(33.3946, -80.3474, estimateScenariosResponse, "20", 0.058, 0.503, 20.84, 4.13)

if __name__ == "__main__":
    main()