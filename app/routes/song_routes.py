from typing import List, Union

from fastapi import APIRouter, HTTPException, Query, Request

from app.schemas.song_schema import SongSchema
from app.services.saavn_service import SaavnService

router = APIRouter()


@router.get("/", response_model=List[Union[dict, SongSchema]])
async def search_songs(
    request: Request,
    query: str = Query(..., description="Search query for songs"),
    lyrics: bool = Query(False, description="Include song lyrics"),
    songdata: bool = Query(True, description="Fetch full song details"),
):
    """
    Search for songs on Saavn.
    - **query**: Search term for finding songs
    - **lyrics**: Include song lyrics in the response
    - **songdata**: Fetch full song details or basic information
    """
    if not query:
        raise HTTPException(
            status_code=400, detail="Query is required to search songs!"
        )
    try:
        saavn_service: SaavnService = request.app.state.saavn_service
        songs = await saavn_service.search_songs(
            query, include_lyrics=lyrics, full_data=songdata
        )
        return songs
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error searching songs: {str(e)}"
        ) from e


@router.get("/get", response_model=Union[dict, SongSchema])
async def get_song(
    request: Request,
    song_id: str = Query(..., description="Song ID"),
    lyrics: bool = Query(False, description="Include song lyrics"),
):
    """
    Retrieve a specific song by its ID.
    - **song_id**: Unique identifier of the song
    - **lyrics**: Include song lyrics in the response
    """
    if not song_id:
        raise HTTPException(status_code=400, detail="Song ID is required!")
    try:
        saavn_service: SaavnService = request.app.state.saavn_service
        song = await saavn_service.get_song(song_id, include_lyrics=lyrics)
        if not song:
            raise HTTPException(status_code=404, detail="Invalid Song ID!")
        return song
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error fetching song: {str(e)}"
        ) from e
