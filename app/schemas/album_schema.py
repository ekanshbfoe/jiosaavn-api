from typing import List

from pydantic import BaseModel

from .song_schema import SongSchema


class AlbumSchema(BaseModel):
    """
    Pydantic model for representing an album's metadata.
    """

    name: str
    year: str
    primary_artists: str
    image: str
    songs: List[SongSchema]

    class Config:
        extra = "allow"
