from fastapi import FastAPI, HTTPException, Response
from fastapi.responses import RedirectResponse
from starlette.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from ChannelWidthWeighting import curveNumber, rainfallData


app = FastAPI(
    title='Channel Width Weighting Services',
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
    x: float
    y: float

    class Config:
        schema_extra = {
            "example": {
                "x": 34.01599,
                "y": -80.99818
            }
        }

class RainfallData(BaseModel):

    # all fields are required
    x: float
    y: float

    class Config:
        schema_extra = {
            "example": {
                "x": 34.01599,
                "y": -80.99818
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
            request_body.x,
            request_body.y
        )
        return {
            "response": response,
        }

    except Exception as e:
        raise HTTPException(status_code = 500, detail =  str(e))

@app.post("/rainfalldata/")
def rainfalldata(request_body: RainfallData, response: Response):

    try: 
        response = rainfallData(
            request_body.x,
            request_body.y
        )
        return {
            "response": response,
        }

    except Exception as e:
        raise HTTPException(status_code = 500, detail =  str(e))