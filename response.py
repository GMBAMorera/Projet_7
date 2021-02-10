import json
from constants import GRUMPY_GRANDPY_NO_DESCRIPTION, GRUMPY_GRANDPY_NO_GMAP_RESULT

class Response:
    SHORT_INTRO = "Bien sûr mon poussin! La voici: "
    LINK_TEXT = "[En savoir plus sur Wikipedia]"
    def __init__(self, gmap, wiki):
        if gmap == GRUMPY_GRANDPY_NO_GMAP_RESULT:
            short = "Grmbl! Je suis un peu sourd avec l'âge, peux-tu répéter?",
            position = {
                "lat": 0,
                "lng": 0
            }
        else:
            short = "".join([self.SHORT_INTRO, gmap["formatted_address"]]),
            position = gmap["position"]

        if wiki == GRUMPY_GRANDPY_NO_DESCRIPTION:
            long_desc = "Je ne vois pas de quoi tu parles. Cela peut-être dû à une mauvaise orthographe, à une tournure trop compliquée ou simplement à une connexion difficile avec ma mémoire...",
            text_link = "",
            href_link = "",
        else:
            long_desc =  wiki["desc"],
            text_link = self.LINK_TEXT,
            href_link = wiki["link"],
        self.json = self._make_response(short, position, long_desc, text_link, href_link)

    def _make_response(self, short, position, long_desc, text_link, href_link):
        response_dict = {
            "short": short,
            "long": long_desc,
            "link": {
                "text": text_link,
                "href": href_link
            },
            "position": position
        }
        return json.dumps(response_dict)

        