from fastapi import FastAPI

from distribution.feed_functions import get_published_events
from save_load import load_platform


app = FastAPI(
    title="Goldliner Trading Matrix API",
    description="Customer-facing sportsbook odds feed.",
    version="0.1.0",
)


@app.get("/")
def api_home():
    return {
        "service": "Goldliner Trading Matrix API",
        "status": "running",
    }


@app.get("/events")
def get_events():
    platform = load_platform()

    return get_published_events(platform)