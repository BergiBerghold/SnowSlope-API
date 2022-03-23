from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from main import do_flood_fill
from pydantic import BaseModel
from fastapi import FastAPI

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


@app.post("/calculation_endpoint")
async def calculation_endpoint(data: datapoint):
    return {"filename": None, "code": 13}

    tiles_filename, return_code = do_flood_fill(lat=data.positionLat,
                                                long=data.positionLng,
                                                min_slope=data.minimumGradient,
                                                max_slope=data.maximumGradient)

    if tiles_filename:
        app.mount(f"/{tiles_filename}", StaticFiles(directory=f"Kaprun_output/{tiles_filename}"), name=tiles_filename)

    return {"filename": tiles_filename, "code": return_code}
