import asyncio
import logging
import os
from contextlib import asynccontextmanager
from typing import Dict, List, Union

import markdown
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from app.config import settings
from app.core.exceptions import GlobalExceptionHandler
from app.routes import album_routes, lyrics_routes, playlist_routes, song_routes
from app.services.saavn_service import SaavnService

BASE_URL = settings.SAAVN_BASE_URL
SAAVN_URLS = [
    f"{BASE_URL}?__call=song.getDetails",
    f"{BASE_URL}?__call=content.getAlbumDetails",
    f"{BASE_URL}?__call=playlist.getDetails",
    f"{BASE_URL}?__call=lyrics.getLyrics",
    f"{BASE_URL}?__call=autocomplete.get",
]


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize the SaavnService and store it in app state
    saavn_service = SaavnService()
    await saavn_service.startup()
    app.state.saavn_service = saavn_service
    yield
    # Shutdown the SaavnService
    await saavn_service.shutdown()


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.
    Returns:
        FastAPI: Configured FastAPI application instance
    """
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    logger = logging.getLogger(__name__)

    # Initialize FastAPI app
    fastapi_app = FastAPI(
        title="Saavn API",
        description="Unofficial API for retrieving music information from Saavn",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # Add CORS middleware
    fastapi_app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include global exception handler
    GlobalExceptionHandler(fastapi_app)

    @fastapi_app.get("/", response_class=HTMLResponse, tags=["Root"])
    async def read_root():
        # Path to the README file
        readme_path = os.path.join(os.path.dirname(__file__), "README.md")
        # Read and convert the README.md file to HTML
        with open(readme_path, "r", encoding="utf-8") as file:
            readme_content = file.read()
            html_content = markdown.markdown(
                readme_content, extensions=["fenced_code", "tables"]
            )
        # Add custom links for API documentation
        html_page = f"""
        <html>
            <head>
                <title>JioSaavn API</title>
            </head>
            <body>
                <nav>
                    <ul>
                        <li><a href="/docs">Swagger Docs</a></li>
                        <li><a href="/redoc">ReDoc</a></li>
                    </ul>
                </nav>
                <hr>
                {html_content}
            </body>
        </html>
        """
        return HTMLResponse(content=html_page)

    # Health check
    @fastapi_app.get("/ping", tags=["Health Check"])
    async def health_check(
        request: Request,
    ) -> Dict[str, Union[str, List[Dict[str, Union[str, bool]]]]]:
        """Health check endpoint to see if you can connect to JioSaavn."""
        saavn_service: SaavnService = request.app.state.saavn_service

        async def check_url(url):
            try:
                response = await saavn_service.client.get(url)
                if response.status_code == 200:
                    return {"url": url, "status": "ok"}
                else:
                    return {
                        "url": url,
                        "status": f"failed with code {response.status_code}",
                    }
            except Exception as e:
                return {"url": url, "status": f"failed with error: {str(e)}"}

        tasks = [check_url(url) for url in SAAVN_URLS]
        health_status = await asyncio.gather(*tasks)

        overall_status = (
            "healthy"
            if all(item["status"] == "ok" for item in health_status)
            else "unhealthy"
        )

        return {
            "msg": "Pong!",
            "status": overall_status,
            "details": list(health_status),
        }

    fastapi_app.include_router(song_routes.router, prefix="/song", tags=["Songs"])
    fastapi_app.include_router(album_routes.router, prefix="/album", tags=["Albums"])
    fastapi_app.include_router(
        playlist_routes.router, prefix="/playlist", tags=["Playlists"]
    )
    fastapi_app.include_router(lyrics_routes.router, prefix="/lyrics", tags=["Lyrics"])

    logger.info("Application initialized successfully")
    return fastapi_app


app = create_app()
