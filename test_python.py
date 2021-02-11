from api_request import ApiRequest
import urllib.request
import json

from cred import API_KEY
### ApiRequest ###


class TestApiRequest:

    def __init(self, monkeypatch):
        def mockreturn_urlopen(request):
            return {'status': 'ok', 'candidates':[{'formatted_address': 'Place Charles de Gaulle, 75008 Paris, France', 'name': 'Arc de Triomphe'}], 'results':[{'geometry':{'location':{'position':{'lat':0, 'lng':0}}}}]}

        def mockreturn_wikipedia():
            pass

        monkeypatch.setattr(urllib.request, 'urlopen', mockreturn_urlopen)

        self.req = ApiRequest("quel est l'adresse de la ville de Paris?")
        self.req_2 = ApiRequest("Dis-moi, vieille branche, tu peux me dire où se trouve l'arc de triomphe?")
        self.req_3 = ApiRequest("Bon sang! GrandPy, je n'arrive pas à retrouver le département de la ville de Saint Mars la Jaille?")


    # Parser
    def test_parser1(self):
        assert self.req._query == ("ville de Paris")
        
    def test_parser2(self):
        assert self.req_2._query == ("trouve l'arc de triomphe")
        
    def test_parser3(self):
        assert self.req_3._query == ("Saint Mars la Jaille")

    ## Parser submethods

    def test__expand_safe_words(self):
        assert self.req._expand_safe_word("où") == [" où ", " où,", " où."]

    def test__split_question(self):
        self.req._chunks = [" où est donc ornicar? où se situe le canal de Suez? où se loge l'omoplate?"]
        assert self.req._split_question("où") == ["où ", " est donc ornicar? ", " où ", " se situe le canal de Suez? ", " où ", " se loge l'omoplate?"]

    def test__aerate_chunks(self):
        assert self.req._aerate_chunks(["où", "est donc ornicar?", "où", "se situe le canal de Suez?", "où", "se loge l'omoplate?"]) == ["où ", " est donc ornicar? ", " où ", " se situe le canal de Suez? ", " où ", " se loge l'omoplate?"]
    
    def test__intercalate_stop_words(self):
        assert self.req._intercalate_stop_word(["est donc ornicar? ", " se situe le canal de Suez? ", " se loge l'omoplate?"], " où ") == ["est donc ornicar? ", " où ", " se situe le canal de Suez?", " où ", " se loge l'omoplate?"]

    def test__delete_extra_chunks(self):
        assert self.req._delete_extra_chunk(["", " où ", " est donc ornicar? ", " où ", ""]) == [" où ", " est donc ornicar? "]

    def test__integrate_chunks(self):
        assert self.req._integrate_chunks([" où,", " se situe le canal de Suez "],
            [" où ", " est donc ornicar? ", " où, se situe le canal de Suez? ", " où ", " se loge l'omoplate?"],
            2) == [" où ", " est donc ornicar? ", " où,", " se situe le canal de Suez? ", " où ", " se loge l'omoplate?"]
    
    def test__extract_query1(self):
        self.req._chunks = [" où ", " est donc ornicar? "]
        assert self.req._extract_query() == "où est donc ornicar?"

    def test__extract_query2(self):
        self.req._chunks = [" où ", " est donc ornicar? ", " où,", " se situe le canal de Suez? ", " où ", " se loge l'omoplate?"]
        assert self.req._extract_query() == " se situe le canal de Suez? où se loge l'omoplate?"

    # Google Maps requests
    def test_gmap_request(self):
        assert self.req._gmap_response == {'formatted_address': 'Place Charles de Gaulle, 75008 Paris, France', 'name': 'Arc de Triomphe', 'position': {'lat': 0, 'lng': 0}}

    ## Google maps requests
    def test__get_places_url(self):
        self.req._query = "tour eiffel"
        assert self.req._get_place_url() == f"https://maps.googleapis.com/maps/api/place/findplacefromtext/json?input=+tour+eiffel&key={API_KEY}&inputtype=textquery&fields=formatted_address%2Cname"

    def test__get_gmap_results(self):
        url = f"https://maps.googleapis.com/maps/api/place/findplacefromtext/json?input=+tour+eiffel&key={API_KEY}&inputtype=textquery&fields=formatted_address%2Cname"
        assert self.req._get_gmap_results(url) = {'status': 'ok', 'candidates':[{'formatted_address': 'Place Charles de Gaulle, 75008 Paris, France', 'name': 'Arc de Triomphe'}], 'results':[{'geometry':{'location':{'position':{'lat':0, 'lng':0}}}}]}

    # WikiMedia API
    def test_wiki_request(self):
        assert self.req._wiki_response["desc"] == "Un arc de triomphe, et plus généralement un arc monumental, est une structure libre monumentale enjambant une voie et utilisant la forme architecturale de l'arc avec un ou plusieurs passages voûtés"

    # Response class
    def test_response(self):
        assert self.req.json == json.dumps({
            "short": "Bien sûr mon poussin! La voici: Place Charles de Gaulle, 75008 Paris, France",
            "long": "Un arc de triomphe, et plus généralement un arc monumental, est une structure libre monumentale enjambant une voie et utilisant la forme architecturale de l'arc avec un ou plusieurs passages voûtés",
            "link": {
                "text": "[En savoir plus sur Wikipedia]",
                "href": "https://fr.wikipedia.org/wiki/Arc_de_triomphe"
                },
            "map": "ChIJjx37cOxv5kcRPWQuEW5ntdk"
            })
