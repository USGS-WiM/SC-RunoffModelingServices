from fastapi import FastAPI, HTTPException, Response
from fastapi.responses import RedirectResponse
from starlette.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from SC_Synthetic_UH_Method import curveNumber, rainfallData, rainfallDistributionCurve
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
    lat: float
    lon: float

    class Config:
        schema_extra = {
            "example": {
                "lat": 33.3946,
                "lon": -80.3474
            }
        }

class RainfallData(BaseModel):

    # all fields are required
    lat: float
    lon: float

    class Config:
        schema_extra = {
            "example": {
                "lat": 33.3946,
                "lon": -80.3474
            }
        }

class RainfallDistributionCurve(BaseModel):

    # all fields are required
    lat: float
    lon: float

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
    dataSheetFlow: dict
    dataExcessSheetFlow: dict
    P2_24_2: float
    dataShallowConcentratedFlow: dict
    dataChannelizedFlowOpenChannel: list
    dataChannelizedFlowStormSewer: list
    dataChannelizedFlowStormSewerOrOpenChannelUserInputVelocity: list
    class Config:
        schema_extra = {
            "example": {
                "dataSheetFlow": {
                    "Light underbrush": 
                        {
                            "Length": 300,
                            "Overland Slope": 0.33,
                        },
                    "Natural Range": 
                        {
                            "Length": 66,
                            "Overland Slope": 3.33,
                        },
                    "Bermuda grass": 
                        {
                            "Length": 33,
                            "Overland Slope": 0.00,
                        }
                    },
                "dataExcessSheetFlow": {
                    "Short-grass pasture": 
                        {
                            "Slope": 2.00,
                        }
                    },
                "P2_24_2": 3.76,
                "dataShallowConcentratedFlow": {
                    "Nearly bare and untilled (overland flow)": 
                        {
                            "Length": 100,
                            "Slope": 0.50,
                        },
                    "Cultivated straight row crops": 
                        {
                            "Length": 110,
                            "Slope": 1.00,
                        },
                    "Short-grass pasture": 
                        {
                            "Length": 130,
                            "Slope": 2.00,
                        },
                    "Minimum cultivation, contour or strip-cropped, and woodlands": 
                        {
                            "Length": 120,
                            "Slope": 2.00,
                        },
                    "Pavement and small upland gullies": 
                        {
                            "Length": 140,
                            "Slope": 2.00,
                        }
                    },
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

@app.post("/curvenumber/")
def curvenumber(request_body: CurveNumber, response: Response):

    try: 
        response = curveNumber(
            request_body.lat,
            request_body.lon
        )
        return {
            "response": response,
        }

    except Exception as e:
        raise HTTPException(status_code = 500, detail =  str(e))

@app.post("/rainfalldata/")
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
        timeOfConcentration = travelTimeMethodTimeOfConcentration(
            request_body.dataSheetFlow,
            request_body.dataExcessSheetFlow,
            request_body.P2_24_2,
            request_body.dataShallowConcentratedFlow,
            request_body.dataChannelizedFlowOpenChannel,
            request_body.dataChannelizedFlowStormSewer,
            request_body.dataChannelizedFlowStormSewerOrOpenChannelUserInputVelocity
        )
        return {
            "time_of_concentration": timeOfConcentration
        }

    except Exception as e:
        raise HTTPException(status_code = 500, detail =  str(e))