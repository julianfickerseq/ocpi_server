from flask import Flask
import sys
import json

with open(f'{sys.path[0]}/ocpi_creds.json', 'r') as file:
    data = json.load(file)
    print(data)

app = Flask(__name__)
@app.route("/locations/404")
def location():
    return {}


app.run(host="localhost", port=5001, debug=True)