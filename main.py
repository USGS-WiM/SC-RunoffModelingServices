from fastapi import FastAPI, HTTPException, Response
from starlette.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from SC_Synthetic_UH_Method import weightedCurveNumber, PRFData, rainfallData, rainfallDistributionCurve, computeSCSyntheticUnitHydrograph, calculateMissingParametersSCSUH
from Bohman_Method_1989 import computeRuralFloodHydrographBohman1989
from Bohman_Method_1992 import getRI2, computeUrbanFloodHydrographBohman1992
from Tc_Calculator import lagTimeMethodTimeOfConcentration, travelTimeMethodTimeOfConcentration
from Storm_Ponds import calcStormPonds

app = FastAPI(
    title='SC Runoff Modeling Services',
    #root_path='/local/scrunoffservices'
    # To run locally use
    root_path=''
    # To run in production use
    #    root_path='/local/scrunoffservices'
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
    watershedFeatures: list = Field(..., title="watershed features", description="list of features of delineated watershed returned by StreamStatsServices")
    P24hr: float = Field(..., title="24-hour rainfall depth", description="24-hour rainfall depth for the associated Annual Exceedance Probability (AEP), inches (float)", example="5.74")
    weightingMethod: str = Field(..., title="weighting method", description="weighting method for Standard CN ('runoff' or 'area')", example="runoff")

    class Config:
        schema_extra = {
            "example": {
                "watershedFeatures": [{"type":"Feature","geometry":{"type":"Polygon","coordinates":[[[-80.34840490286565,33.39422261175201],[-80.34850320525864,33.39422313161143],[-80.34850196585636,33.3943880487428],[-80.34860026843751,33.394388568524725],[-80.34860088804575,33.394306109958826],[-80.34879749302459,33.39430714928652],[-80.34879687360336,33.394389607853384],[-80.34889517618805,33.39439012740008],[-80.34889455685915,33.39447258596689],[-80.34909116221907,33.394473624825906],[-80.34909178136097,33.39439116625811],[-80.3491900839492,33.39439168556949],[-80.34918946490079,33.39447414413778],[-80.34928776758372,33.39447466337122],[-80.34928714862761,33.394557121939464],[-80.34948375418395,33.39455816017202],[-80.34948313541369,33.39464061874074],[-80.34958143828713,33.39464113773984],[-80.34958081960919,33.39472359630849],[-80.34967912257731,33.39472411522965],[-80.34967850399171,33.394806573798284],[-80.3497768070545,33.39480709264151],[-80.34977618856121,33.39488955121011],[-80.35016940119814,33.39489162580061],[-80.35016878307769,33.3949740843706],[-80.35046369284825,33.39497563949139],[-80.35046431068821,33.39489318091995],[-80.35085752335806,33.3948952533143],[-80.35085814082287,33.39481279474034],[-80.35095644389975,33.39481331264236],[-80.35095582652848,33.39489577121682],[-80.35105412970005,33.39489628904088],[-80.3510535124211,33.39497874761531],[-80.35125011895478,33.39497978302911],[-80.35125073604674,33.394897324453744],[-80.35134903922183,33.3948978420425],[-80.35134965621911,33.39481538346608],[-80.35154626238582,33.39481641840736],[-80.35154564557554,33.39489887698476],[-80.35164394875416,33.394899394338225],[-80.35164333203625,33.39498185291552],[-80.35183993858399,33.39498288738815],[-80.35183932205189,33.395065345965925],[-80.35203592879135,33.39506638012579],[-80.35203469609762,33.39523129728172],[-80.3521329996561,33.395231814244966],[-80.35213238340098,33.3953142728226],[-80.35232899070849,33.39531530651478],[-80.35232775856875,33.3954802236704],[-80.35242606241127,33.39548074039982],[-80.35242483045384,33.39564565755427],[-80.35291635061901,33.39564824002971],[-80.35291696613078,33.3955657814503],[-80.35301527007384,33.395566297709614],[-80.35301588549095,33.39548383912917],[-80.35311418934168,33.39548435530957],[-80.35311480466412,33.39540189672813],[-80.35321310842248,33.39540241282957],[-80.35321372365026,33.395319954247135],[-80.35360693832149,33.395322017866626],[-80.35360632346773,33.39540447645104],[-80.35380293099736,33.395405507791175],[-80.35380170166034,33.395570424960354],[-80.35399830956867,33.39557145598869],[-80.35399769508541,33.39565391457344],[-80.35389939103717,33.395653399098],[-80.3538883284556,33.39713765352282],[-80.35379002272542,33.397137137960186],[-80.35378940803295,33.39721959653375],[-80.35349449056896,33.39721804937374],[-80.35349510554195,33.397135590801646],[-80.35329849409216,33.397134558970436],[-80.353299109251,33.39705210039881],[-80.35310249799288,33.39705106825483],[-80.35310311333757,33.39696860968362],[-80.35300480780379,33.396968093494436],[-80.3530054232408,33.39688563492319],[-80.35280881236373,33.396884602310564],[-80.3528094279866,33.39680214373972],[-80.35261281730124,33.396801110814316],[-80.35261096986812,33.39704848652225],[-80.3524143586264,33.39704745328019],[-80.35241497462562,33.3969649947124],[-80.35231666910005,33.39696447797417],[-80.35231605300731,33.39704693654152],[-80.35221774738939,33.39704641972436],[-80.35221651501338,33.397211336856415],[-80.35211820920962,33.39721081995987],[-80.35211759292636,33.397293278524586],[-80.35201928703027,33.39729276154911],[-80.35201867065234,33.39737522011279],[-80.35192036466388,33.397374703058425],[-80.35191974819128,33.397457161621055],[-80.3518214421105,33.397456644487754],[-80.35182082554321,33.39753910304937],[-80.3517225193701,33.39753858583713],[-80.35172190270814,33.39762104439772],[-80.35162359644269,33.39762052710657],[-80.35162297968604,33.39770298566615],[-80.35152467332827,33.397702468296075],[-80.35152405647693,33.397784926854584],[-80.35093421779392,33.397781820983965],[-80.35093360038036,33.397864279539014],[-80.35083529384379,33.3978637616189],[-80.35083467633554,33.39794622017296],[-80.35073636970665,33.3979457021739],[-80.35073575210372,33.398028160726895],[-80.35063744538249,33.39802764264891],[-80.3506368276849,33.3981101012009],[-80.35053852087131,33.39810958304401],[-80.35053666749091,33.39835695869519],[-80.35034005330627,33.39835592214313],[-80.35034067128792,33.39827346359425],[-80.35024236429086,33.39827294520109],[-80.3502417462157,33.398355403749456],[-80.35014343912631,33.398354885277335],[-80.35014652995793,33.39794259253245],[-80.34985161009945,33.397941036652846],[-80.34985284698489,33.39777611955404],[-80.34975454055478,33.39777560077159],[-80.34975515908924,33.3976931422219],[-80.3496568527538,33.39769262336152],[-80.34965809000623,33.39752770626139],[-80.349363171568,33.3975261492126],[-80.34936379047299,33.397443690663195],[-80.34926548442277,33.397443171490565],[-80.34926610342006,33.397360712941094],[-80.34916779746453,33.3973601936905],[-80.34916841655416,33.397277735141024],[-80.34907011069332,33.39727721581249],[-80.34907072987528,33.39719475726293],[-80.3489724241091,33.39719423785647],[-80.34897304338341,33.39711177930684],[-80.34887473771192,33.397111259822424],[-80.34887597644398,33.39694634272261],[-80.34877767096067,33.39694582316074],[-80.34878014878467,33.39661598895656],[-80.34868184367656,33.396615469318206],[-80.34868246322314,33.396533010766284],[-80.34858415820973,33.39653249104996],[-80.3485847778486,33.39645003249805],[-80.34838816801236,33.39644899283113],[-80.34838878783707,33.39636653427961],[-80.34819217819252,33.39636549429992],[-80.34819279820307,33.39628303574887],[-80.34809449347607,33.39628251564187],[-80.3481000743594,33.39554038866255],[-80.34800177047511,33.395539868481514],[-80.34800239066085,33.395457409926095],[-80.34770747929561,33.39545584891391],[-80.34770809976068,33.3953733903594],[-80.34751149237674,33.39537234929342],[-80.34751211302763,33.39528989073934],[-80.34731550583544,33.39528884936059],[-80.34731612667217,33.39520639080698],[-80.34721782317133,33.39520587000045],[-80.34722092780473,33.39479357722676],[-80.34761413994512,33.394795659972424],[-80.34761476049424,33.394713201414135],[-80.34771306343882,33.39471372190397],[-80.34771368389323,33.394631263344635],[-80.34781198674548,33.39463178375554],[-80.34781260710525,33.39454932519514],[-80.34791090986513,33.39454984552715],[-80.34791153013026,33.39446738696575],[-80.34800983279783,33.39446790721883],[-80.34801045296824,33.3943854486564],[-80.3481087555435,33.394385968830576],[-80.34810937561923,33.3943035102671],[-80.3484042830716,33.39430507031742],[-80.34840490286565,33.39422261175201]]]},"id":"globalwatershed","properties":{}}],
                "P24hr": 5.74,
                "weightingMethod": "runoff"
            }
        }

class PRF(BaseModel):
    # all fields are required
    prfData: list = Field(..., title="PRF Data", description="data corresponding to PRF values (list)")

    class Config:
        schema_extra = {
            "example": {
                "prfData":[
                    {
                        "PRF": 180,
                        "Area": 50.0
                    },
                    {
                        "PRF": 300,
                        "Area": 50.0
                    }
                ]   
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
    Qp: float = Field(..., title="weighted Qp", description="area-weighted flow statistic for the AEP of interest (cubic feet per second, float)", example="400.0")
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
                "Qp": 37.5,
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
                            "Overland Slope": 0.000001,
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
    AEP: float = Field(..., title="Annual Exceedance Probability", description="Annual Exceedance Probability (%); options are 100 50, 20, 10, 4, 2, 1, which correspond to 1-yr, 2-yr, 5-yr, 10-yr, 25-yr, 50-yr, and 100-yr storms (int)", example="4")
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
    watershedFeatures: list = Field(..., title="watershed features", description="list of features of delineated watershed returned by StreamStatsServices")
    prfData: list = Field(..., title="PRF Data", description="data corresponding to PRF values (list)")
    AEP: float = Field(..., title="Annual Exceedance Probability", description="Annual Exceedance Probability (%); options are 100, 50,20, 10, 4, 2, 1, which correspond to 1-yr, 2-yr, 5-yr, 10-yr, 25-yr, 50-yr, and 100-yr storms (int)", example="4")
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
                "watershedFeatures": [{"type":"Feature","geometry":{"type":"Polygon","coordinates":[[[-80.34840490286565,33.39422261175201],[-80.34850320525864,33.39422313161143],[-80.34850196585636,33.3943880487428],[-80.34860026843751,33.394388568524725],[-80.34860088804575,33.394306109958826],[-80.34879749302459,33.39430714928652],[-80.34879687360336,33.394389607853384],[-80.34889517618805,33.39439012740008],[-80.34889455685915,33.39447258596689],[-80.34909116221907,33.394473624825906],[-80.34909178136097,33.39439116625811],[-80.3491900839492,33.39439168556949],[-80.34918946490079,33.39447414413778],[-80.34928776758372,33.39447466337122],[-80.34928714862761,33.394557121939464],[-80.34948375418395,33.39455816017202],[-80.34948313541369,33.39464061874074],[-80.34958143828713,33.39464113773984],[-80.34958081960919,33.39472359630849],[-80.34967912257731,33.39472411522965],[-80.34967850399171,33.394806573798284],[-80.3497768070545,33.39480709264151],[-80.34977618856121,33.39488955121011],[-80.35016940119814,33.39489162580061],[-80.35016878307769,33.3949740843706],[-80.35046369284825,33.39497563949139],[-80.35046431068821,33.39489318091995],[-80.35085752335806,33.3948952533143],[-80.35085814082287,33.39481279474034],[-80.35095644389975,33.39481331264236],[-80.35095582652848,33.39489577121682],[-80.35105412970005,33.39489628904088],[-80.3510535124211,33.39497874761531],[-80.35125011895478,33.39497978302911],[-80.35125073604674,33.394897324453744],[-80.35134903922183,33.3948978420425],[-80.35134965621911,33.39481538346608],[-80.35154626238582,33.39481641840736],[-80.35154564557554,33.39489887698476],[-80.35164394875416,33.394899394338225],[-80.35164333203625,33.39498185291552],[-80.35183993858399,33.39498288738815],[-80.35183932205189,33.395065345965925],[-80.35203592879135,33.39506638012579],[-80.35203469609762,33.39523129728172],[-80.3521329996561,33.395231814244966],[-80.35213238340098,33.3953142728226],[-80.35232899070849,33.39531530651478],[-80.35232775856875,33.3954802236704],[-80.35242606241127,33.39548074039982],[-80.35242483045384,33.39564565755427],[-80.35291635061901,33.39564824002971],[-80.35291696613078,33.3955657814503],[-80.35301527007384,33.395566297709614],[-80.35301588549095,33.39548383912917],[-80.35311418934168,33.39548435530957],[-80.35311480466412,33.39540189672813],[-80.35321310842248,33.39540241282957],[-80.35321372365026,33.395319954247135],[-80.35360693832149,33.395322017866626],[-80.35360632346773,33.39540447645104],[-80.35380293099736,33.395405507791175],[-80.35380170166034,33.395570424960354],[-80.35399830956867,33.39557145598869],[-80.35399769508541,33.39565391457344],[-80.35389939103717,33.395653399098],[-80.3538883284556,33.39713765352282],[-80.35379002272542,33.397137137960186],[-80.35378940803295,33.39721959653375],[-80.35349449056896,33.39721804937374],[-80.35349510554195,33.397135590801646],[-80.35329849409216,33.397134558970436],[-80.353299109251,33.39705210039881],[-80.35310249799288,33.39705106825483],[-80.35310311333757,33.39696860968362],[-80.35300480780379,33.396968093494436],[-80.3530054232408,33.39688563492319],[-80.35280881236373,33.396884602310564],[-80.3528094279866,33.39680214373972],[-80.35261281730124,33.396801110814316],[-80.35261096986812,33.39704848652225],[-80.3524143586264,33.39704745328019],[-80.35241497462562,33.3969649947124],[-80.35231666910005,33.39696447797417],[-80.35231605300731,33.39704693654152],[-80.35221774738939,33.39704641972436],[-80.35221651501338,33.397211336856415],[-80.35211820920962,33.39721081995987],[-80.35211759292636,33.397293278524586],[-80.35201928703027,33.39729276154911],[-80.35201867065234,33.39737522011279],[-80.35192036466388,33.397374703058425],[-80.35191974819128,33.397457161621055],[-80.3518214421105,33.397456644487754],[-80.35182082554321,33.39753910304937],[-80.3517225193701,33.39753858583713],[-80.35172190270814,33.39762104439772],[-80.35162359644269,33.39762052710657],[-80.35162297968604,33.39770298566615],[-80.35152467332827,33.397702468296075],[-80.35152405647693,33.397784926854584],[-80.35093421779392,33.397781820983965],[-80.35093360038036,33.397864279539014],[-80.35083529384379,33.3978637616189],[-80.35083467633554,33.39794622017296],[-80.35073636970665,33.3979457021739],[-80.35073575210372,33.398028160726895],[-80.35063744538249,33.39802764264891],[-80.3506368276849,33.3981101012009],[-80.35053852087131,33.39810958304401],[-80.35053666749091,33.39835695869519],[-80.35034005330627,33.39835592214313],[-80.35034067128792,33.39827346359425],[-80.35024236429086,33.39827294520109],[-80.3502417462157,33.398355403749456],[-80.35014343912631,33.398354885277335],[-80.35014652995793,33.39794259253245],[-80.34985161009945,33.397941036652846],[-80.34985284698489,33.39777611955404],[-80.34975454055478,33.39777560077159],[-80.34975515908924,33.3976931422219],[-80.3496568527538,33.39769262336152],[-80.34965809000623,33.39752770626139],[-80.349363171568,33.3975261492126],[-80.34936379047299,33.397443690663195],[-80.34926548442277,33.397443171490565],[-80.34926610342006,33.397360712941094],[-80.34916779746453,33.3973601936905],[-80.34916841655416,33.397277735141024],[-80.34907011069332,33.39727721581249],[-80.34907072987528,33.39719475726293],[-80.3489724241091,33.39719423785647],[-80.34897304338341,33.39711177930684],[-80.34887473771192,33.397111259822424],[-80.34887597644398,33.39694634272261],[-80.34877767096067,33.39694582316074],[-80.34878014878467,33.39661598895656],[-80.34868184367656,33.396615469318206],[-80.34868246322314,33.396533010766284],[-80.34858415820973,33.39653249104996],[-80.3485847778486,33.39645003249805],[-80.34838816801236,33.39644899283113],[-80.34838878783707,33.39636653427961],[-80.34819217819252,33.39636549429992],[-80.34819279820307,33.39628303574887],[-80.34809449347607,33.39628251564187],[-80.3481000743594,33.39554038866255],[-80.34800177047511,33.395539868481514],[-80.34800239066085,33.395457409926095],[-80.34770747929561,33.39545584891391],[-80.34770809976068,33.3953733903594],[-80.34751149237674,33.39537234929342],[-80.34751211302763,33.39528989073934],[-80.34731550583544,33.39528884936059],[-80.34731612667217,33.39520639080698],[-80.34721782317133,33.39520587000045],[-80.34722092780473,33.39479357722676],[-80.34761413994512,33.394795659972424],[-80.34761476049424,33.394713201414135],[-80.34771306343882,33.39471372190397],[-80.34771368389323,33.394631263344635],[-80.34781198674548,33.39463178375554],[-80.34781260710525,33.39454932519514],[-80.34791090986513,33.39454984552715],[-80.34791153013026,33.39446738696575],[-80.34800983279783,33.39446790721883],[-80.34801045296824,33.3943854486564],[-80.3481087555435,33.394385968830576],[-80.34810937561923,33.3943035102671],[-80.3484042830716,33.39430507031742],[-80.34840490286565,33.39422261175201]]]},"id":"globalwatershed","properties":{}}],
                "prfData":[
                    {
                        "PRF": 180,
                        "Area": 50.0
                    },
                    {
                        "PRF": 300,
                        "Area": 50.0
                    }
                ],
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
                            "Overland Slope": 0.000001,
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

class calculateStormPonds(BaseModel):
    lat: float = Field(..., title="latitude", description="latitude coordinate of the drainage point (float)", example="33.3946")
    lon: float = Field(..., title="longitude", description="longitude coordinate of the drainage point (float)", example="-80.3474")
    AEP: float = Field(..., title="Annual Exceedance Probability", description="Annual Exceedance Probability (%); options are 100 50, 20, 10, 4, 2, 1, which correspond to 1-yr, 2-yr, 5-yr, 10-yr, 25-yr, 50-yr, and 100-yr storms (int)", example="4")
    CNModificationMethod: str = Field(..., title="Curve Number Modification Method", description="method used to modify the Curve Number; options are 'McCuen' or 'Merkel' (string)", example="Merkel")
    Area: float = Field(..., title="Area", description="drainage area of delineated basin (float)", example="100.0")
    Tc: float = Field(..., title="Time of Concentration", description="Time of Concentration as computed by Travel Time Method or Lag Time Equation (float)", example="64.5")
    RainfallDistributionCurve: str = Field(..., title="Rainfall Distribution Curve", description="rainfall distribution curve letter; options are 'II', 'III', 'A', 'B', 'C', 'D' (string)", example="II")
    PRF: float = Field(..., title="Peak Rate Factor (float)", description="", example="240")
    CN: float = Field(..., title="Curve Number", description="weighted Curve Number (float)", example="67.3")
    S: float = Field(..., title="Watershed Retention", description="watershed Retention, S (float)", example="4.86")
    Ia: float = Field(..., title="Initial Abstraction", description="Initial Abstraction, Ia (float)", example="0.97")
    pondOption: int = Field(..., title="Pond Option", description="Pond Option, (int)", example="1")
    pond_bottom_elev: float = Field(..., title="Bottom Elevation", description="Elevation of pond bottom in feet (float)", example="100")
    Orif1_Coeff: float = Field(..., title="Orifice 1 Coefficient", description="Coefficient of 1st stage circular orifice (float)", example=".60")
    Orif1_Dia: float = Field(..., title="Orifice 1 Diameter", description="Diameter of 1st stage circular orifice in inches (float)", example="6.0")
    Orif1_CtrEL: float = Field(..., title="Orifice 1 Centerline Elevation", description="Centerline elevation above pond bottom of 1st stage circular orifice in feet (float)", example=".5")
    Orif1_NumOpenings: int = Field(..., title="Orifice 1 Number of Openings", description="Number of openings for 1st stage circular orifice, (int)", example="1")
    Orif2_Coeff: float = Field(..., title="Orifice 2 Coefficient", description="Coefficient of 2nd stage circular orifice (float)", example=".60")
    Orif2_Dia: float = Field(..., title="Orifice 2 Diameter", description="Diameter of 2nd stage circular orifice in inches (float)", example="6.0")
    Orif2_CtrEL: float = Field(..., title="Orifice 2 Centerline Elevation", description="Centerline elevation above pond bottom of 2nd stage circular orifice in feet (float)", example="2.0")
    Orif2_NumOpenings: int = Field(..., title="Orifice 2 Number of Openings", description="Number of openings for 2nd stage circular orifice, (int)", example="1")
    Rec_Weir_Coeff: float = Field(..., title="Weir Coefficient", description="Coefficient of 3rd stage rectangular weir (float)", example="3.30")
    Rec_Weir_Ex: float = Field(..., title="Weir Exponent", description="Exponent of 3rd stage rectangular weir (float)", example="1.5")
    Rec_Weir_Length: float = Field(..., title="Weir Length", description="Length of 3rd stage rectangular weir in feet (float)", example="2.0")
    Rec_WeirCrest_EL: float = Field(..., title="Weir Crest Elevation", description="Crest elevation above pond bottom of 3rd stage rectangular weir in feet (float)", example="4.0")
    Rec_Num_Weirs: int = Field(..., title="Number of Weirs", description="Number of weirs for 3rd stage rectangular weir, (int)", example="1")
    OS_BCWeir_Coeff: float = Field(..., title="Broad-Crested Weir Coefficient", description="Broad-Crested weir coefficient of overflow spillway (float)", example="3.00")
    OS_Weir_Ex: float = Field(..., title="Weir Exponent", description="Exponent of  overflow spillway (float)", example="1.5")
    OS_Length: float = Field(..., title="Overflow Spillway Length", description="Length of overflow spillway in feet (float)", example="2.0")
    OS_Crest_EL: float = Field(..., title="Overflow Crest Elevation", description="Crest elevation above pond bottom of overflow spillway in feet (float)", example="6.0") 
    Seepage_Bottom: float = Field(..., title="Bottom Seepage", description="Seepage through pond bottom in in/hr, (float)", example="2.0")
    Seepage_Side: float = Field(..., title="Side Slope Seepage", description="Seepage through side slopes in in/hr, (float)", example="4.0")
    length: float = Field(default=None, title="Length of Inverted Quadrilateral Frustum", description="Length of inverted quadrilateral frustum in feet, for pond option 1, (float)", example="200")
    w1: float = Field(default=None, title="W1 Inverted Quadrilateral Frustum", description="W1 of inverted quadrilateral frustum in feet, for pond option 1, (float)", example="200")
    w2: float = Field(default=None, title="W2 Inverted Quadrilateral Frustum", description="W2 of inverted quadrilateral frustum in feet, for pond option 1, (float)", example="200")
    side_slope_z: float = Field(default=None, title="Side Slope of Inverted Quadrilateral Frustum", description="Side slope z of inverted quadrilateral frustum, for pond option 1, (float)", example="3.0")
    bottom_slope: float = Field(default=None, title="Bottom Slope of Inverted Quadrilateral Frustum", description="Bottom slope of inverted quadrilateral frustum in %, for pond option 1, (float)", example=".5")
    Elev_Area: list = Field(default=None, title="Elevation vs Surface Area", description="Elevation in ft-MSL vs Surface Area in sq ft, for pond option 2, (float)", example="[[100, 2000], [101,2100],[102,2200],[103,2400],[104, 2900],[105,3300],[106,3700],[107,4000],[108,4400],[109,4800]]")
    
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
                "Ia": 0.97,
                "pondOption": 1,
                "pond_bottom_elev": 100,
                "Orif1_Coeff":.6,
                "Orif1_Dia": 6,
                "Orif1_CtrEL": .5,
                "Orif1_NumOpenings": 1,
                "Orif2_Coeff": .6,
                "Orif2_Dia": 6,
                "Orif2_CtrEL": 2,
                "Orif2_NumOpenings": 1,
                "Rec_Weir_Coeff": 3.3,
                "Rec_Weir_Ex": 1.5,
                "Rec_Weir_Length": 2,
                "Rec_WeirCrest_EL": 4,
                "Rec_Num_Weirs": 1,
                "OS_BCWeir_Coeff": 3,
                "OS_Weir_Ex": 1.5,
                "OS_Length": 20,
                "OS_Crest_EL": 6,
                "Seepage_Bottom": 2,
                "Seepage_Side": 4,
                "length": 200,
                "w1": 200,
                "w2": 200,
                "side_slope_z": 3,
                "bottom_slope": .5
            }
        }


######
##
## API Endpoints
##
######


# redirect root and /settings.SERVICE_NAME to the docs
@app.get("/", include_in_schema=False)
#def docs_redirect_root():
#    return RedirectResponse(url=app.docs_url)
async def root():
    return {"message": "Hello World"}

@app.post("/weightedcurvenumber/")
def weighted(request_body: CurveNumber, response: Response):

    try: 
        runoff_weighted_CN, WS_retention_S, initial_abstraction_Ia = weightedCurveNumber(
            request_body.watershedFeatures,
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
            request_body.prfData
        )
        return {
            "PRF": PRF
        }

    except Exception as e:
        raise HTTPException(status_code = 500, detail =  str(e))


@app.post("/rainfall/")
def rainfalldata(request_body: RainfallData, response: Response):

    try: 
        P1_1,P1_2,P1_3,P1_6,P1_12,P1_24,P2_1,P2_2,P2_3,P2_6,P2_12,P2_24,P5_1,P5_2,P5_3,P5_6,P5_12,P5_24,P10_1,P10_2,P10_3,P10_6,P10_12,P10_24,P25_1,P25_2,P25_3,P25_6,P25_12,P25_24,P50_1,P50_2,P50_3,P50_6,P50_12,P50_24,P100_1,P100_2,P100_3,P100_6,P100_12,P100_24,P2_24_1,P2_24_2,P2_24_5,P2_24_10,P2_24_25,P2_24_50,P2_24_100 = rainfallData(
            request_body.lat,
            request_body.lon
        )

        return {
            "P1_1": P1_1, 
            "P1_2": P1_2,
            "P1_3": P1_3,
            "P1_6": P1_6,
            "P1_12": P1_12,
            "P1_24": P1_24,
            "P2_1": P2_1, 
            "P2_2": P2_2,
            "P2_3": P2_3,
            "P2_6": P2_6,
            "P2_12": P2_12,
            "P2_24": P2_24,
            "P5_1": P5_1, 
            "P5_2": P5_2,
            "P5_3": P5_3,
            "P5_6": P5_6,
            "P5_12": P5_12,
            "P5_24": P5_24,
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
            request_body.Qp,
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

@app.post("/calculatemissingparametersSCSUH/")
def calculatemissingparametersSCSUH(request_body: CalculateMissingParametersSCSUH, response: Response):

    try: 
        rainfall_distribution_curve_letter, Tc, PRF, CN, S, Ia = calculateMissingParametersSCSUH(
            request_body.lat,
            request_body.lon,
            request_body.watershedFeatures,
            request_body.prfData,
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
    


@app.post("/stormponds/")
def stormponds(request_body: calculateStormPonds, response: Response):

    try: 
        runoff_and_ponding_results, pond_inflow_and_outflow_ordinates = calcStormPonds(
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
            request_body.Ia,
            request_body.pondOption,
            request_body.pond_bottom_elev,
            request_body.Orif1_Coeff,
            request_body.Orif1_Dia,
            request_body.Orif1_CtrEL,
            request_body.Orif1_NumOpenings,
            request_body.Orif2_Coeff,
            request_body.Orif2_Dia,
            request_body.Orif2_CtrEL,
            request_body.Orif2_NumOpenings,
            request_body.Rec_Weir_Coeff,
            request_body.Rec_Weir_Ex,
            request_body.Rec_Weir_Length,
            request_body.Rec_WeirCrest_EL,
            request_body.Rec_Num_Weirs,
            request_body.OS_BCWeir_Coeff,
            request_body.OS_Weir_Ex,
            request_body.OS_Length,
            request_body.OS_Crest_EL,
            request_body.Seepage_Bottom,
            request_body.Seepage_Side,
            request_body.length,
            request_body.w1,
            request_body.w2,
            request_body.side_slope_z,
            request_body.bottom_slope
        )
        return {
            "runoff_and_ponding_results": runoff_and_ponding_results,
            "pond_inflow_and_outflow_ordinates": pond_inflow_and_outflow_ordinates        
        }        

    except Exception as e:
        raise HTTPException(status_code = 500, detail =  str(e))

