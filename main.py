from fastapi import FastAPI, HTTPException, Response
from fastapi.responses import RedirectResponse
from starlette.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from SC_Synthetic_UH_Method import curveNumber, rainfallData, rainfallDistributionCurve
from Bohman_Method_1992 import RI2

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

    regionBlueRidgePercentArea: float = Field(0.0, title="Blue Ridge region percent area", description="percent area of the basin that is in the Blue Ridge region (percent, float)", example="0.0")
    regionPiedmontPercentArea: float = Field(0.0, title="Piedmont region percent area", description="percent area of the basin that is in the Piedmont region (percent, float)", example="0.0")
    regionUpperCoastalPlainPercentArea: float = Field(0.0, title="Upper Coastal Plain region percent area", description="percent area of the basin that is in the Upper Coastal Plain region (percent, float)", example="0.0")
    regionLowerCoastalPlain1PercentArea: float = Field(0.0, title="Lower Coastal Plain region 1 percent area", description="percent area of the basin that is in the Lower Coastal Plain region 1 (percent, float)", example="0.0")
    regionLowerCoastalPlain2PercentArea: float = Field(0.0, title="Lower Coastal Plain region 2 percent area", description="percent area of the basin that is in the Lower Coastal Plain region 2 (percent, float)", example="0.0")
    Qp: float = Field(0.0, title="weighted Qp", description="flow statistic for the AEP of interest (ex. 'UPK50AEP') in Region_3_Urban_2014_5030 (cubic feet per second, float)", example="0.0")
    region4Qp: float = Field(0.0, title="region 4 Qp", description="area-weighted flow statistic for the AEP of interest (cubic feet per second, float)", example="35.7")
    A: float = Field(..., title="basin area", description="total drainage area of the delineated basin (square miles, float)", example="0.058")

    class Config:
        null = 0.0 # null values will become 0.0
        schema_extra = {
            "example": {
                "regionBlueRidgePercentArea": 0.0,
                "regionPiedmontPercentArea": 0.0,
                "regionUpperCoastalPlainPercentArea": 0.0,
                "regionLowerCoastalPlain1PercentArea": 0.0,
                "regionLowerCoastalPlain2PercentArea": 0.0,
                "Qp": 0.0,
                "A": 0.058,
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
        ri2 = RI2(
            request_body.lat,
            request_body.lon
        )

        return {
            "RI2": ri2
        }

    except Exception as e:
        raise HTTPException(status_code = 500, detail =  str(e))
