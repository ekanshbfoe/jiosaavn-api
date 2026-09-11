# JioSaavn API

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-yellow.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/release/python-3110/)
[![FastAPI](https://img.shields.io/badge/fastapi-0.115.6-green)](https://fastapi.tiangolo.com/)

A high-performance unofficial API for JioSaavn, written in Python using the FastAPI framework. This API allows you to fetch DRM-free songs, cover art, lyrics, albums, playlists, artist information, and more.

## Tech Stack

* **Language:** Python3
* **Framework:** FastAPI
* **Libraries:**
    * `httpx`: For making non-blocking asynchronous HTTP requests to the JioSaavn website.
    * `cachetools`: For in-memory TTL caching of repeat queries to reduce latency.
    * `pyDes`: For decrypting encrypted media URLs.
    * `pydantic`: For data validation and serialization.
    * `fastapi`: For building the API.
    * `uvicorn`: For serving the API. 
    * `markdown`: For rendering the README.md in the browser.

## Architecture Overview

This API interacts with the JioSaavn website by scraping data and utilizing undocumented APIs. It then processes and formats the retrieved data, including decrypting media URLs, to provide a clean and consistent JSON response.

**Data Flow:**

1. **Request:** A client sends a request to a specific API endpoint (e.g., `/song/`).
2. **Fetch:** The API sends a request to the JioSaavn website to retrieve the relevant data.
3. **Process:** The API processes the raw data, extracts necessary information, and formats it. This may include decrypting media URLs using `pyDes` and cleaning up strings.
4. **Response:** The API returns the processed data as a JSON response to the client.

## Design Choices

* **FastAPI:** Chosen for its speed, ease of use, and built-in features like automatic documentation generation.
* **pydantic:** Used for data validation and serialization, ensuring data integrity and consistency.
* **Asynchronous Requests:** Using `httpx.AsyncClient` with `asyncio.gather` for native, non-blocking asynchronous calls. This ensures FastAPI's event loop is never blocked, drastically reducing latency under load.

## Getting Started

1. **Clone the repository:**
   ```bash
   git clone https://github.com/anxkhn/jiosaavn-api
   ```

2. **Navigate to the project directory:**
   ```bash
   cd jiosaavn-api
   ```

3. **Run the application:**

   You have two options for running the application:

   - **Option 1: Run directly using FastAPI**
   
     Install the dependencies and run the application using FastAPI (without Docker):
     ```bash
     pip install -r requirements.txt
     fastapi dev main.py
     ```

   - **Option 2: Run the application using Docker**
   
     Alternatively, you can run the application in Docker using Docker Compose:
     ```bash
     docker-compose up --build
     ```

4. **Access the application:**

   After running the application, you can access the following documentation pages:

   - Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
   - ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)

   You can also visit the app directly at `http://0.0.0.0:8000`.

## API Endpoints


## **Songs:**

### **`/song/`:** Search for songs.
  - **Query Parameters:**
    - `query`: Search term for finding songs (required).
    - `lyrics`: Include song lyrics in the response (optional, default: False).
    - `songdata`: Fetch full song details or basic information (optional, default: True).

### Example of a Song Response

Curl

```sh
curl -X 'GET' \
  'http://localhost:8000/song/?query=Chammak%20Challo&lyrics=false&songdata=true' \
  -H 'accept: application/json'
```

Request URL

```sh
http://localhost:8000/song/?query=Chammak%20Challo&lyrics=false&songdata=true
```


The response will contain details about the song "Chammak Challo" from the album *Ra-One*:

```json
[
  {
    "id": "Fy1Afntv",
    "type": "",
    "song": "Chammak Challo",
    "album": "Ra-One",
    "year": "2011",
    "music": "Vishal & Shekhar",
    "music_id": "459880",
    "primary_artists": "Vishal & Shekhar, Akon",
    "primary_artists_id": "459880, 483645",
    "featured_artists": "",
    "featured_artists_id": "",
    "singers": "Akon",
    "starring": "Kareena Kapoor Khan, Arjun Rampal, Shah Rukh Khan",
    "image": "https://c.saavncdn.com/026/Ra-One-Hindi-2011-500x500.jpg",
    "label": "T-Series",
    "albumid": "1044026",
    "language": "hindi",
    "origin": "none",
    "play_count": 46741633,
    "is_drm": 1,
    "copyright_text": "©  2011 T-Series",
    "320kbps": "true",
    "is_dolby_content": false,
    "explicit_content": 0,
    "has_lyrics": "true",
    "lyrics_snippet": "Kaisa sharmana aaja nach ke dikha de",
    "encrypted_drm_media_url": "ID2ieOjCrwdjlkMElYlzWCptgNdUpWD8xydJt7j6jXEdgCPneyZNojdeP8sog1HrHQ1ju7mPTY4iVo7ihHTYTo92mytrdt3FDnQW0nglPS4=",
    "encrypted_media_url": "ID2ieOjCrwfgWvL5sXl4B1ImC5QfbsDyEQ4rHVh0RMokzViB7agvK6ObqSdeDpzjWYUvjJuwilxeDkUt1t4NVxw7tS9a8Gtq",
    "encrypted_media_path": "NMKyboFo/Fi2SD0aWempyWwikK8l2oSw5GbkRrzcQETj7mZn3xcsGdeEuYbCUYfB",
    "media_preview_url": "https://preview.saavncdn.com/026/3W5heJ12fDeGr8uk8P6oWqULYijpVLh1l5Q5XJ6SLfxZ76_96_p.mp4",
    "perma_url": "https://www.jiosaavn.com/song/chammak-challo/NhFacBJeQ0U",
    "album_url": "https://www.jiosaavn.com/album/ra-one/bcUOpGHj1I4_",
    "duration": "208",
    "rights": {
      "code": 0,
      "reason": "",
      "cacheable": true,
      "delete_cached_object": false
    },
    "webp": false,
    "cache_state": "false",
    "starred": "false",
    "artistMap": {
      "Vishal &amp; Shekhar": "459880",
      "Akon": "483645",
      "Vishal Dadlani": "455669",
      "Niranjan Iyengar": "465066",
      "Kareena Kapoor Khan": "852212",
      "Arjun Rampal": "457647",
      "Shah Rukh Khan": "461361"
    },
    "release_date": "",
    "vcode": "010910090367265",
    "vlink": "https://jiotunepreview.jio.com/content/Converted/010910090380670.mp3",
    "triller_available": false,
    "label_url": "/label/t-series-albums/6DLuXO3VoTo_",
    "label_id": "34297",
    "media_url": "https://aac.saavncdn.com/026/4525eb9287203ed2f7d2abab5eff46bc_320.mp4",
    "lyrics": null
  }
]
```

### **Notes:**
1. **`media_url`**: The **320kbps** decrypted media URL (provides high-quality audio).
2. **`media_preview_url`**: The **96kbps** preview URL (for low-quality preview).

3. There can be a **`.mp4`** extension occasionally in the URLs. It does not denote a video; instead, it is just in .mp4 format with only an audio channel. Endpoints should handle it.



* **`/song/get`:** Retrieve a specific song by its ID.
    * **Query Parameters:**
        * `song_id`: Unique identifier of the song (required).
        * `lyrics`: Include song lyrics in the response (optional, default: False).

**Albums:**

* **`/album/`:** Retrieve album details.
    * **Query Parameters:**
        * `query`: Album URL or ID (required).
        * `lyrics`: Include song lyrics in the response (optional, default: False).

**Playlists:**

* **`/playlist/`:** Retrieve playlist details.
    * **Query Parameters:**
        * `query`: Playlist URL or ID (required).
        * `lyrics`: Include song lyrics in the response (optional, default: False).

**Lyrics:**

* **`/lyrics/`:** Retrieve song lyrics.
    * **Query Parameters:**
        * `query`: Song URL, link, or direct lyrics ID (required).

**Health:**

* **`/ping`:** Health check on all JioSaavn endpoints, including service-specific connectivity statuses.

* **Note:** Kindly ensure all endpoints are working properly before use. Check the health status using the `/ping` endpoint. If everything is functioning correctly, you should receive a response similar to the following:

    ```json
    {
        "msg": "Pong!",
        "status": "healthy",
        "details": [...]
    }
    ```

* **TODO:**
    
    [ ] Enhance the `/ping` endpoint to include more comprehensive testing. This will involve validating actual media data (e.g., fetching and processing song, album, and playlist details) to ensure the full functionality of the services.



## File Structure and Breakdown

```
├── app
│   ├── schemas
│   │   ├── song_schema.py
│   │   ├── playlist_schema.py
│   │   └── album_schema.py
│   ├── services
│   │   ├── saavn_service.py
│   │   └── crypto_service.py
│   ├── routes
│   │   ├── song_routes.py
│   │   ├── playlist_routes.py
│   │   ├── lyrics_routes.py
│   │   └── album_routes.py
│   ├── core
│   │   └── exceptions.py
│   └── config.py
├── test
│   └── test_api.py
├── main.py
├── requirements.txt
└── README.md

```

* **`app/schemas`:** Contains Pydantic models for defining the structure of API responses.
* **`app/services`:** Contains the core logic for interacting with the JioSaavn website and processing data.
    * **`saavn_service.py`:**  Handles fetching and processing data from JioSaavn. Features in-memory caching and graceful error fallback to prevent 500s.
    * **`crypto_service.py`:**  Handles decryption of media URLs.
* **`app/routes`:** Defines the API endpoints and their corresponding handlers.
* **`app/core`:** Contains modules for exception handling and other core functionalities.
* **`app/config.py`:**  Manages application configuration settings.
* **`test/test_api.py`:** An automated health, Telegram inline CDN verification, and concurrency benchmark suite using `aiohttp`.
* **`main.py`:**  The main application file that creates and runs the FastAPI app.
* **`requirements.txt`:** Lists the project dependencies.

## License

This project is licensed under the GNU General Public License v3.0. See the [LICENSE](LICENSE) file for details.
