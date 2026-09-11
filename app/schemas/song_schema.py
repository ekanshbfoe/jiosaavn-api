from typing import Optional

from pydantic import BaseModel, Field


class SongSchema(BaseModel):
    """
    Pydantic model for representing a song's metadata.
    """

    id: str
    song: str
    album: str
    artists: str = Field(alias="primary_artists")
    singers: str
    image: str
    media_url: Optional[str] = None
    lyrics: Optional[str] = None
    duration: Optional[str] = None
    year: Optional[str] = None
    language: Optional[str] = None
    copyright_text: Optional[str] = None

    class Config:
        allow_population_by_field_name = True
        extra = "allow"
