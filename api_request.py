import json
import time
import urllib.error
import urllib.parse
import urllib.request
from wikipediaapi import Wikipedia as Wiki

from constants import STOP_WORDS
from response import Response


class ApiRequest:
    API_KEY = "AIzaSyDvBP_TNwyA_nlarRZzSBwsFnhyu1gXmrg"
    PLACE_BASE_URL = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json"
    LEN_LONG_DESC = 255

    INITIAL_GMAP_DELAY =  0.1
    MAX_GMAP_DELAY = 5

    GRUMPY_GRANDPY_QUESTION_MARK = "Groumf!"
    GRUMPY_GRANDPY_MAX_ATTEMPT_FAILED = "Ooof!"
    GRUMPY_GRANDPY_UNKNOWN_ERROR = "Marf!"
    GRUMPY_GRANDPY_NO_WIKI_PAGE = "Tsss!"
    GRUMPY_GRANDPY_NO_SUMMARY = 'Aaargh!'

    def __init__(self, question):
        print(question)
        self._query = self.parser(question)
        print(self._query)
        self._gmap_response = self.gmap_request()
        print(self._gmap_response)
        self._wiki_response = self.wiki_request()
        self.json = Response(self._gmap_response, self._wiki_response).json

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
        print(self.chunks)
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
        return (
            self.chunks[-1].strip(),
            ' '.join(
                [self.chunks[-3].strip(),
                self.chunks[-2].strip(),
                self.chunks[-1].strip()]
            )
        )

    def gmap_request(self):
        url = self._get_url()
        result = self._get_gmap_result(url)

        print(result)
        if result["status"] == "OK":
            return result["candidates"][0]
        else:
            return self.GRUMPY_GRANDPY_UNKNOWN_ERROR

    def _get_url(self):
        """ Join the parts of the URL together into one string."""
        params = urllib.parse.urlencode({
            "input": self._query,
            "key": self.API_KEY,
            "inputtype": "textquery", "fields":"formatted_address,name,place_id,icon"
            })
        return f"{self.PLACE_BASE_URL}?{params}"

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
                return self.GRUMPY_GRANDPY_MAX_ATTEMPT_FAILED
            print("Waiting", current_delay, "seconds before retrying.")
            time.sleep(current_delay)
            current_delay *= 2  # Increase the delay each time we retry.

    def wiki_request(self):
        wiki_fr = Wiki('fr')
        page = wiki_fr.page(self._gmap_response['name'])
        if not page.exists():
            return self.GRUMPY_GRANDPY_NO_WIKI_PAGE
        else:
            return {
                "desc": self._extract_info(page.summary),
                "link": page.fullurl
            }

    def _extract_info(self, summary):
        if summary == '':
            return self.GRUMPY_GRANDPY_NO_SUMMARY

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
