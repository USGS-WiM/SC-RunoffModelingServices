from fastapi import FastAPI, HTTPException, Response
from fastapi.responses import RedirectResponse
from starlette.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from SC_Synthetic_UH_Method import weightedCurveNumber, PRFData, rainfallData, rainfallDistributionCurve, computeSCSyntheticUnitHydrograph, calculateMissingParametersSCSUH
from Bohman_Method_1989 import computeRuralFloodHydrographBohman1989
from Bohman_Method_1992 import getRI2, computeUrbanFloodHydrographBohman1992
from Tc_Calculator import lagTimeMethodTimeOfConcentration, travelTimeMethodTimeOfConcentration

app = FastAPI(
    title='SC Runoff Modeling Services',
    openapi_url='/openapi.json',
    docs_url='/docs'
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


######
##
## Pydantic Schemas
##
######

# These schemas provide format and data type validation
#  of request body inputs, and automated API documentation

class CurveNumber(BaseModel):
    # all fields are required
    lat: float = Field(..., title="latitude", description="latitude coordinate of the drainage point (float)", example="33.3946")
    lon: float = Field(..., title="longitude", description="longitude coordinate of the drainage point (float)", example="-80.3474")
    P24hr: float = Field(..., title="24-hour rainfall depth", description="24-hour rainfall depth for the associated Annual Exceedance Probability (AEP), inches (float)", example="5.74")
    weightingMethod: str = Field(..., title="weighting method", description="weighting method for Standard CN ('runoff' or 'area')", example="runoff")

    class Config:
        schema_extra = {
            "example": {
                "lat": 33.3946,
                "lon": -80.3474,
                "P24hr": 5.74,
                "weightingMethod": "runoff"
            }
        }

class PRF(BaseModel):
    # all fields are required
    lat: float = Field(..., title="latitude", description="latitude coordinate of the drainage point (float)", example="33.3946")
    lon: float = Field(..., title="longitude", description="longitude coordinate of the drainage point (float)", example="-80.3474")

    class Config:
        schema_extra = {
            "example": {
                "lat": 33.3946,
                "lon": -80.3474
            }
        }

class RainfallData(BaseModel):
    # all fields are required
    lat: float = Field(..., title="latitude", description="latitude coordinate of the drainage point (float)", example="33.3946")
    lon: float = Field(..., title="longitude", description="longitude coordinate of the drainage point (float)", example="-80.3474")

    class Config:
        schema_extra = {
            "example": {
                "lat": 33.3946,
                "lon": -80.3474
            }
        }

class RainfallDistributionCurve(BaseModel):
    # all fields are required
    lat: float = Field(..., title="latitude", description="latitude coordinate of the drainage point (float)", example="33.3946")
    lon: float = Field(..., title="longitude", description="longitude coordinate of the drainage point (float)", example="-80.3474")

    class Config:
        schema_extra = {
            "example": {
                "lat": 33.3946,
                "lon": -80.3474
            }
        }

class RuralHydrographBohman1989(BaseModel):
    regionBlueRidgePercentArea: float = Field(0.0, title="Blue Ridge region percent area", description="percent area of the basin that is in the Blue Ridge region (percent, float)", example="10.0")
    regionPiedmontPercentArea: float = Field(0.0, title="Piedmont region percent area", description="percent area of the basin that is in the Piedmont region (percent, float)", example="90.0")
    regionUpperCoastalPlainPercentArea: float = Field(0.0, title="Upper Coastal Plain region percent area", description="percent area of the basin that is in the Upper Coastal Plain region (percent, float)", example="0.0")
    regionLowerCoastalPlain1PercentArea: float = Field(0.0, title="Lower Coastal Plain region 1 percent area", description="percent area of the basin that is in the Lower Coastal Plain region 1 (percent, float)", example="0.0")
    regionLowerCoastalPlain2PercentArea: float = Field(0.0, title="Lower Coastal Plain region 2 percent area", description="percent area of the basin that is in the Lower Coastal Plain region 2 (percent, float)", example="0.0")
    Qp: float = Field(..., title="weighted Qp", description="area-weighted flow statistic for the AEP of interest (cubic feet per second, float)", example="400.0")
    A: float = Field(..., title="basin area", description="total drainage area of the delineated basin (square miles, float)", example="35.0")

    class Config:
        null = 0.0 # null values will become 0.0
        schema_extra = {
            "example": {
                "regionBlueRidgePercentArea": 10.0,
                "regionPiedmontPercentArea": 90.0,
                "regionUpperCoastalPlainPercentArea": 0.0,
                "regionLowerCoastalPlain1PercentArea": 0.0,
                "regionLowerCoastalPlain2PercentArea": 0.0,
                "Qp": 400.0,
                "A": 35.0,
            }
        }

class UrbanHydrographBohman1992(BaseModel):
    lat: float = Field(..., title="latitude", description="latitude coordinate of the drainage point (float)", example="33.3946")
    lon: float = Field(..., title="longitude", description="longitude coordinate of the drainage point (float)", example="-80.3474")
    region3PercentArea: float = Field(0.0, title="region 3 percent area", description="percent area of the basin that is in Region_3_Urban_2014_5030: Piedmont-upper Coastal Plain (percent, float)", example="0.0")
    region4PercentArea: float = Field(0.0, title="region 4 percent area", description="percent area of the basin that is in Region_4_Urban_2014_5030: lower Coastal Plain (percent, float)", example="0.0")
    region3Qp: float = Field(0.0, title="region 3 Qp", description="flow statistic for the AEP of interest (ex. 'UPK50AEP') in Region_3_Urban_2014_5030 (cubic feet per second, float)", example="0.0")
    region4Qp: float = Field(0.0, title="region 4 Qp", description="flow statistic for the AEP of interest (ex. 'UPK50AEP') in Region_4_Urban_2014_5030 (cubic feet per second, float)", example="35.7")
    A: float = Field(..., title="basin area", description="Drainage area of the delineated basin (square miles, float)", example="0.058")
    L: float = Field(..., title="channel length", description="main channel length (miles, float)", example="0.503")
    S: float = Field(..., title="channel slope", description="main channel slope (feet per mile, float)", example="20.84")
    TIA: float = Field(..., title="total impervious area", description="total percent impervious area (percent, float)", example="4.13")

    class Config:
        null = 0.0 # null values will become 0.0
        schema_extra = {
            "example": {
                "lat": 33.3946,
                "lon": -80.3474,
                "region3PercentArea": 0.0,
                "region4PercentArea": 100.0,
                "region3Qp": 0.0,
                "region4Qp": 35.7,
                "A": 0.058,
                "L": 0.503,
                "S": 20.84,
                "TIA": 4.13,
            }
        }

class LagTimeMethodTimeOfConcentration(BaseModel):
    length: float = Field(..., title="length of flowpath", description="length of flow path in watershed, in feet (float)", example="1250")
    slope: float = Field(..., title="slope of flowpath", description="slope of flow path in watershed, in % (float)", example="0.50")
    CN: float = Field(..., title="Curve Number", description="Curve Number of watershed (float)", example="67.3")

    class Config:
        schema_extra = {
            "example": {
                "length": 1250,
                "slope": 0.50,
                "CN": 67.3
            }
        }

class TravelTimeMethodTimeOfConcentration(BaseModel):
    dataSheetFlow: list = Field(..., title="Sheet Flow data", description="data corresponding to Sheet Flow section for Travel Time Method (list)")
    dataExcessSheetFlow: list = Field(..., title="Excess Sheet Flow data", description="data corresponding to Excess Sheet Flow section for Travel Time Method (list)")
    P2_24_2: float = Field(..., title="2-yr 24-hr Precipitation", description="output from rainfallData function; precipitation frequency estimate (inches) for 24-hour storms with an average recurrence interval of 2 years (AEP 50%) (float)", example="3.76")
    dataShallowConcentratedFlow: list = Field(..., title="Shallow Concentrated Flow data", description="data corresponding to Shallow Concentrated Flow section for Travel Time Method (list)")
    dataChannelizedFlowOpenChannel: list = Field(..., title="Channelized Flow - Open Channel data", description="data corresponding to Channelized Flow - Open Channel section for Travel Time Method (list)")
    dataChannelizedFlowStormSewer: list = Field(..., title="Channelized Flow - Storm Sewer data", description="data corresponding to Channelized Flow - Storm Sewer section for Travel Time Method (list)")
    dataChannelizedFlowStormSewerOrOpenChannelUserInputVelocity: list = Field(..., title="Channelized Flow (Storm Sewer and/or Open Channel) - User Input Velocity data", description="data corresponding to Channelized Flow (Storm Sewer and/or Open Channel) - User Input Velocity section for Travel Time Method (list)")
    class Config:
        schema_extra = {
            "example": {
                "dataSheetFlow": [
                        {
                            "Surface": "Light underbrush",
                            "Length": 300,
                            "Overland Slope": 0.33,
                        },
                        {
                            "Surface": "Natural Range",
                            "Length": 66,
                            "Overland Slope": 3.33,
                        },
                        {
                            "Surface": "Bermuda grass",
                            "Length": 33,
                            "Overland Slope": 0.00,
                        }
                ],
                "dataExcessSheetFlow": [
                        {
                            "Surface": "Short-grass pasture",
                            "Slope": 2.00,
                        }
                ],
                "P2_24_2": 3.76,
                "dataShallowConcentratedFlow": [
                        {
                            "Shallow Flow Type": "Nearly bare and untilled (overland flow)",
                            "Length": 100,
                            "Slope": 0.50,
                        },
                        {
                            "Shallow Flow Type": "Cultivated straight row crops",
                            "Length": 110,
                            "Slope": 1.00,
                        },
                        {
                            "Shallow Flow Type": "Short-grass pasture",
                            "Length": 130,
                            "Slope": 2.00,
                        },
                        {
                            "Shallow Flow Type": "Minimum cultivation, contour or strip-cropped, and woodlands",
                            "Length": 120,
                            "Slope": 2.00,
                        },
                        {
                            "Shallow Flow Type": "Pavement and small upland gullies",
                            "Length": 140,
                            "Slope": 2.00,
                        }
                    ],
                "dataChannelizedFlowOpenChannel": [
                        {
                            "Base Width": 3.0,
                            "Front Slope": 2.0,
                            "Back Slope": 3.0,
                            "Channel Depth": 2.0,
                            "Length": 1500,
                            "Channel Bed Slope": 0.25,
                            "Manning n-value": 0.035,
                        },
                        {
                            "Base Width": 3.0,
                            "Front Slope": 2.0,
                            "Back Slope": 3.0,
                            "Channel Depth": 2.0,
                            "Length": 1500,
                            "Channel Bed Slope": 0.25,
                            "Manning n-value": 0.035,
                        }
                    ],
                "dataChannelizedFlowStormSewer": [
                        {
                            "Pipe Material": "CMP",
                            "Diameter": 36,
                            "Length": 300,
                            "Slope": 0.50
                        },
                        {
                            "Pipe Material": "PVC",
                            "Diameter": 24,
                            "Length": 300,
                            "Slope": 0.5
                        },
                        {
                            "Pipe Material": "Concrete",
                            "Diameter": 30,
                            "Length": 300,
                            "Slope": 0.5
                        },
                        {
                            "Pipe Material": "Steel",
                            "Diameter": 36,
                            "Length": 300,
                            "Slope": 0.5
                        }
                    ],
                "dataChannelizedFlowStormSewerOrOpenChannelUserInputVelocity": [
                        {
                            "Length": 300,
                            "Velocity": 2.00,
                        },
                        {
                            "Length": 300,
                            "Velocity": 3.00,
                        },
                        {
                            "Length": 300,
                            "Velocity": 4.00,
                        }
                    ]
            }
        }

class SCSyntheticUnitHydrograph(BaseModel):
    lat: float = Field(..., title="latitude", description="latitude coordinate of the drainage point (float)", example="33.3946")
    lon: float = Field(..., title="longitude", description="longitude coordinate of the drainage point (float)", example="-80.3474")
    AEP: float = Field(..., title="Annual Exceedance Probability", description="Annual Exceedance Probability (%); options are 10, 4, 2, 1, which correspond to 10-yr, 25-yr, 50-yr, and 100-yr storms (int)", example="4")
    CNModificationMethod: str = Field(..., title="Curve Number Modification Method", description="method used to modify the Curve Number; options are 'McCuen' or 'Merkel' (string)", example="Merkel")
    Area: float = Field(..., title="Area", description="drainage area of delineated basin (float)", example="100.0")
    Tc: float = Field(..., title="Time of Concentration", description="Time of Concentration as computed by Travel Time Method or Lag Time Equation (float)", example="64.5")
    RainfallDistributionCurve: str = Field(..., title="Rainfall Distribution Curve", description="rainfall distribution curve letter; options are 'II', 'III', 'A', 'B', 'C', 'D' (string)", example="II")
    PRF: float = Field(..., title="Peak Rate Factor (float)", description="", example="240")
    CN: float = Field(..., title="Curve Number", description="weighted Curve Number (float)", example="67.3")
    S: float = Field(..., title="Watershed Retention", description="watershed Retention, S (float)", example="4.86")
    Ia: float = Field(..., title="Initial Abstraction", description="Initial Abstraction, Ia (float)", example="0.97")

    class Config:
        schema_extra = {
            "example": {
                "lat": 33.3946,
                "lon": -80.3474,
                "AEP": 4,
                "CNModificationMethod": "Merkel",
                "Area": 100.0,
                "Tc": 64.5,
                "RainfallDistributionCurve": "II",
                "PRF": 240,
                "CN": 67.3,
                "S": 4.86,
                "Ia": 0.97
            }
        }

class CalculateMissingParametersSCSUH(BaseModel):
    lat: float = Field(..., title="latitude", description="latitude coordinate of the drainage point (float)", example="33.3946")
    lon: float = Field(..., title="longitude", description="longitude coordinate of the drainage point (float)", example="-80.3474")
    AEP: float = Field(..., title="Annual Exceedance Probability", description="Annual Exceedance Probability (%); options are 10, 4, 2, 1, which correspond to 10-yr, 25-yr, 50-yr, and 100-yr storms (int)", example="4")
    curveNumberMethod: str = Field(..., title="weighting method", description="weighting method for Standard CN ('runoff' or 'area')", example="runoff")
    TcMethod: str = Field(default=None, title="time of concentration method", description="time of concentration ('lagtime' or 'traveltime')", example="traveltime")
    length: float = Field(default=None, title="length of flowpath", description="length of flow path in watershed, in feet (float)", example="1250")
    slope: float = Field(default=None, title="slope of flowpath", description="slope of flow path in watershed, in % (float)", example="0.50")
    dataSheetFlow: list = Field(default=None, title="Sheet Flow data", description="data corresponding to Sheet Flow section for Travel Time Method (list)")
    dataExcessSheetFlow: list = Field(default=None, title="Excess Sheet Flow data", description="data corresponding to Excess Sheet Flow section for Travel Time Method (list)")
    dataShallowConcentratedFlow: list = Field(default=None, title="Shallow Concentrated Flow data", description="data corresponding to Shallow Concentrated Flow section for Travel Time Method (list)")
    dataChannelizedFlowOpenChannel: list = Field(default=None, title="Channelized Flow - Open Channel data", description="data corresponding to Channelized Flow - Open Channel section for Travel Time Method (list)")
    dataChannelizedFlowStormSewer: list = Field(default=None, title="Channelized Flow - Storm Sewer data", description="data corresponding to Channelized Flow - Storm Sewer section for Travel Time Method (list)")
    dataChannelizedFlowStormSewerOrOpenChannelUserInputVelocity: list = Field(default=None, title="Channelized Flow (Storm Sewer and/or Open Channel) - User Input Velocity data", description="data corresponding to Channelized Flow (Storm Sewer and/or Open Channel) - User Input Velocity section for Travel Time Method (list)")

    class Config:
        schema_extra = {
            "example": {
                "lat": 33.3946,
                "lon": -80.3474,
                "AEP": 4,
                "curveNumberMethod": "runoff",
                "TcMethod": "traveltime",
                "dataSheetFlow": [
                        {
                            "Surface": "Light underbrush",
                            "Length": 300,
                            "Overland Slope": 0.33,
                        },
                        {
                            "Surface": "Natural Range",
                            "Length": 66,
                            "Overland Slope": 3.33,
                        },
                        {
                            "Surface": "Bermuda grass",
                            "Length": 33,
                            "Overland Slope": 0.00,
                        }
                ],
                "dataExcessSheetFlow": [
                        {
                            "Surface": "Short-grass pasture",
                            "Slope": 2.00,
                        }
                ],
                "dataShallowConcentratedFlow": [
                        {
                            "Shallow Flow Type": "Nearly bare and untilled (overland flow)",
                            "Length": 100,
                            "Slope": 0.50,
                        },
                        {
                            "Shallow Flow Type": "Cultivated straight row crops",
                            "Length": 110,
                            "Slope": 1.00,
                        },
                        {
                            "Shallow Flow Type": "Short-grass pasture",
                            "Length": 130,
                            "Slope": 2.00,
                        },
                        {
                            "Shallow Flow Type": "Minimum cultivation, contour or strip-cropped, and woodlands",
                            "Length": 120,
                            "Slope": 2.00,
                        },
                        {
                            "Shallow Flow Type": "Pavement and small upland gullies",
                            "Length": 140,
                            "Slope": 2.00,
                        }
                    ],
                "dataChannelizedFlowOpenChannel": [
                        {
                            "Base Width": 3.0,
                            "Front Slope": 2.0,
                            "Back Slope": 3.0,
                            "Channel Depth": 2.0,
                            "Length": 1500,
                            "Channel Bed Slope": 0.25,
                            "Manning n-value": 0.035,
                        },
                        {
                            "Base Width": 3.0,
                            "Front Slope": 2.0,
                            "Back Slope": 3.0,
                            "Channel Depth": 2.0,
                            "Length": 1500,
                            "Channel Bed Slope": 0.25,
                            "Manning n-value": 0.035,
                        }
                    ],
                "dataChannelizedFlowStormSewer": [
                        {
                            "Pipe Material": "CMP",
                            "Diameter": 36,
                            "Length": 300,
                            "Slope": 0.50
                        },
                        {
                            "Pipe Material": "PVC",
                            "Diameter": 24,
                            "Length": 300,
                            "Slope": 0.5
                        },
                        {
                            "Pipe Material": "Concrete",
                            "Diameter": 30,
                            "Length": 300,
                            "Slope": 0.5
                        },
                        {
                            "Pipe Material": "Steel",
                            "Diameter": 36,
                            "Length": 300,
                            "Slope": 0.5
                        }
                    ],
                "dataChannelizedFlowStormSewerOrOpenChannelUserInputVelocity": [
                        {
                            "Length": 300,
                            "Velocity": 2.00,
                        },
                        {
                            "Length": 300,
                            "Velocity": 3.00,
                        },
                        {
                            "Length": 300,
                            "Velocity": 4.00,
                        }
                    ]
            }
        }
######
##
## API Endpoints
##
######


# redirect root and /settings.SERVICE_NAME to the docs
@app.get("/", include_in_schema=False)
def docs_redirect_root():
    return RedirectResponse(url=app.docs_url)

@app.post("/weightedcurvenumber/")
def weighted(request_body: CurveNumber, response: Response):

    try: 
        runoff_weighted_CN, WS_retention_S, initial_abstraction_Ia = weightedCurveNumber(
            request_body.lat,
            request_body.lon,
            request_body.P24hr,
            request_body.weightingMethod
        )
        return {
            "CN": runoff_weighted_CN,
            "S": WS_retention_S,
            "Ia": initial_abstraction_Ia
        }

    except Exception as e:
        raise HTTPException(status_code = 500, detail =  str(e))

@app.post("/prf/")
def prfdata(request_body: PRF, response: Response):

    try: 
        PRF = PRFData(
            request_body.lat,
            request_body.lon
        )
        return {
            "PRF": PRF
        }

    except Exception as e:
        raise HTTPException(status_code = 500, detail =  str(e))


@app.post("/rainfall/")
def rainfalldata(request_body: RainfallData, response: Response):

    try: 
        P10_1,P10_2,P10_3,P10_6,P10_12,P10_24,P25_1,P25_2,P25_3,P25_6,P25_12,P25_24,P50_1,P50_2,P50_3,P50_6,P50_12,P50_24,P100_1,P100_2,P100_3,P100_6,P100_12,P100_24,P2_24_1,P2_24_2,P2_24_5,P2_24_10,P2_24_25,P2_24_50,P2_24_100 = rainfallData(
            request_body.lat,
            request_body.lon
        )

        return {
            "P10_1": P10_1, 
            "P10_2": P10_2,
            "P10_3": P10_3,
            "P10_6": P10_6,
            "P10_12": P10_12,
            "P10_24": P10_24,
            "P25_1": P25_1,
            "P25_2": P25_2,
            "P25_3": P25_3,
            "P25_6": P25_6,
            "P25_12": P25_12,
            "P25_24": P25_24,
            "P50_1": P50_1,
            "P50_2": P50_2,
            "P50_3": P50_3,
            "P50_6": P50_6,
            "P50_12": P50_12,
            "P50_24" : P50_24,
            "P100_1": P100_1,
            "P100_2": P100_2,
            "P100_3": P100_3,
            "P100_6": P100_6,
            "P100_12": P100_12,
            "P100_24": P100_24,
            "P2_24_1": P2_24_1,
            "P2_24_2": P2_24_2,
            "P2_24_5": P2_24_5,
            "P2_24_10": P2_24_10,
            "P2_24_25": P2_24_25,
            "P2_24_50": P2_24_50,
            "P2_24_100": P2_24_100
        }

    except Exception as e:
        raise HTTPException(status_code = 500, detail =  str(e))

@app.post("/rainfalldistributioncurve/")
def rainfalldistributioncurve(request_body: RainfallDistributionCurve, response: Response):

    try: 
        rainfall_distribution_curve_letter, rainfall_distribution_curve_number = rainfallDistributionCurve(
            request_body.lat,
            request_body.lon
        )
        return {
            "rainfall_distribution_curve_letter": rainfall_distribution_curve_letter,
            "rainfall_distribution_curve_number": rainfall_distribution_curve_number,
        }

    except Exception as e:
        raise HTTPException(status_code = 500, detail =  str(e))

@app.post("/RI2/")
def ri2(request_body: RainfallData, response: Response):

    try: 
        ri2 = getRI2(
            request_body.lat,
            request_body.lon
        )

        return {
            "RI2": ri2
        }

    except Exception as e:
        raise HTTPException(status_code = 500, detail =  str(e))

@app.post("/ruralhydrographbohman1989/")
def ruralhydrographbohman1989(request_body: RuralHydrographBohman1989, response: Response):

    try: 
        weightedVR, timeCoordinates, dischargeCoordinates, warningMessage = computeRuralFloodHydrographBohman1989(
            request_body.regionBlueRidgePercentArea,
            request_body.regionPiedmontPercentArea,
            request_body.regionUpperCoastalPlainPercentArea,
            request_body.regionLowerCoastalPlain1PercentArea,
            request_body.regionLowerCoastalPlain2PercentArea,
            request_body.Qp,
            request_body.A,
        )
        if warningMessage is not None:
            response.headers["X-warning"] = warningMessage
            response.headers["Access-Control-Expose-Headers"] = "X-warning"
        return {
            "weighted_runoff_volume": weightedVR,
            "time_coordinates": timeCoordinates,
            "discharge_coordinates": dischargeCoordinates
        }

    except Exception as e:
        raise HTTPException(status_code = 500, detail =  str(e))
        
@app.post("/urbanhydrographbohman1992/")
def urbanhydrographbohman1992(request_body: UrbanHydrographBohman1992, response: Response):

    try: 
        weightedVR, timeCoordinates, dischargeCoordinates, warningMessage = computeUrbanFloodHydrographBohman1992(
            request_body.lat,
            request_body.lon,
            request_body.region3PercentArea,
            request_body.region4PercentArea,
            request_body.region3Qp,
            request_body.region4Qp,
            request_body.A,
            request_body.L,
            request_body.S,
            request_body.TIA
        )
        if warningMessage is not None:
            response.headers["X-warning"] = warningMessage
            response.headers["Access-Control-Expose-Headers"] = "X-warning"
        return {
            "weighted_runoff_volume": weightedVR,
            "time_coordinates": timeCoordinates,
            "discharge_coordinates": dischargeCoordinates
        }

    except Exception as e:
        raise HTTPException(status_code = 500, detail =  str(e))

@app.post("/lagtimetc/")
def lagtimetc(request_body: LagTimeMethodTimeOfConcentration, response: Response):

    try: 
        timeOfConcentration = lagTimeMethodTimeOfConcentration(
            request_body.length,
            request_body.slope,
            request_body.CN
        )
        return {
            "time_of_concentration": timeOfConcentration
        }

    except Exception as e:
        raise HTTPException(status_code = 500, detail =  str(e))

@app.post("/traveltimetc/")
def traveltimetc(request_body: TravelTimeMethodTimeOfConcentration, response: Response):

    try: 
        timeOfConcentration, warningMessage = travelTimeMethodTimeOfConcentration(
            request_body.dataSheetFlow,
            request_body.dataExcessSheetFlow,
            request_body.P2_24_2,
            request_body.dataShallowConcentratedFlow,
            request_body.dataChannelizedFlowOpenChannel,
            request_body.dataChannelizedFlowStormSewer,
            request_body.dataChannelizedFlowStormSewerOrOpenChannelUserInputVelocity
        )
        if warningMessage is not None:
            response.headers["X-warning"] = warningMessage
            response.headers["Access-Control-Expose-Headers"] = "X-warning"
        return {
            "time_of_concentration": timeOfConcentration
        }

    except Exception as e:
        raise HTTPException(status_code = 500, detail =  str(e))

@app.post("/scsyntheticunithydrograph/")
def scsyntheticunithydrograph(request_body: SCSyntheticUnitHydrograph, response: Response):

    try: 
        watershed_data, unit_hydrograph_data, runoff_results_table, hydrograph_ordinates_table = computeSCSyntheticUnitHydrograph(
            request_body.lat,
            request_body.lon,
            request_body.AEP,
            request_body.CNModificationMethod,
            request_body.Area,
            request_body.Tc,
            request_body.RainfallDistributionCurve,
            request_body.PRF,
            request_body.CN,
            request_body.S,
            request_body.Ia
        )
        return {
            "watershed_data": watershed_data,
            "unit_hydrograph_data": unit_hydrograph_data,
            "runoff_results_table": runoff_results_table,
            "hydrograph_ordinates_table": hydrograph_ordinates_table
        }

    except Exception as e:
        raise HTTPException(status_code = 500, detail =  str(e))

@app.post("/calculatemissingparametersSCSUH /")
def calculatemissingparametersSCSUH(request_body: CalculateMissingParametersSCSUH, response: Response):

    try: 
        rainfall_distribution_curve_letter, Tc, PRF, CN, S, Ia = calculateMissingParametersSCSUH(
            request_body.lat,
            request_body.lon,
            request_body.AEP,
            request_body.curveNumberMethod,
            request_body.TcMethod,        
            request_body.length,
            request_body.slope,      
            request_body.dataSheetFlow,
            request_body.dataExcessSheetFlow,
            request_body.dataShallowConcentratedFlow,
            request_body.dataChannelizedFlowOpenChannel,
            request_body.dataChannelizedFlowStormSewer,
            request_body.dataChannelizedFlowStormSewerOrOpenChannelUserInputVelocity,
        )
        return {
            "rainfall_distribution_curve_letter": rainfall_distribution_curve_letter,
            "time_of_concentration": Tc,
            "peak_rate_factor": PRF,
            "curve_number": CN,
            "S": S,
            "Ia": Ia
        }

    except Exception as e:
        raise HTTPException(status_code = 500, detail =  str(e))
