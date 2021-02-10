import json
import time
import urllib.error
import urllib.parse
import urllib.request
from wikipediaapi import Wikipedia as Wiki

from constants import STOP_WORDS, GRUMPY_GRANDPY_NO_GMAP_RESULT, GRUMPY_GRANDPY_NO_DESCRIPTION
from response import Response
from cred import API_KEY


class ApiRequest:
    PLACE_BASE_URL = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json"
    GEO_BASE_URL = "https://maps.googleapis.com/maps/api/geocode/json"
    LEN_LONG_DESC = 255

    INITIAL_GMAP_DELAY =  0.1
    MAX_GMAP_DELAY = 5
    

    def __init__(self, question):
        question = self.decode(question)
        self._query = self.parser(question)
        print(self._query)
        self._gmap_response = self.gmap_request()

        if (self._gmap_response == GRUMPY_GRANDPY_NO_GMAP_RESULT):
            self._wiki_response = GRUMPY_GRANDPY_NO_DESCRIPTION
        else:
            self._wiki_response = self.wiki_request()

        self.json = Response(self._gmap_response, self._wiki_response).json
        print("json:", self.json)

    def decode(self, question):
        """Decode the question, previously encoded in javascript."""
        return question

    def parser(self, question):
        """ Cut the question into chunks who are stop words
        or who were inserted beween stop word.
        Then, extract the last expression."""

        # Initialize the list of chunks
        self.chunks = [' ' + question]
        for SW in STOP_WORDS:
            alt_sw = self._expand_safe_word(SW)
            for asw in alt_sw:
                self.chunks = self._split_question(asw)
        return self._extract_queries()

    def _expand_safe_word(self, sw):
        """ List all variant of possibily encountered stop word."""
        return [
            sw.join([' ', ' ']),
            sw.join([' ', ',']),
            sw.join([' ', '.'])
        ]

    def _split_question(self, asw):
        """recursively split a question into a list of a specific stop word
        and words bteween two such words."""
        new_chunks = self.chunks.copy()
        count = 0
        for c in self.chunks:
            sw_chunks = self._split_in_chunks(c, asw)
            new_chunks, count = self._integrate_chunks(sw_chunks, asw, new_chunks, count)
        return new_chunks

    def _split_in_chunks(self, c, asw):
        sw_chunks = c.split(asw)
        if len(sw_chunks) != 1:
            sw_chunks = (
                [''.join([sw_chunks[0], ' '])]
                + [''.join([' ', s, ' ']) for s in sw_chunks[1:-1]]
                + [''.join([' ', sw_chunks[-1]])]
            )
        return sw_chunks

    def _integrate_chunks(self, sw_chunks, asw, new_chunks, count):
        pop = self._compute_deleted_char(sw_chunks)

        alt_sw_chunks = [None]*(len(sw_chunks*2))
        alt_sw_chunks[::2] = sw_chunks
        alt_sw_chunks[1::2] = [asw]*len(sw_chunks)
        alt_sw_chunks.pop(pop)

        new_chunks = new_chunks[:count] + alt_sw_chunks + new_chunks[count + 1:]
        count += len(alt_sw_chunks)
        return new_chunks, count

    def _compute_deleted_char(self, sw_chunks):
        if sw_chunks[-1] == "":
            pop = -2
        else:
            pop = -1
        return pop

    def _extract_queries(self):
        if len(self.chunks) >= 3:
            return ' '.join(c.strip() for c in self.chunks[-3:])
        else:
            return ' '.join([c.strip() for c in self.chunks])

    def gmap_request(self):
        """Request google map for finding the place asked in the query."""
        url = self._get_place_url()
        result = self._get_gmap_result(url)

        if result["status"] == "OK":
            if "candidates" in result:
                result = result["candidates"][0]
            else:
                return GRUMPY_GRANDPY_NO_GMAP_RESULT
        else:
            return GRUMPY_GRANDPY_NO_GMAP_RESULT

        geo_url = self._get_geocoding_url(result["formatted_address"])
        position = self._get_gmap_result(geo_url)

        if ("results" not in position
            or "geometry" not in position["results"][0]
            or "location" not in position["results"][0]["geometry"]):
            result["position"] = {"lat": 0, "lng": 0}
        else:
            result["position"] = position["results"][0]["geometry"]["location"]
        return result


    def _get_place_url(self):
        params = urllib.parse.urlencode({
            "input": self._query,
            "key": API_KEY,
            "inputtype": "textquery", "fields":"formatted_address,name"
            })
        return f"{self.PLACE_BASE_URL}?{params}"

    def _get_geocoding_url(self, address):
        params = urllib.parse.urlencode({
            "address": address,
            "key": API_KEY
            })
        return f"{self.GEO_BASE_URL}?{params}"


    def _get_gmap_result(self, url):
        """ Get the API response and corresponding result."""
        current_delay = self.INITIAL_GMAP_DELAY  # Set the initial retry delay to 100ms.
        while True:
            try:
                # Get the API response.
                response = urllib.request.urlopen(url)
            except urllib.error.URLError:
                pass  # Fall through to the retry loop.
            else:
                # If we didn't get an IOError then parse the result.
                result = json.load(response)
                if result["status"] != "UNKNOWN_ERROR":
                    return result

            if current_delay > self.MAX_GMAP_DELAY:
                return GRUMPY_GRANDPY_NO_GMAP_RESULT
            print("Waiting", current_delay, "seconds before retrying.")
            time.sleep(current_delay)
            current_delay *= 2  # Increase the delay each time we retry.

    def wiki_request(self):
        """Request WikiMedia for additional information
        about the place found on google Map."""
        wiki_fr = Wiki('fr')
        page = wiki_fr.page(self._gmap_response['name'])
        if not page.exists():
            return GRUMPY_GRANDPY_NO_DESCRIPTION
        else:
            return {
                "desc": self._extract_info(page.summary),
                "link": page.fullurl
            }

    def _extract_info(self, summary):
        if summary == '':
            return GRUMPY_GRANDPY_NO_DESCRIPTION

        all_info = summary.split('. ')
        info = self._resume_info(all_info)

        if len(all_info) == 1 and len(info) > self.LEN_LONG_DESC:
            info = self._cut_info(info)
        return info

    def _resume_info(self, all_info):
        count = 1
        info = all_info[0]
        while count < len(all_info) and len(info) + len(all_info[count]) < self.LEN_LONG_DESC:
            info = '. '.join([info, all_info[count]])
            count += 1

        if info[-1] != '.':
            info = info + '.'
        return info

    def _cut_info(self, info):
        # if a one-phrase intro is stil too long, cut all parts into parenthesis.
        while '(' in info:
            info = info.partition(' (')[0] + info.partition(')')[-1]
        if len(info) > 255:
            # if it is still too long, cut at the first semi-colon if exist.
            info = info.partition(';')[0]
            # if no semi-colon, accept the length.
        return info