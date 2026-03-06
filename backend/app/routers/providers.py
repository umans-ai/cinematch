"""Router for streaming providers and region management."""

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

# TMDB Watch Provider IDs
PROVIDERS: dict[str, dict[str, str | int]] = {
    "netflix": {"id": 8, "name": "Netflix", "logo_path": "/t2yyOv40KVeID71UaGuYIvyrjzC.png"},
    "prime": {"id": 9, "name": "Prime Video", "logo_path": "/fvP5nBdYG1Q3RrP6Xn0R7HQjNgC.png"},
    "disney": {"id": 337, "name": "Disney+", "logo_path": "/nzrn4QcJ4w1yKBRqPznE4PsMCjY.png"},
    "hbo": {"id": 384, "name": "HBO Max", "logo_path": "/pdN7WLOGPc1X9cfQqHr7L1ScIoK.png"},
    "appletv": {"id": 350, "name": "Apple TV+", "logo_path": "/8ciL3GDanlr8M9M7UJQfNJMzpw0.png"},
    "hulu": {"id": 15, "name": "Hulu", "logo_path": "/2wUJGxU0aWgBCnIximZ5WhpOmuN.png"},
}

# Major markets with region codes
REGIONS = {
    "US": {"name": "United States", "flag": "🇺🇸"},
    "FR": {"name": "France", "flag": "🇫🇷"},
    "GB": {"name": "United Kingdom", "flag": "🇬🇧"},
    "DE": {"name": "Germany", "flag": "🇩🇪"},
    "ES": {"name": "Spain", "flag": "🇪🇸"},
    "IT": {"name": "Italy", "flag": "🇮🇹"},
    "CA": {"name": "Canada", "flag": "🇨🇦"},
    "AU": {"name": "Australia", "flag": "🇦🇺"},
    "JP": {"name": "Japan", "flag": "🇯🇵"},
    "BR": {"name": "Brazil", "flag": "🇧🇷"},
}

# Rough bounding boxes for major regions (for GPS detection)
# Format: (min_lat, max_lat, min_lng, max_lng)
REGION_BOUNDS = {
    "US": (24.396308, 49.384358, -124.848974, -66.885444),
    "FR": (41.325300, 51.124200, -5.141300, 9.560100),
    "GB": (49.959999, 58.635000, -7.572168, 1.681531),
    "DE": (47.270111, 55.099161, 5.866315, 15.041932),
    "ES": (35.173000, 43.791000, -9.301000, 4.328000),
    "IT": (35.493000, 47.092000, 6.626720, 18.520400),
    "CA": (41.676556, 83.336212, -141.001870, -52.323551),
    "AU": (-43.634597, -10.668186, 113.338953, 153.569469),
    "JP": (24.396308, 45.551483, 122.934570, 153.986672),
    "BR": (-33.751748, 5.271946, -73.982817, -34.793147),
}


class ProviderResponse(BaseModel):
    id: int
    name: str
    logo_url: str


class RegionResponse(BaseModel):
    code: str
    name: str
    flag: str


class RegionDetectRequest(BaseModel):
    lat: float
    lng: float


class RegionDetectResponse(BaseModel):
    code: str | None
    name: str | None
    flag: str | None
    detected: bool


@router.get("", response_model=list[ProviderResponse])
def get_providers() -> list[ProviderResponse]:
    """Get list of available streaming platforms."""
    base_url = "https://image.tmdb.org/t/p/original"
    return [
        ProviderResponse(
            id=int(data["id"]),
            name=str(data["name"]),
            logo_url=f"{base_url}{data['logo_path']}",
        )
        for key, data in PROVIDERS.items()
    ]


@router.get("/regions", response_model=list[RegionResponse])
def get_regions() -> list[RegionResponse]:
    """Get list of available regions."""
    return [
        RegionResponse(code=code, name=data["name"], flag=data["flag"])
        for code, data in REGIONS.items()
    ]


@router.post("/detect-region", response_model=RegionDetectResponse)
def detect_region(request: RegionDetectRequest) -> RegionDetectResponse:
    """Detect region from GPS coordinates."""
    lat, lng = request.lat, request.lng

    for code, (min_lat, max_lat, min_lng, max_lng) in REGION_BOUNDS.items():
        if min_lat <= lat <= max_lat and min_lng <= lng <= max_lng:
            region_data = REGIONS[code]
            return RegionDetectResponse(
                code=code,
                name=region_data["name"],
                flag=region_data["flag"],
                detected=True,
            )

    return RegionDetectResponse(
        code=None,
        name=None,
        flag=None,
        detected=False,
    )
