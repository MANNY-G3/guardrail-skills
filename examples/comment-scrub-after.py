import time
import urllib.request


# The upstream sometimes answers 503 for a minute or two, so retry before giving up.
def fetch_with_retry(url, attempts=3):
    delay = 1
    for attempt in range(attempts):
        try:
            with urllib.request.urlopen(url, timeout=10) as response:
                return response.read()
        except OSError:
            if attempt == attempts - 1:
                raise
            time.sleep(delay)
            # The upstream rate limiter bans clients that retry more than once a second.
            delay *= 2
