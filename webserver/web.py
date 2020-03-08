import json
from flask import Flask, render_template
from flask_googlemaps import GoogleMaps
from flask_googlemaps import Map

app = Flask(__name__, template_folder=".")
api_key = ""

with open('key.json') as f:
   json_info = json.load(f)
   api_key = json_info["key"]

GoogleMaps(app, key=api_key)

@app.route("/")
def mapview():
    # creating a map in the view
    mymap = Map(
        identifier="sndmap",
        lat=37.4419,
        lng=-122.1419,
        markers=[
          {
             'icon': 'http://maps.google.com/mapfiles/ms/icons/green-dot.png',
             'lat': 37.4419,
             'lng': -122.1419,
             'infobox': "<b>Hello World</b> Elias is a little bitch dawg"
          },
          {
             'icon': 'http://maps.google.com/mapfiles/ms/icons/blue-dot.png',
             'lat': 37.4300,
             'lng': -122.1400,
             'infobox': "<b>Hello World from other place</b>"
          }
        ]
    )
    return render_template('template.html', mymap=mymap)

if __name__ == "__main__":
    app.run(debug=True)
