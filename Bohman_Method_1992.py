import requests
import ast

# Retrieve the 2-year 2-hour rainfall amount, in inches, from the the NOAA Precipitation Frequency Data Server
# https://hdsc.nws.noaa.gov/hdsc/pfds/pfds_map_cont.html?bkmrk=sc
def RI2(lat, lon):

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
