import json

class Response:
    SHORT_INTRO = "Bien sûr mon poussin! La voici: "
    LINK_TEXT = "[En savoir plus sur Wikipedia]"
    def __init__(self, gmap, wiki):
        response_dict = {
            "short": "".join([self.SHORT_INTRO, gmap["formatted_address"]]),
            "long": wiki["desc"],
            "link": {
                "text": self.LINK_TEXT,
                "href": wiki["link"]
            },
            "map": gmap["place_id"]
        }
        self.json = json.dumps(response_dict)
        