import asyncio
import json
import logging
import re
from typing import Dict, List, Optional, Union

import httpx
from cachetools import TTLCache

from app.config import settings
from app.services.crypto_service import CryptoService

logger = logging.getLogger(__name__)


class SaavnService:
    """
    Service responsible for interacting with Saavn API and processing music data asynchronously.
    """

    BASE_URL = settings.SAAVN_BASE_URL

    def __init__(self):
        self.client = None
        # In-memory cache for search: 256 items, 10 minutes TTL
        self.search_cache = TTLCache(maxsize=256, ttl=600)

    async def startup(self):
        """Initialize the HTTP client on app startup."""
        self.client = httpx.AsyncClient(timeout=settings.REQUEST_TIMEOUT)

    async def shutdown(self):
        """Close the HTTP client on app shutdown."""
        if self.client:
            await self.client.aclose()

    @staticmethod
    def _format_string(string: str) -> str:
        """
        Clean and format input strings.
        Args:
            string (str): Input string to format
        Returns:
            str: Formatted string
        """
        if not string:
            return ""
        return (
            string.encode()
            .decode()
            .replace("&quot;", "'")
            .replace("&amp;", "&")
            .replace("&#039;", "'")
        )

    async def get_song_id(self, url: str) -> str:
        """
        Extract song ID from a Saavn URL.
        """
        try:
            res = await self.client.get(url)
            try:
                return (res.text.split('"pid":"'))[1].split('","')[0]
            except IndexError:
                return (
                    res.text.split('"song":{"type":"')[1]
                    .split('","image":')[0]
                    .split('"id":"')[-1]
                )
        except Exception as e:
            logger.error("Error extracting song ID: %s", e)
            raise

    async def get_album_id(self, input_url: str) -> str:
        """
        Extract album ID from a Saavn URL.
        """
        try:
            res = await self.client.get(input_url)
            try:
                return res.text.split('"album_id":"')[1].split('"')[0]
            except IndexError:
                return res.text.split('"page_id","')[1].split('","')[0]
        except Exception as e:
            logger.error("Error extracting album ID: %s", e)
            raise

    async def get_playlist_id(self, input_url: str) -> str:
        """
        Extract playlist ID from a Saavn URL.
        """
        try:
            res = await self.client.get(input_url)
            try:
                return res.text.split('"type":"playlist","id":"')[1].split('"')[0]
            except IndexError:
                return res.text.split('"page_id","')[1].split('","')[0]
        except Exception as e:
            logger.error("Error extracting playlist ID: %s", e)
            raise

    async def get_song(
        self, song_id: str, include_lyrics: bool = False
    ) -> Optional[Dict]:
        """
        Retrieve detailed song information.
        """
        try:
            song_url = f"{self.BASE_URL}?__call=song.getDetails&cc=in&_marker=0%3F_marker%3D0&_format=json&pids={song_id}"
            song_response = await self.client.get(song_url)
            song_data = song_response.text.encode().decode("unicode-escape")
            song_data = json.loads(song_data)
            if song_id not in song_data:
                return None

            processed_song = await self.format_song_data(
                song_data[song_id], include_lyrics
            )
            return processed_song
        except Exception as e:
            logger.warning("Error fetching song details for ID %s: %s", song_id, e)
            return None

    async def get_album(
        self, album_id: str, include_lyrics: bool = False
    ) -> Optional[Dict]:
        """
        Retrieve album details.
        """
        try:
            album_url = f"{self.BASE_URL}?__call=content.getAlbumDetails&_format=json&cc=in&_marker=0%3F_marker%3D0&albumid={album_id}"
            response = await self.client.get(album_url)
            album_data = response.text.encode().decode("unicode-escape")
            album_data = json.loads(album_data)

            # Process album data
            album_data["image"] = album_data.get("image", "").replace(
                "150x150", "500x500"
            )
            album_data["name"] = self._format_string(album_data.get("name", ""))
            album_data["primary_artists"] = self._format_string(
                album_data.get("primary_artists", "")
            )

            # Process songs in the album (concurrently formatted for safety, though formatting isn't inherently async here unless get_lyrics is needed)
            processed_songs = []
            for song in album_data.get("songs", []):
                try:
                    formatted = await self.format_song_data(song, include_lyrics)
                    if formatted and formatted.get("media_url"):
                        processed_songs.append(formatted)
                except Exception as e:
                    logger.warning("Error processing song in album: %s", e)
                    continue
            album_data["songs"] = processed_songs

            return album_data
        except Exception as e:
            logger.error("Error fetching album details: %s", e)
            raise

    async def get_playlist(
        self, playlist_id: str, include_lyrics: bool = False
    ) -> Optional[Dict]:
        """
        Retrieve playlist details.
        """
        try:
            playlist_url = f"{self.BASE_URL}?__call=playlist.getDetails&_format=json&cc=in&_marker=0%3F_marker%3D0&listid={playlist_id}"
            response = await self.client.get(playlist_url)
            playlist_data = response.text.encode().decode("unicode-escape")
            playlist_data = json.loads(playlist_data)

            # Process playlist data
            playlist_data["firstname"] = self._format_string(
                playlist_data.get("firstname", "")
            )
            playlist_data["listname"] = self._format_string(
                playlist_data.get("listname", "")
            )

            # Process songs in the playlist
            processed_songs = []
            for song in playlist_data.get("songs", []):
                try:
                    formatted = await self.format_song_data(song, include_lyrics)
                    if formatted and formatted.get("media_url"):
                        processed_songs.append(formatted)
                except Exception as e:
                    logger.warning("Error processing song in playlist: %s", e)
                    continue
            playlist_data["songs"] = processed_songs

            return playlist_data
        except Exception as e:
            logger.error("Error fetching playlist details: %s", e)
            raise

    async def get_lyrics(self, song_id: str) -> Optional[str]:
        """
        Retrieve song lyrics.
        """
        try:
            lyrics_url = f"{self.BASE_URL}?__call=lyrics.getLyrics&ctx=web6dot0&api_version=4&_format=json&_marker=0%3F_marker%3D0&lyrics_id={song_id}"
            response = await self.client.get(lyrics_url)
            lyrics_data = json.loads(response.text)
            return lyrics_data.get("lyrics")
        except Exception as e:
            logger.error("Error fetching lyrics: %s", e)
            return None

    async def format_song_data(
        self, data: Dict, include_lyrics: bool = False
    ) -> Optional[Dict[str, Union[str, None]]]:
        """
        Format and process song data gracefully.
        Returns None if critical errors occur during processing to omit bad tracks.
        """
        try:
            if not isinstance(data, dict):
                return None

            # Process media URL safely
            encrypted_url = data.get("encrypted_media_url")
            decrypted_url = (
                CryptoService.decrypt_url(encrypted_url) if encrypted_url else ""
            )
            data["media_url"] = decrypted_url

            # Adjust URL based on quality
            if data.get("320kbps") != "true" and data.get("media_url"):
                data["media_url"] = data["media_url"].replace("_320.mp4", "_160.mp4")

            # Process various fields safely
            for field in [
                "song",
                "music",
                "singers",
                "starring",
                "album",
                "primary_artists",
            ]:
                data[field] = self._format_string(data.get(field, ""))

            data["image"] = data.get("image", "").replace("150x150", "500x500")
            data["duration"] = str(data.get("duration", "0"))

            # Process lyrics if requested
            if include_lyrics and data.get("has_lyrics") == "true":
                data["lyrics"] = await self.get_lyrics(data.get("id"))
            else:
                data["lyrics"] = None

            # Process copyright text
            data["copyright_text"] = data.get("copyright_text", "").replace(
                "&copy;", "©"
            )
            return data
        except Exception as e:
            logger.warning("Error formatting song data (skipping track): %s", e)
            return None

    async def search_songs(
        self, query: str, include_lyrics: bool = False, full_data: bool = True
    ) -> List[Dict]:
        """
        Search for songs on Saavn concurrently with caching.
        """
        cache_key = f"{query}:{include_lyrics}:{full_data}"
        if cache_key in self.search_cache:
            return list(self.search_cache[cache_key])

        try:
            search_url = f"{self.BASE_URL}?__call=autocomplete.get&_format=json&_marker=0&cc=in&includeMetaTags=1&query={query}"
            response = await self.client.get(search_url)

            # Process response
            response_text = response.text.encode().decode("unicode-escape")
            response_text = re.sub(r'\(From "([^"]+)"\)', r"(From '\1')", response_text)

            try:
                search_results = json.loads(response_text)
            except json.JSONDecodeError as e:
                logger.error("Failed to parse JSON for search query '%s': %s", query, e)
                return []

            song_results = search_results.get("songs", {}).get("data", [])

            if not full_data:
                # Basic formatting for lightweight response
                formatted_results = []
                for song in song_results:
                    try:
                        formatted = await self.format_song_data(
                            song, include_lyrics=False
                        )
                        if formatted and formatted.get("media_url"):
                            formatted_results.append(formatted)
                    except Exception as e:
                        logger.warning("Failed to format basic song data: %s", e)
                        continue
                self.search_cache[cache_key] = formatted_results
                return list(formatted_results)

            # Full Data: Gather all song details concurrently
            tasks = [
                self.get_song(song["id"], include_lyrics)
                for song in song_results
                if "id" in song
            ]
            songs = await asyncio.gather(*tasks, return_exceptions=True)

            # Filter out None values and exceptions from gather
            valid_songs = []
            for s in songs:
                if isinstance(s, dict) and s.get("media_url"):
                    valid_songs.append(s)

            self.search_cache[cache_key] = valid_songs
            return list(valid_songs)

        except Exception as e:
            logger.error("Song search error: %s", e)
            return []
