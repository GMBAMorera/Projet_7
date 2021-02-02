from api_request import ApiRequest
import json
### ApiRequest ###

# Parser

def test_parser1():
    req = ApiRequest("quel est l'adresse de la ville de Paris?")
    assert req._query == ("Paris", "ville de Paris")
    
def test_parser2():
    req = ApiRequest("Dis-moi, vieille branche, tu peux me dire où se trouve l'arc de triomphe?")
    assert req._query == ("triomphe", "trouve l'arc de triomphe")
    
def test_parser3():
    req = ApiRequest("Bon sang! GrandPy, je n'arrive pas à retrouver le département de la ville de Saint Mars la Jaille?")
    assert req._query == ("Jaille", "Saint Mars la Jaille")

def test_gmap_request():
    req = ApiRequest("quel est l'adresse de l'arc de triomphe?")
    assert req._gmap_response == {'formatted_address': 'Place Charles de Gaulle, 75008 Paris, France', 'icon': 'https://maps.gstatic.com/mapfiles/place_api/icons/v1/png_71/museum-71.png', 'name': 'Arc de Triomphe', 'place_id': 'ChIJjx37cOxv5kcRPWQuEW5ntdk'}

def test_wiki_request():
    req = ApiRequest("quel est l'adresse de l'arc de triomphe?")
    assert req._wiki_response["desc"] == "Un arc de triomphe, et plus généralement un arc monumental, est une structure libre monumentale enjambant une voie et utilisant la forme architecturale de l'arc avec un ou plusieurs passages voûtés"

def test__init__api_request():
    req = ApiRequest("quel est l'adresse de l'arc de triomphe?")
    assert req.json == json.dumps({
        "short": "Bien sûr mon poussin! La voici: Place Charles de Gaulle, 75008 Paris, France",
        "long": "Un arc de triomphe, et plus généralement un arc monumental, est une structure libre monumentale enjambant une voie et utilisant la forme architecturale de l'arc avec un ou plusieurs passages voûtés",
        "link": {
            "text": "[En savoir plus sur Wikipedia]",
            "href": "https://fr.wikipedia.org/wiki/Arc_de_triomphe"
            },
        "map": "ChIJjx37cOxv5kcRPWQuEW5ntdk"
        })
