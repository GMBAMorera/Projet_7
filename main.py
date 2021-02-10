from flask import Flask, render_template, request, url_for, send_file, make_response
import json
import os

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
        print("req: ", question)
        return ApiRequest(question).json

if __name__ == "__main__":
    m = Main()
    m.app.run(debug=True, port=8080)
