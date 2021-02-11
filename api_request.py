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
        self._query = self.parser(question)
        print(self._query)
        self._gmap_response = self.gmap_request()

        if (self._gmap_response == GRUMPY_GRANDPY_NO_GMAP_RESULT):
            self._wiki_response = GRUMPY_GRANDPY_NO_DESCRIPTION
        else:
            self._wiki_response = self.wiki_request()

        self.json = Response(self._gmap_response, self._wiki_response).json
        print("json:", self.json)

    # Parser
    def parser(self, question):
        """ Cut the question into chunks who are stop words
        or who were inserted beween stop word.
        Then, extract the last three expressions."""

        # Initialize the list of chunks
        self._chunks = [' ' + question.lower()]
        for SW in STOP_WORDS:
            alternatives_stop_words = self._expand_safe_word(SW)
            for asw in alternatives_stop_words:
                self._chunks = self._split_question(asw)
        return self._extract_query()

    def _expand_safe_word(self, sw):
        """ List all variants of possibily encountered stop word."""
        return [
            sw.join([' ', ' ']),
            sw.join([' ', ',']),
            sw.join([' ', '.'])
        ]

    def _split_question(self, stop_word):
        """recursively split a question into a list of a specific stop word
        and words bteween two stop words."""
        new_chunks = self._chunks.copy()
        count = 0
        for c in self._chunks:
            c_chunks = c.split(stop_word)
            c_chunks = self._aerate_chunks(c_chunks)
            c_chunks = self._intercalate_stop_word(c_chunks, stop_word)
            c_chunks = self._delete_extra_chunk(c_chunks)
            new_chunks, count = self._integrate_chunks(
                c_chunks, new_chunks, count)
        return new_chunks

    def _aerate_chunks(self, c_chunks):
        if len(c_chunks) != 1:
            c_chunks = (
                [''.join([c_chunks[0], ' '])]
                + [''.join([' ', s, ' ']) for s in c_chunks[1:-1]]
                + [''.join([' ', c_chunks[-1]])]
            )
        return c_chunks

    def _intercalate_stop_word(self, c_chunks, stop_word):
        alt_c_chunks = [None]*(len(c_chunks*2))
        alt_c_chunks[::2] = c_chunks
        alt_c_chunks[1::2] = [stop_word]*len(c_chunks)
        return alt_c_chunks

    def _delete_extra_chunk(self, c_chunks):
        if c_chunks[-2] == "":
            c_chunks = c_chunks[:-2]
        else:
            c_chunks = c_chunks[:-1]
        
        if c_chunks[0] == "":
            c_chunks = c_chunks[1:]
        return c_chunks

    def _integrate_chunks(self, c_chunks, new_chunks, count):
        new_chunks = new_chunks[:count] + c_chunks + new_chunks[count + 1:]
        count += len(c_chunks)
        return new_chunks, count

    def _extract_query(self):
        print (self._chunks)
        if len(self._chunks) >= 3:
            return ' '.join(c.strip() for c in self._chunks[-3:])
        else:
            return ' '.join(c.strip() for c in self._chunks)

    # Google Maps API requests
    def gmap_request(self):
        """Request google map for finding the place asked in the query."""
        url = self._get_places_url()
        print(url)
        results = self._get_gmap_results(url)
        results = self._check_places_results(results)

        if results != GRUMPY_GRANDPY_NO_GMAP_RESULT:
            geo_url = self._get_geocoding_url(results["formatted_address"])
            geo_results = self._get_gmap_results(geo_url)
            results["position"] = self._check_geocoding_results(geo_results)
        return results

    def _get_places_url(self):
        params = urllib.parse.urlencode({
            "input": self._query,
            "key": API_KEY,
            "inputtype": "textquery",
            "fields": "formatted_address,name"
            })
        return f"{self.PLACE_BASE_URL}?{params}"

    def _get_gmap_results(self, url):
        """ Get the API response and corresponding result."""
        current_delay = self.INITIAL_GMAP_DELAY
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
            current_delay = self._wait(current_delay)

    def _wait(self, current_delay):
        print("Waiting", current_delay, "seconds before retrying.")
        time.sleep(current_delay)
        return current_delay * 2  # Increase the delay each time we retry.

    def _check_places_results(self, results):
        if self._if_results(results):
            return results["candidates"][0]
        else:
            return GRUMPY_GRANDPY_NO_GMAP_RESULT

    def _if_results(self, results):
        return (type(results) == dict 
            and results["status"] == "OK"
            and "candidates" in results)

    def _get_geocoding_url(self, address):
        params = urllib.parse.urlencode({
            "address": address,
            "key": API_KEY
            })
        return f"{self.GEO_BASE_URL}?{params}"

    def _if_position(self, geo_results):
        return (type(geo_results) == dict
            and "results" in geo_results
            and "geometry" in geo_results["results"][0]
            and "location" in geo_results["results"][0]["geometry"])

    def _check_geocoding_results(self, geo_results):
        if self._if_position(geo_results):
            return geo_results["results"][0]["geometry"]["location"]
        else:
            return {"lat": 0, "lng": 0}

    # WikiMedia API request
    def wiki_request(self):
        """Request WikiMedia for additional information
        about the place found on google Map."""
        page = self._find_page()
        if page.summary == '':
            return GRUMPY_GRANDPY_NO_DESCRIPTION
        else:
            return {
                "desc": self._extract_info(page.summary),
                "link": page.fullurl
            }

    def _find_page(self):
        wiki_fr = Wiki('fr')
        page = wiki_fr.page(self._gmap_response['name'])
        if not page.exists():
            page = wiki_fr.page(self._query)
        return page

    def _extract_info(self, summary):
        split_summary = summary.split('. ')
        if len(split_summary[0]) > self.LEN_LONG_DESC:
            return self._cut_info(split_summary[0])
        else:
            return self._resume_info(split_summary)

    def _cut_info(self, info):
        # if a one-phrase intro is too long,
        # delete all parts into parenthesis.
        while '(' in info:
            info = info.partition(' (')[0] + info.partition(')')[-1]
        if len(info) > 255:
            # if it is still too long, cut at the first semi-colon if exist.
            info = info.partition(';')[0]
        # if there is no semi-colon, accept the length.
        return info

    def _resume_info(self, split_summary):
        info = split_summary[0]
        for sentence in split_summary[1:]:
            augmented_info = '. '.join([info, sentence])
            if len(augmented_info) > self.LEN_LONG_DESC:
                break
            info = augmented_info

        return self._info_with_dot(info)

    def _info_with_dot(self, info):
        if info[-1] != '.':
            return info + '.'
        else:
            return info