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
        #place = gmaps.find_place(input = [f"{location} {key}"], input_type="textquery", fields=return_fields, location_bias=bias)
        place = gmaps.places_nearby(location=coords, radius=16000, keyword=key, rank_by="prominence")
        places[key] = place["results"][0]
        #print(place["results"])

    return places

def places_list(set_of_locations):
    returned_locations = []

    for i in set_of_locations:
        for key in i:
            place = i[key]

            if place == "OK":
                break

            location_coords = (place["geometry"]["location"]["lat"], place["geometry"]["location"]["lng"])
            html = "<b>{name}</b><br><b>Rating: </b>{rating}<br><a href='https://www.google.com/maps/search/?api=1&query_place_id={place_id}'>Google Maps</a>"

            returned_locations.append({
                'icon': 'https://maps.google.com/mapfiles/ms/icons/green-dot.png',
                'lat': location_coords[0], 'lng': location_coords[1],
                'infobox': html.format(
                    name=place["name"],
                    rating=place["rating"],
                    place_id=place["place_id"]
                )})
    return returned_locations

@app.route("/", methods=['GET', 'POST'])
def mapview():
    if request.method == 'POST':
        location = request.form['text']
        coords = gmaps.geocode(address=location)[0]
        coords = (coords["geometry"]["location"]["lat"], coords["geometry"]["location"]["lng"])

        morning = get_locations(location, coords, ["breakfast", "coffee", "park", "hike"])
        afternoon = get_locations(location, coords, ["lunch", "zoo", "museum", "shopping"])
        evening = get_locations(location, coords, ["dinner", "dessert", "club", "concert", "nightlife"])

        locations = places_list((morning, afternoon, evening))

        # creating a map in the view
        mymap = Map(
            identifier="mymap",
            lat=coords[0],
            lng=coords[1],
            markers=locations,
            cls="maps",
            style = ("height:100rem;", "width:100rem;", "margin-left:2rem;", "margin-bottom:4rem;")
            #style = ("height:1000px","width:1000px", "top:17%;", "left:3%;", "right:39.5%;", "bottom:4%;"),
            #zoom = 12,
        )

        locations_template = "<div class='location-element'> <p><b>{name}</b></p><br><p><b>Rating: </b>{rating}/5</p><br><p>{address}</p></div>"
        location_html = ""

        for i in (morning, afternoon, evening):
            for key in i:
                place = i[key]

                location_html += locations_template.format(
                    name = place["name"],
                    rating = place["rating"],
                    address = place["vicinity"],
                )

        return render_template('template.html', mymap=mymap, locations=location_html)

    else:
        return render_template('template_home.html')

@app.route("/credits")
def credits():
    return "made by elias sean han and vivian"

@app.route("/<anything>")
def whats_up(anything):
    return "whats up " + anything

if __name__ == "__main__":
    app.run(debug=True)
