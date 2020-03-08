import json
import googlemaps

from flask import Flask, render_template, request
from flask_googlemaps import GoogleMaps
from flask_googlemaps import Map

app = Flask(__name__, template_folder=".")
api_key = ""

with open('key.json') as f:
   json_info = json.load(f)
   api_key = json_info["key"]

GoogleMaps(app, key=api_key)
gmaps = googlemaps.Client(key=api_key)

def get_locations(location, coords, keywords):
    """ Location is string, keywords is list of strings to search for
        get_locations("las vegas", ["dinner", "night", "club"])
    """
    return_fields = ["formatted_address", "name", "rating", "opening_hours", "photos"]
    bias = f"point:{coords[0]},{coords[1]}"
    places = {}

    for key in keywords:
        place = gmaps.find_place(input = [f"{location} {key}"], input_type="textquery", fields=return_fields, location_bias=bias)
        places[key] = place

    return places

@app.route("/", methods=['GET', 'POST'])
def mapview():
    if request.method == 'POST':
        location = request.form['text']
        coords = gmaps.geocode(address=location)[0]
        coords = (coords["geometry"]["location"]["lat"], coords["geometry"]["location"]["lng"])

        morning = get_locations(location, coords, ["breakfast", "coffee", "park"])
        afternoon = get_locations(location, coords, [])
        evening = get_locations(location, coords, [])

        locations = []

        for key in morning:
            for place in morning[key]:
                place = morning[key][place]

                if place == "OK":
                    break

                location_coords = gmaps.geocode(address=place[0]["formatted_address"])
                location_coords = (location_coords[0]["geometry"]["location"]["lat"], location_coords[0]["geometry"]["location"]["lat"])
                html = "<b>{name}</b><br><b>Rating: </b>{rating}<br>{gmaps_link}Google Maps</a>"

                locations.append({
                    'icon': 'https://maps.google.com/mapfiles/ms/icons/green-dot.png',
                    'lat': location_coords[0], 'lng': location_coords[1],
                    'infobox': html.format(
                        name=place[0]["name"],
                        rating=place[0]["rating"],
                        gmaps_link=place[0]["photos"][0]["html_attributions"][0].replace("</a>", '')
                    )})

         # creating a map in the view
        mymap = Map(
            identifier="mymap",
            lat=coords[0],
            lng=coords[1],
            markers=locations,
            style = "height:30rem;width:75rem",
            zoom = 15,
        )
        return render_template('template.html', mymap=mymap)


    else:
        return render_template('template_home.html')

@app.route("/credits")
def credits():
    return "made by elias sean han and vivian"

if __name__ == "__main__":
    app.run(debug=True)
