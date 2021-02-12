from flask import Flask, render_template, request
import json
import os

from api_request import ApiRequest

class Main:
    """ This class load the HTML page."""
    def __init__(self):
        self.app = Flask(__name__)
        self.app.config.from_pyfile('config.py', silent=True)
        self.app.add_url_rule('/', 'home', self.home)
        self.app.add_url_rule('/question', 'req', self.req, methods=['POST'])

    def home(self):
        return render_template('page.html')

    def req(self):
        question = request.data.decode("utf-8")
        return ApiRequest(question).json

if __name__ == "__main__":
    m = Main()
    m.app.run("https://ocgrandpy.herokuapp.com/")
