# Corresponds to "Tc Calculator" sheet in SCDOT SC Synthetic UH Method Excel workbook
# This file contains functions to compute time of concentration (Tc)
# There are two methods to compute time of concentration (Tc): Lag Time Equation and Travel Time Method

import math

## Lag Time Equation
# Time of Concentration (Tc) as computed by Lag Time Equation
def lagTimeMethodTimeOfConcentration(length, slope, CN):
    # length: flow path length in feet
    # slope: flow path slope in %
    # CN: Curve Number

    S = 1000 / CN - 10 # Watershed Retention
    lag_time = 60*((length**0.8)*(S+1)**0.7)/(1900*(math.sqrt(slope))) # minutes
    time_of_concentration = 1.67 * lag_time # minutes

    return time_of_concentration

## Travel Time Method

# Key is "Sheet Flow Surface"
# Value is "Manning's N"
sheetFlowSurfaceManningsNTable = {
    "Smooth asphalt": 0.011,
    "Smooth concrete": 0.012,
    "Fallow (no residue)": 0.050,
    "Short grass prairie": 0.150,
    "Dense grasses": 0.240,
    "Bermuda grass": 0.410,
    "Light underbrush": 0.400,
    "Dense underbrush": 0.800,
    "Cultivated Soil with Residue cover <=20%": 0.060,
    "Cultivated Soil with Residue cover >=20%": 0.170,
    "Natural Range": 0.130
}

# Key is "Shallow Flow Types"
shallowFlowTypesTable = {
    "Pavement and small upland gullies": 
        {
            "Depth": 0.2,
            "Manning's N": 0.025,
            "Velocity Constant": 20.328
        },
    "Grassed waterways": 
        {
            "Depth": 0.4,
            "Manning's N": 0.05,
            "Velocity Constant": 16.135 
        },
    "Nearly bare and untilled (overland flow)": 
        {
            "Depth": 0.2,
            "Manning's N": 0.051,
            "Velocity Constant": 9.965 
        },
    "Cultivated straight row crops": 
        {
            "Depth": 0.2,
            "Manning's N": 0.058,
            "Velocity Constant": 8.762
        },
    "Short-grass pasture": 
        {
            "Depth": 0.2,
            "Manning's N": 0.073,
            "Velocity Constant": 6.962
        },
    "Minimum cultivation, contour or strip-cropped, and woodlands": 
        {
            "Depth": 0.2,
            "Manning's N": 0.101,
            "Velocity Constant": 5.032 
        },
    "Forest with heavy ground litter and hay meadows": 
        {
            "Depth": 0.2,
            "Manning's N": 0.202,
            "Velocity Constant": 2.516
        }
}

# Key is "Storm Sewer Material"
# Value is "Manning's N"
stormSewerMaterialManningsNTable = {
    "Aluminum": 0.024,
    "CMP": 0.024,
    "Concrete": 0.013,
    "Corrugated HDPE": 0.02,
    "PVC": 0.01,
    "Steel": 0.013
}

def calculateSheetFlowTravelTime(dataSheetFlow, dataExcessSheetFlow, P2_24_2):
    # dataSheetFlow (example): {
    #    "Short grass prairie": 
    #       {
    #         "Length": 250,
    #         "Overland Slope": 2.00,
    #       },
    #    "Smooth asphalt": 
    #       {
    #         "Length": 500,
    #         "Overland Slope": 1.00,
    #       }
    # }
    # dataExcessSheetFlow (example): {
    #    "Pavement and small upland gullies": 
    #       {
    #         "Slope": 2.00,
    #       }
    #    }
    
    # P2_24_2: output from rainfallData function; precipitation frequency estimate (inches) for 24-hour storms with an average recurrence interval of 2 years (AEP 50%)
    travel_time_sheet_flow = 0.0 # minutes
    travel_time_excess_sheet_flow = 0.0 # minutes
    total_length = 0.0 # feet
    total_corrected_length = 0.0 # feet
    for surface in dataSheetFlow:
        mannings_n = sheetFlowSurfaceManningsNTable[surface]
        limit = (100.0*math.sqrt(dataSheetFlow[surface]["Overland Slope"]/100.0))/mannings_n # feet
        total_length += dataSheetFlow[surface]["Length"]
        if dataSheetFlow[surface]["Length"] > limit: 
            corrected_length = limit # feet
        else:
            corrected_length = dataSheetFlow[surface]["Length"] # feet
        total_corrected_length += corrected_length # feet
        travel_time_sheet_flow += (0.42 / math.sqrt(P2_24_2)) * (mannings_n*corrected_length/math.sqrt((max(0.0001,dataSheetFlow[surface]["Overland Slope"])/100.0))**0.8) # minutes
    for surface in dataExcessSheetFlow:
        length = max(0,total_length-total_corrected_length) # feet
        velocity_constant = shallowFlowTypesTable[surface]["Velocity Constant"]
        velocity = velocity_constant * math.sqrt(dataExcessSheetFlow[surface]["Slope"]/100) # feet per second
        travel_time_excess_sheet_flow += length / velocity / 60.0 # minutes
    return travel_time_sheet_flow + travel_time_excess_sheet_flow

