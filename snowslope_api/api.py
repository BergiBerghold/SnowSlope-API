from fastapi.middleware.cors import CORSMiddleware
from snowslope_api.main import calculate_slope
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from fastapi import FastAPI
from osgeo import gdal
import os

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class datapoint(BaseModel):
    minimumGradient: int
    maximumGradient: int
    positionLat: float
    positionLng: float


if not os.path.exists('tiles_output'):
    os.mkdir('tiles_output')

app.mount(f"/tiles_output", StaticFiles(directory=f"tiles_output"), name="tiles_output")


if os.path.exists('DGM_Salzburg.tif'):
    model_file = 'DGM_Salzburg.tif'

elif os.path.exists('../DGM_Salzburg.tif'):
    model_file = '../DGM_Salzburg.tif'

dgm_datasource = gdal.Open(model_file)


@app.post("/calculation_endpoint")
async def calculation_endpoint(data: datapoint):
    return_data, return_code = calculate_slope(datasource=dgm_datasource,
                                               lat=data.positionLat,
                                               long=data.positionLng,
                                               min_slope=data.minimumGradient,
                                               max_slope=data.maximumGradient)

    return {"return_data": return_data, "code": return_code}
