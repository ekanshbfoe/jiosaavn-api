import asyncio
import aiohttp
import time
import sys

# ANSI escape codes for colors
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
RESET = "\033[0m"

BASE_URL = "http://127.0.0.1:8000"


def print_pass(msg):
    print(f"{GREEN}[PASS]{RESET} {msg}")


def print_fail(msg):
    print(f"{RED}[FAIL]{RESET} {msg}")


def print_info(msg):
    print(f"{CYAN}[INFO]{RESET} {msg}")


async def test_health_check(session):
    print_info("Running Health Check Test...")
    url = f"{BASE_URL}/ping"
    try:
        async with session.get(url) as response:
            if response.status != 200:
                print_fail(f"Health check failed with status {response.status}")
                return False
            data = await response.json()
            if data.get("status") != "healthy":
                print_fail(
                    f"Health check failed: expected status 'healthy', got {data.get('status')}"
                )
                return False
            print_pass("Health check passed.")
            return True
    except Exception as e:
        print_fail(f"Health check failed with exception: {e}")
        return False


async def test_search_and_extract(session):
    print_info("Running Search & Payload Extraction Test...")
    url = f"{BASE_URL}/song/?query=Amplifier&lyrics=false&songdata=true"
    start_time = time.time()
    try:
        async with session.get(url) as response:
            latency_ms = (time.time() - start_time) * 1000
            print_info(f"Search request latency: {latency_ms:.2f} ms")
            if response.status != 200:
                print_fail(f"Search request failed with status {response.status}")
                text = await response.text()
                print_info(f"Response payload:\n{text}")
                return False, None

            # Use content_type=None in case the server returns unexpected content type but still JSON
            data = await response.json(content_type=None)

            if not isinstance(data, list) or len(data) == 0:
                print_fail("Search response is empty or not a list")
                print_info(f"Response payload:\n{data}")
                return False, None

            song = data[0]
            extracted = {
                "song": song.get("song"),
                "primary_artists": song.get("primary_artists"),
                "duration": song.get("duration"),
                "image": song.get("image"),
                "media_url": song.get("media_url"),
            }

            missing = [k for k, v in extracted.items() if not v]
            if missing:
                print_fail(f"Missing fields in song payload: {missing}")
                print_info(f"Payload:\n{song}")
                return False, None

            print_pass("Search & Payload Extraction passed.")
            print_info("Extracted data:")
            for k, v in extracted.items():
                print(f"  {k}: {v}")
            return True, extracted.get("media_url")
    except Exception as e:
        print_fail(f"Search request failed with exception: {e}")
        return False, None


async def test_cdn_readiness(session, media_url):
    print_info("Running Telegram Inline CDN Readiness Test...")
    if not media_url:
        print_fail("No media_url provided to test")
        return False

    try:
        async with session.head(media_url, allow_redirects=True) as response:
            if response.status != 200:
                print_fail(
                    f"CDN readiness test failed with status {response.status} for URL: {media_url}"
                )
                return False

            content_length = response.headers.get("Content-Length")
            content_type = response.headers.get("Content-Type")

            if not content_length or int(content_length) <= 0:
                print_fail("Content-Length is missing or <= 0")
                return False

            if not content_type or not content_type.startswith("audio/"):
                print_fail(f"Invalid Content-Type: {content_type}")
                return False

            print_pass(
                f"CDN Readiness passed. Content-Type: {content_type}, Content-Length: {content_length}"
            )
            return True
    except Exception as e:
        print_fail(f"CDN Readiness test failed with exception: {e}")
        return False


async def fetch_song(session, query):
    url = f"{BASE_URL}/song/?query={query}&lyrics=false&songdata=false"
    start = time.time()
    try:
        async with session.get(url) as response:
            latency = (time.time() - start) * 1000
            status = response.status
            # read to consume response
            await response.read()
            return {
                "query": query,
                "status": status,
                "latency": latency,
                "success": status == 200,
            }
    except Exception as e:
        return {
            "query": query,
            "status": "Error",
            "latency": (time.time() - start) * 1000,
            "success": False,
            "error": str(e),
        }


async def test_concurrency(session):
    print_info("Running Concurrency & Throughput Benchmark...")
    queries = [
        "Despacito",
        "Shape of You",
        "Blinding Lights",
        "Dance Monkey",
        "Rockstar",
        "Sunflower",
        "One Dance",
        "Closer",
        "Believer",
        "Perfect",
        "Say You Won't Let Go",
        "Thinking Out Loud",
        "God's Plan",
        "Lucid Dreams",
        "Senorita",
    ]

    start_time = time.time()
    tasks = [fetch_song(session, q) for q in queries]
    results = await asyncio.gather(*tasks)
    total_time = (time.time() - start_time) * 1000

    success_count = sum(1 for r in results if r["success"])
    fail_count = len(queries) - success_count

    print_info(f"Concurrency benchmark completed in {total_time:.2f} ms")
    print_info(f"Success: {success_count}/{len(queries)}, Failures: {fail_count}")

    latencies = [r["latency"] for r in results if r["success"]]
    if latencies:
        avg_latency = sum(latencies) / len(latencies)
        print_info(f"Average latency for successful requests: {avg_latency:.2f} ms")
        print_info(
            f"Min latency: {min(latencies):.2f} ms | Max latency: {max(latencies):.2f} ms"
        )

    if fail_count > 0:
        print_fail("Some concurrent requests failed:")
        for r in results:
            if not r["success"]:
                print(
                    f"  {r['query']}: Status {r['status']}, Error: {r.get('error', 'N/A')}"
                )
        return False

    print_pass("Concurrency benchmark passed.")
    return True


async def main():
    async with aiohttp.ClientSession() as session:
        print("========================================")
        print("      JioSaavn API Test Suite")
        print("========================================\n")

        health_ok = await test_health_check(session)
        print("")

        search_ok, media_url = await test_search_and_extract(session)
        print("")

        cdn_ok = False
        if search_ok and media_url:
            cdn_ok = await test_cdn_readiness(session, media_url)
        else:
            print_info("Skipping CDN Readiness Test due to previous failures.")
        print("")

        concurrency_ok = await test_concurrency(session)
        print("")

        print("========================================")
        print("      Test Suite Summary")
        print("========================================")
        print(f"Health Check:           {'[PASS]' if health_ok else '[FAIL]'}")
        print(f"Search & Extraction:    {'[PASS]' if search_ok else '[FAIL]'}")
        print(f"CDN Readiness:          {'[PASS]' if cdn_ok else '[FAIL]'}")
        print(f"Concurrency:            {'[PASS]' if concurrency_ok else '[FAIL]'}")

        if all([health_ok, search_ok, cdn_ok, concurrency_ok]):
            print(f"\n{GREEN}ALL TESTS PASSED!{RESET}")
            sys.exit(0)
        else:
            print(f"\n{RED}SOME TESTS FAILED!{RESET}")
            sys.exit(1)


if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