def shallowConcentratedFlowTravelTime(data):
    # data (example): {
    #    "Short-grass pasture": 
    #       {
    #         "Length": 250,
    #         "Slope": 2.00,
    #       },
    #    "Minimum cultivation, contour or strip-cropped, and woodlands": 
    #       {
    #         "Length": 500,
    #         "Slope": 1.00,
    #       }
    # }
    travel_time = 0.0
    for surface in data:
        velocity_constant = shallowFlowTypesTable[surface]["Velocity Constant"]
        velocity = velocity_constant * math.sqrt(data[surface]["Slope"]/100) # feet per second
        travel_time += data[surface]["Length"] / velocity / 60.0 # minutes
    return travel_time  

def channelizedFlowOpenChannelTravelTime(data):
    # data (example): [
    #   {
    #       "Base Width": 3.0,
    #       "Front Slope": 2.0,
    #       "Black Slope": 3.0,
    #       "Channel Depth": 2.0,
    #       "Length": 100,
    #       "Channel Bed Slope": 0.25,
    #       "Manning n-value": 0.035,
    #   },
    #   {
    #       "Base Width": 3.0,
    #       "Front Slope": 2.0,
    #       "Black Slope": 3.0,
    #       "Channel Depth": 2.0,
    #       "Length": 200,
    #       "Channel Bed Slope": 0.25,
    #       "Manning n-value": 0.035,
    #   }
    # ]
    travel_time = 0.0
    for channel in data:
        base_width = channel["Base Width"]
        front_slope = channel["Front Slope"]
        back_slope = channel["Back Slope"]
        channel_depth = channel["Channel Depth"]
        length = channel["Length"]
        channel_bed_slope = channel["Channel Bed Slope"]
        manning_n_value = channel["Manning n-value"]
        wetted_perimeter = (math.sqrt(((channel_depth**2)+((channel_depth*front_slope)**2))))+(math.sqrt(((channel_depth**2)+((channel_depth*back_slope)^2))))+base_width # feet
        cross_sectional_area = ((0.5*channel_depth**2)*(front_slope+back_slope))+(base_width*channel_depth) # square feet
        stream_flow = (1.49/manning_n_value)*cross_sectional_area*((cross_sectional_area/(base_width+2*channel_depth*math.sqrt(1+front_slope*back_slope)))**(2/3))*math.sqrt(channel_bed_slope/100) # cubic feet per second
        velocity = stream_flow / cross_sectional_area # feet per second
        travel_time += length / velocity / 60.0 # minutes
    return travel_time 

def channelizedFlowStormSewerTravelTime(data):
    # data (example): [
    #   {
    #       "Pipe Material": "Concrete",
    #       "Diameter": 30,
    #       "Length": 1500,
    #       "Slope": 1.0
    #   },
    #   {
    #       "Pipe Material": "PVC",
    #       "Diameter": 24,
    #       "Length": 1200,
    #       "Slope": 0.5
    #   }
    # ]
    travel_time = 0.0
    for pipe in data:
        diameter = pipe["Diameter"]
        length = pipe["Length"]
        slope = pipe["Slope"]
        manning_n_value = stormSewerMaterialManningsNTable[pipe["Pipe Material"]]
        pipe_flow = (1.486/manning_n_value)*3.14159*(((diameter/12)**2)/4)*(((diameter/12)/4)**(2/3))*math.sqrt(slope/100) # cubic feet per second
        cross_sectional_area = 3.14159*(((diameter/12)*2)/4) # square feet
        velocity = pipe_flow / cross_sectional_area # feet per second
        travel_time += length / velocity / 60.0
    return travel_time
    
def channelizedFlowStormSewerOrOpenChannelUserInputVelocityTravelTime(data):
    # data (example): [
    #   {
    #       "Length": 1000,
    #       "Velocity": 2.00,
    #   },
    #   {
    #       "Length": 1500,
    #       "Velocity": 3.00,
    #   }
    # ]
    travel_time = 0.0
    for pipe in data:
        length = pipe["Length"]
        velocity = pipe["Velocity"]
        travel_time += length / velocity / 60.0
    return travel_time

# Time of Concentration (Tc) as computed by Travel Time Method
def travelTimeMethodTimeOfConcentration(dataSheetFlow, dataExcessSheetFlow, P2_24_2,
                                        dataShallowConcentratedFlow,
                                        dataChannelizedFlowOpenChannel,
                                        dataChannelizedFlowStormSewer,
                                        dataChannelizedFlowStormSewerOrOpenChannelUserInputVelocity):
    time_of_concentration = calculateSheetFlowTravelTime(dataSheetFlow, dataExcessSheetFlow, P2_24_2) + \
        shallowConcentratedFlowTravelTime(dataShallowConcentratedFlow) + \
        channelizedFlowOpenChannelTravelTime(dataChannelizedFlowOpenChannel) + \
        channelizedFlowStormSewerTravelTime(dataChannelizedFlowStormSewer) + \
        channelizedFlowStormSewerOrOpenChannelUserInputVelocityTravelTime(dataChannelizedFlowStormSewerOrOpenChannelUserInputVelocity)
    return time_of_concentration

