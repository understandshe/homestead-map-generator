from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from renderer import HomesteadRenderer
import io

app = FastAPI(title="Homestead Realistic Map Generator")

class Feature(BaseModel):
    x: float
    y: float
    w: float
    h: float
    color: str
    shadow: bool = True

class MapRequest(BaseModel):
    width_m: int
    height_m: int
    px_per_meter: int = 12
    features: list[Feature]
    legend: list[tuple[str, str]]  # [("House", "#C4A484"), ...]

@app.post("/generate-map")
async def generate_map(req: MapRequest):
    try:
        renderer = HomesteadRenderer(req.width_m, req.height_m, req.px_per_meter)
        png_bytes = renderer.render(
            [f.model_dump() for f in req.features],
            req.legend
        )
        return StreamingResponse(png_bytes, media_type="image/png")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
