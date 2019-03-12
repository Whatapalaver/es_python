# make sure ES is up and running
from flask import Flask
from routes.search import search_blueprint

app = Flask(__name__)
app.register_blueprint(search_blueprint)

if __name__ == "__main__":
    app.run(port=5000, debug=True)
