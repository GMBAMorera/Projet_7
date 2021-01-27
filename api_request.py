import json
import time
import urllib.error
import urllib.parse
import urllib.request


class ApiRequest:
    API_KEY = "YOUR_KEY_HERE"
    PLACE_BASE_URL = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json"

    def __init__(self, question):
        first_result = self.place_request(question)

    def place_request(self, question):
        # Join the parts of the URL together into one string.
        params = urllib.parse.urlencode(
            {"input": question, "key": self.API_KEY, "inputtype": "textquery", "fields":"formatted_adress,name,place_id,icon"}
        )
        url = f"{self.PLACE_BASE_URL}?{params}"

        current_delay = 0.1  # Set the initial retry delay to 100ms.
        max_delay = 5  # Set the maximum retry delay to 5 seconds.

        while True:
            try:
                # Get the API response.
                response = urllib.request.urlopen(url)
            except urllib.error.URLError:
                pass  # Fall through to the retry loop.
            else:
                # If we didn't get an IOError then parse the result.
                result = json.load(response)

                if result["status"] == "OK":
                    return result["candidates"][0]
                elif result["status"] != "UNKNOWN_ERROR":
                    # Many API errors cannot be fixed by a retry, e.g. INVALID_REQUEST or
                    # ZERO_RESULTS. There is no point retrying these requests.
                    raise Exception(result["error_message"])

            if current_delay > max_delay:
                raise Exception("Too many retry attempts.")

            print("Waiting", current_delay, "seconds before retrying.")

            time.sleep(current_delay)
            current_delay *= 2  # Increase the delay each time we retry.
