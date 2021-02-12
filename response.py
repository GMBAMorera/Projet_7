import json
from random import randint
from constants import GRUMPY_GRANDPY_NO_DESCRIPTION, GRUMPY_GRANDPY_NO_GMAP_RESULT

class Response:
    SHORT_INTRO = [
        "Bien sûr mon poussin! La voici:",
        "La voilà mon chou:",
        "Tout pour te faire plaisir:",
        "Ces jeunes, incapables de chercher par eux-mêmes...",
        "Tiens, et n'oublie pas d'aller t'acheter des bonbons."
    ]
    LONG_INTRO = [
        "Mais t'ai-je déjà raconté l'histoire de ce quartier qui m'a vu en culottes courtes ?",
        "Ah, tant de souvenirs me remontent. Laisse-moi te raconter.",
        "Ils en ont vu de belles, les bancs de cette belle ville. Tiens, écoute.",
        "Alors comme ça tu veux en savoir plus?",
        "C'est gentil, d'écouter son vieux grand-père. Savais-tu que"
    ]
    LINK_TEXT = "[En savoir plus sur Wikipedia]"
    NO_GMAP = {
        "short": "Grmbl! Je suis un peu sourd avec l'âge, peux-tu répéter?",
        "position": {"lat": 0, "lng": 0}
    }
    NO_DESC = {
        "long_desc": "Je ne vois pas de quoi tu parles. Cela peut-être dû à une mauvaise orthographe, à des caractères pas très français, à une tournure trop compliquée ou simplement à une connexion difficile avec ma mémoire...",
        "text_link": "",
        "href_link": ""
    }

    def __init__(self, gmap, wiki):
        all_description = self._extract_desc(gmap, wiki)
        self._response = self._make_response(*all_description)
        self.json = json.dumps(self._response)

    def _extract_desc(self, gmap, wiki):
        if gmap == GRUMPY_GRANDPY_NO_GMAP_RESULT:
            short = self.NO_GMAP["short"]
            position = self.NO_GMAP["position"]
        else:
            short = self._pick_intro(self.SHORT_INTRO, gmap["formatted_address"])
            position = gmap["position"]

        if wiki == GRUMPY_GRANDPY_NO_DESCRIPTION:
            long_desc = self.NO_DESC["long_desc"]
            text_link = self.NO_DESC["text_link"]
            href_link = self.NO_DESC["href_link"]
        else:
            long_desc = self._pick_intro(self.LONG_INTRO, wiki["desc"])
            text_link = self.LINK_TEXT
            href_link = wiki["link"]
        return short, position, long_desc, text_link, href_link

    def _pick_intro(self, all_intro, body):
        length = len(all_intro)
        pos = randint(1, length) - 1
        intro = all_intro[pos]
        return " ".join([intro, body])

    def _make_response(self, short, position, long_desc, text_link, href_link):
        return {
            "short": short,
            "long": long_desc,
            "link": {
                "text": text_link,
                "href": href_link
            },
            "position": position
        }

        