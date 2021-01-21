from flask import Flask, render_template, request, url_for

class Main:
    """ This class load the HTML page."""
    def __init__(self):
        self.app = Flask(__name__)
        self.app.add_url_rule('/', 'home', self.home)

    def home(self):
        return render_template('page.html')


if __name__ == "__main__":
    m = Main()
    m.app.run(debug=True, port=8080)
