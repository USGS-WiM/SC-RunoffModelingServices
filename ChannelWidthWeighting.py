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


    # print(response[response.index("quantiles = ")+len("quantiles = "):response.index("upper")-2])

    return requestURL 