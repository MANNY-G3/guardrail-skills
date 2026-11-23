import time
import urllib.request


# This function fetches a URL with retries.
# It exists because the upstream service sometimes answers 503 for a minute or
# two, and after some discussion we decided the simplest thing was to try a few
# times before giving up, instead of adding a queue or a circuit breaker.
def fetch_with_retry(url, attempts=3):
    # Initialize the delay to 1 second
    delay = 1
    # Loop over the attempts
    for attempt in range(attempts):
        try:
            # Open the URL and return the body
            with urllib.request.urlopen(url, timeout=10) as response:
                return response.read()
        except OSError:
            # Sorry, this is a bit hacky but it works
            if attempt == attempts - 1:
                raise
            # time.sleep(5)
            time.sleep(delay)
            # Double the delay: the upstream rate limiter bans clients that retry more than once a second
            delay *= 2
