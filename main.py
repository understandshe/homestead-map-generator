from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from renderer import PremiumHomesteadRenderer
import io

app = FastAPI(title="Premium Homestead Map Generator")

# CORS Middleware - GitHub Pages से API कॉल के लिए
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Feature(BaseModel):
    x: float
    y: float
    w: float
    h: float
    type: str  # "field", "house", "pond", "road", "garden", "barn", "flower"
    shadow: bool = True

class MapRequest(BaseModel):
    width_m: int
    height_m: int
    px_per_meter: int = 15
    features: list[Feature]
    legend: list[tuple[str, str]]

@app.post("/generate-map")
async def generate_map(req: MapRequest):
    try:
        renderer = PremiumHomesteadRenderer(req.width_m, req.height_m, req.px_per_meter)
        png_bytes = renderer.render(
            [f.model_dump() for f in req.features],
            req.legend
        )
        return StreamingResponse(png_bytes, media_type="image/png")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/")
def root():
    return {"message": "Premium Homestead Map Generator API", "status": "running"}
