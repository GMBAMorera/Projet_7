from flask import Flask, render_template, request, url_for
import json

class Main:
    """ This class load the HTML page."""
    def __init__(self):
        self.app = Flask(__name__)
        self.app.add_url_rule('/', 'home', self.home)
        self.app.add_url_rule('/question/<question>', 'req', self.req)

    def home(self):
        return render_template('page.html')

    def req(self, question):
        ans = {
            "short": "Coucou mon lapin. Voici une adresse.",
            "long": "Lettre ayant pour objet une demande, une adhésion, des félicitations, etc., présentées par un corps constitué, par une réunion de citoyens, à une autorité.",
            "link": {
                "text": "[En savoir plus sur Wikipedia]",
                "href": "https://fr.wiktionary.org/wiki/adresse"
            },
            "map": "Ceci est une carte."
        }
        return json.dumps(ans)


if __name__ == "__main__":
    m = Main()
    m.app.run(debug=True, port=8080)
