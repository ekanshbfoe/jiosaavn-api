from typing import List

from pydantic import BaseModel

from .song_schema import SongSchema


class PlaylistSchema(BaseModel):
    """
    Pydantic model for representing a playlist's metadata.
    """

    firstname: str
    listname: str
    songs: List[SongSchema]

    class Config:
        extra = "allow"
