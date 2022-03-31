import requests
import ast
def curveNumber(lat, lon):
    return "Hello, World!"

# Retrieve rainfall data from the NOAA Precipitation Frequency Data Server
# https://hdsc.nws.noaa.gov/hdsc/pfds/pfds_map_cont.html?bkmrk=sc
def rainfallData(lat, lon):

    # Request data from NOAA
    # TODO error handling
    requestURL = "https://hdsc.nws.noaa.gov/cgi-bin/hdsc/new/cgi_readH5.py?lat={}&lon={}".format(lat, lon)
    response = requests.get(requestURL).content.decode('utf-8')
    # print(response)
    # print(response)
    # json_obj = json.loads(response)
    # print(json_obj)
    # print(type(response))
    # print(response.text)
    # print(response.json())
    # print(response.index("quantiles = "))

    # Extract the results from the response
    # print((response[response.find("quantiles = ")+len("quantiles = "):response.rfind("; upper = ")]))
    data = response[response.index("quantiles = ")+len("quantiles = "):response.index("upper")-2]
    # strs = data.replace('[','').split('],')
    # lists = [map(int, s.replace(']','').split(',')) for s in strs]
    # print(data)
    data_lists = ast.literal_eval(data)

    # print(data_lists)
    print([list(map(float, sublist)) for sublist in data_lists])
    # print(type(data_lists))
    # print(json.loads(data))

    results = [list(map(float, sublist)) for sublist in data_lists]

    results_1hr = results[4]
    results_2hr = results[5]
    results_3hr = results[6]
    results_6hr = results[7]
    results_12hr = results[8]
    results_24hr = results[9]

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
    
    P2_24_1 = results_24hr[0]
    P2_24_2 = results_24hr[1]
    P2_24_5 = results_24hr[2]
    P2_24_10 = results_24hr[3]
    P2_24_25 = results_24hr[4]
    P2_24_50 = results_24hr[5]
    P2_24_100 = results_24hr[6]




    # print(response[response.index("quantiles = ")+len("quantiles = "):response.index("upper")-2])

    return P10_1,P10_2,P10_3,P10_6,P10_12,P10_24,P25_1,P25_2,P25_3,P25_6,P25_12,P25_24,P50_1,P50_2,P50_3,P50_6,P50_12,P50_24,P100_1,P100_2,P100_3,P100_6,P100_12,P100_24,P2_24_1,P2_24_2,P2_24_5,P2_24_10,P2_24_25,P2_24_50,P2_24_100 