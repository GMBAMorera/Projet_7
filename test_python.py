import urllib.request
from wikipediaapi import Wikipedia as Wiki
import json
from time import time
import pytest
from io import BytesIO
from os import environ

from api_request import ApiRequest
from response import Response
from constants import (GRUMPY_GRANDPY_NO_GMAP_RESULT, GRUMPY_GRANDPY_NO_DESCRIPTION,
    MOCKSUMMARY, MOCKURL, MOCKREQUEST, PARSERTEST1, PARSERTEST2, PARSERTEST3,
    QUERYTEST1, QUERYTEST2, QUERYTEST3, SAFEWORDTEST, EXPANDSAFEWORDTEST,
    CHUNKTEST, SAFEWORDCHUNKTEST, FIRSTCHUNKTEST, UNAERATEDCHUNKS, AERATEDCHUNKS,
    UNINTERCALATEDCHUNKS, INTERCALATEDCHUNKS, UNDELETEDCHUNKS1, DELETEDCHUNKS1,
    UNDELETEDCHUNKS2, DELETEDCHUNKS2, CHUNKSTOINTEGRATE, CHUNKSWHEREINTEGRATE,
    INTEGRATEDCHUNKS, POSCHUNKS, NEWPOSCHUNKS, CHUNKSBEFOREQUERY1, QUERYAFTERCHUNKS1,
    CHUNKSBEFOREQUERY2, QUERYAFTERCHUNKS2, TESTGMAPRESPONSE, TESTQUERY, TESTPLACESURL,
    PLACESRESPONSE1, PLACESRESULT1, PLACESRESPONSE2, PLACESRESPONSE3, PLACESRESPONSE4,
    ADDRESS, GEOCODINGURL, GEORESPONSE1, GEORESULT1, GEORESPONSE2, GEORESULT2,
    GEORESPONSE3, GEORESPONSE4, GEORESPONSE5, MOCKWIKIRESPONSE, REALLYLONGSENTENCE,
    LESSLONGSENTENCE, SPLITSUMMARY, ADDRESS2, GRUMPY_GRANDPY_NO_RESULT, RESUMESUMMARY)
### ApiRequest ###

class MockPage:

    def __init__(self):
        self.summary = MOCKSUMMARY
        self.fullurl = MOCKURL

    @staticmethod
    def exists():
        return True

@pytest.fixture(autouse=True)
def mock_requests(monkeypatch):

    def mock_urlopen(url):
        return BytesIO(json.dumps(MOCKREQUEST).encode())

    def mock_wiki(wiki, name):
        return MockPage()

    monkeypatch.setattr(urllib.request, 'urlopen', mock_urlopen)
    monkeypatch.setattr(Wiki, 'page', mock_wiki)

