from flask import Flask, render_template, request, url_for
import json

from api_request import ApiRequest

class Main:
    """ This class load the HTML page."""
    def __init__(self):
        self.app = Flask(__name__)
        self.app.add_url_rule('/', 'home', self.home)
        self.app.add_url_rule('/question/<question>', 'req', self.req)

    def home(self):
        return render_template('page.html')

    def req(self, question):
        reqAnswer = ApiRequest(question)
        return reqAnswer.json


if __name__ == "__main__":
    m = Main()
    m.app.run(debug=True, port=8080)