class TestApiRequest:

    def setup_method(self, method):
        if method == self.test_parser_2:
            self.req = ApiRequest(PARSERTEST2)
        elif method == self.test_parser_3:
            self.req = ApiRequest(PARSERTEST3)
        else:
            self.req = ApiRequest(PARSERTEST1)

        self.response = Response(self.req._gmap_response, self.req._wiki_response)

    ### Apirequest Class ###

    # Parser
    def test_parser_1(self):
        assert self.req._query == QUERYTEST1
        
    def test_parser_2(self):
        assert self.req._query == QUERYTEST2
        
    def test_parser_3(self):
        assert self.req._query == QUERYTEST3

    ## Parser submethods
    def test__expand_safe_words(self):
        assert self.req._expand_safe_word(SAFEWORDTEST) == EXPANDSAFEWORDTEST

    def test__split_question(self):
        self.req._chunks = CHUNKTEST
        assert self.req._split_question(SAFEWORDCHUNKTEST) == FIRSTCHUNKTEST

    def test__aerate_chunks(self):
        assert self.req._aerate_chunks(UNAERATEDCHUNKS) == AERATEDCHUNKS
    
    def test__intercalate_stop_words(self):
        assert self.req._intercalate_stop_word(UNINTERCALATEDCHUNKS, SAFEWORDCHUNKTEST) == INTERCALATEDCHUNKS

    def test__delete_extra_chunks_1(self):
        assert self.req._delete_extra_chunk(UNDELETEDCHUNKS1) == DELETEDCHUNKS1

    def test__delete_extra_chunks_2(self):
        assert self.req._delete_extra_chunk(UNDELETEDCHUNKS2) == DELETEDCHUNKS2

    def test__integrate_chunks(self):
        assert self.req._integrate_chunks(CHUNKSTOINTEGRATE, CHUNKSWHEREINTEGRATE, POSCHUNKS) == (INTEGRATEDCHUNKS, NEWPOSCHUNKS)
    
    def test__extract_query_1(self):
        self.req._chunks = CHUNKSBEFOREQUERY1
        assert self.req._extract_query() == QUERYAFTERCHUNKS1

    def test__extract_query_2(self):
        self.req._chunks = CHUNKSBEFOREQUERY2
        assert self.req._extract_query() == QUERYAFTERCHUNKS2

    # Google Maps requests
    def test_gmap_request(self):
        assert self.req._gmap_response == TESTGMAPRESPONSE

    ## Google maps requests submethods
    def test__get_places_url(self):
        self.req._query = TESTQUERY
        assert self.req._get_places_url() == TESTPLACESURL.format(environ['API_KEY'])

    def test__get_gmap_results(self):
        url = TESTPLACESURL
        assert self.req._get_gmap_results(url) == MOCKREQUEST

    def test__wait1(self):
        current_delay = 2
        assert self.req._wait(current_delay) == 4

    def test__wait2(self):
        current_delay = 2
        start = time()
        self.req._wait(current_delay)
        elapsed_time = time() - start
        assert abs(elapsed_time - current_delay) < 0.1

    def test__check_places_result_1(self):
        assert self.req._check_places_results(PLACESRESPONSE1) == PLACESRESULT1

    def test__check_places_result_2(self):
        assert self.req._check_places_results(PLACESRESPONSE2) == GRUMPY_GRANDPY_NO_GMAP_RESULT

    def test__if_results_1(self):
        assert self.req._if_results(PLACESRESPONSE1)

    def test__if_results_2(self):
        assert not self.req._if_results(PLACESRESPONSE2)

    def test__if_results_3(self):
        assert not self.req._if_results(PLACESRESPONSE3)

    def test__if_results_4(self):
        assert not self.req._if_results(PLACESRESPONSE4)

    def test__get_geocoding_url(self):
        assert self.req._get_geocoding_url(ADDRESS) == GEOCODINGURL.format(environ['API_KEY'])

    def test__check_geocoding_results_1(self):
        assert self.req._check_geocoding_results(GEORESPONSE1) == GEORESULT1

    def test__check_geocoding_results_2(self):
        assert self.req._check_geocoding_results(GEORESPONSE2) == GEORESULT2

    def test__if_position_1(self):
        assert self.req._if_position(GEORESPONSE1)

    def test__if_position_2(self):
        assert not self.req._if_position(GEORESPONSE2)

    def test__if_position_3(self):
        assert not self.req._if_position(GEORESPONSE3)

    def test__if_position_4(self):
        assert not self.req._if_position(GEORESPONSE4)

    def test__if_position_5(self):
        assert not self.req._if_position(GEORESPONSE5)

    # WikiMedia API
    def test__wiki_request(self):
        assert self.req._wiki_response == MOCKWIKIRESPONSE

    ## WikiMedia API submethods

    def test__find_page_1(self):
        assert self.req._find_page().exists(), MockPage().exists()

    def test__find_page_2(self):
        assert self.req._find_page().summary, MockPage().summary

    def test__find_page_3(self):
        assert self.req._find_page().fullurl, MockPage().fullurl

    def test__extract_info(self):
        assert self.req._extract_info(MOCKSUMMARY) == MOCKSUMMARY

    def test__cut_info(self):

        assert self.req._cut_info(REALLYLONGSENTENCE) == LESSLONGSENTENCE

    def test__resume_info(self):
        assert self.req._resume_info(SPLITSUMMARY) == RESUMESUMMARY

    ### Response class ###

    def test__response_1(self):
        assert "short" in self.response._response

    def test__response_2(self):
        assert ADDRESS2 in self.response._response["short"]

    def test__response_3(self):
        intro_index = self.response._response["short"].rfind(" " + ADDRESS2)
        intro = self.response._response["short"][:intro_index]
        assert intro in self.response.SHORT_INTRO

    def test__response_4(self):
        assert "long" in self.response._response

    def test__response_5(self):
        assert MOCKSUMMARY in self.response._response["long"]

    def test__response_6(self):
        intro_index = self.response._response["long"].rfind(" " + MOCKSUMMARY)
        intro = self.response._response["long"][:intro_index]
        assert intro in self.response.LONG_INTRO

    def test__response_7(self):
        assert self.response._response["link"]["text"] == self.response.LINK_TEXT

    def test__response_8(self):
        assert self.response._response["link"]["href"] == MOCKURL

    def test_response_9(self):
        assert self.response._response["position"] == GEORESULT2

    def test_response_10(self):
        grumpy_response = Response(GRUMPY_GRANDPY_NO_GMAP_RESULT, GRUMPY_GRANDPY_NO_DESCRIPTION)
        assert grumpy_response._response == GRUMPY_GRANDPY_NO_RESULT