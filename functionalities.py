import datetime
import math
import pymongo
import streamlit as st
import pycountry
import pandas as pd
import numpy as np
from geopy.exc import GeocoderTimedOut
from geopy.geocoders import Nominatim
import collections


def init_connection():
    return pymongo.MongoClient(**st.secrets["mongo"])


def request(query):
    client = init_connection()
    tracks = client["Spotify_tracks"]["tracks"]

    return tracks.find(query)


def set_map(countries):
    c = expand_abr(countries)
    c = get_location(c)
    print(c)
    return c


def expand_abr(countries):
    dic = {"Country_abr": countries}
    df = pd.DataFrame(data=dic)
    new_c = df["Country_abr"].apply(
        lambda x: pycountry.countries.get(alpha_3=x).name if len(x) == 3 else pycountry.countries.get(alpha_2=x).name)

    for i in range(0, len(new_c)):
        print(new_c[i])
        new_c[i] = new_c[i].split(",")[0]
        if new_c[i] == "Russian Federation":
            new_c[i] = "Russia"
        if new_c[i] == "Viet Nam":
            new_c[i] = "Vietnam"
        if new_c[i] == "Korea":
            new_c[i] = "South Korea"
    return new_c


def generate_abr(country):
    if country == "Taiwan":
        country = "Taiwan, Province of China"
    elif country == "Bolivia":
        country = "Bolivia, Plurinational State of"
    elif country == "South Korea":
        country = "Korea, Republic of"
    elif country == "Russia":
        country = "Russian Federation"

    abr = pycountry.countries.get(name=country)
    return abr.alpha_2.lower()


def get_location(countries):
    longitude = []
    latitude = []
    for i in countries.values:
        if find_geocode(i) is not None:
            loc = find_geocode(i)
            latitude.append(loc.latitude)
            longitude.append(loc.longitude)
        else:
            latitude.append(np.nan)
            longitude.append(np.nan)
    j = 0
    locations_dict = {}
    for c in countries:
        locations_dict[c] = [longitude[j], latitude[j]]
        j += 1

    return locations_dict


def find_geocode(city):
    try:
        geolocator = Nominatim(user_agent="streamlit_app")

        return geolocator.geocode(city)

    except GeocoderTimedOut:

        return find_geocode(city)


def get_countries():
    client = init_connection()
    tracks = client["Spotify_tracks"]["tracks"]

    all_tracks = tracks.find({})
    countries = []
    for t in all_tracks:
        if t["country"] in countries:
            pass
        else:
            countries.append(t["country"])

    if "global" in countries:
        x,  y = countries.index("global"), countries.index(countries[0])
        countries[x], countries[y] = countries[y], countries[x]

    return countries


def get_countries_by_song(song_name):
    client = init_connection()
    tracks = client["Spotify_tracks"]["tracks"]

    all_tracks = tracks.find({"name": song_name})
    countries = []
    for t in all_tracks:
        if t["country"] != "global":
            if t["country"] in countries:
                pass
            else:
                countries.append(t["country"])
    countries = expand_abr(countries)
    return countries


def get_names(country):
    if len(country) > 0:
        all_tracks = request({"country": country})
    else:
        all_tracks = request({})
    song_names = []
    for t in all_tracks:
        name = t["name"]
        if name in song_names:
            pass
        else:
            song_names.append(name)
    return song_names


def delete(query):
    client = init_connection()
    tracks = client["Spotify_tracks"]["tracks"]

    tracks.delete_many(query)


def get_genre(genres):
    genre = genres[1:len(genres) - 1]
    genre = genre.replace("'", "")
    return genre.split(", ")


def millify(n):
    millnames = ['', ' K', ' M', ' B', ' T']
    n = float(n)
    millidx = max(0, min(len(millnames) - 1,
                         int(math.floor(0 if n == 0 else math.log10(abs(n)) / 3))))

    return '{:.0f}{}'.format(n / 10 ** (3 * millidx), millnames[millidx])


def get_time_interval(song, start):
    start = start.split("-")
    start_date = datetime.date(int(start[0]), int(start[1]), int(start[2]))
    track_info = request({"name": song})
    dates = {}
    for item in track_info:
        date = item["date"].split("-")
        date = datetime.date(int(date[0]), int(date[1]), int(date[2]))
        if date >= start_date:
            date = date.strftime("%Y-%m-%d")
            if date in dates.keys():
                if dates[date] < item["position"]:
                    dates[date] = item["position"]
            else:
                dates[date] = item["position"]

    od = collections.OrderedDict(sorted(dates.items()))

    df = {"Dates": [], "Positions": []}
    for d in od:
        df["Dates"].append(d)
        df["Positions"].append(od[d])

    df = pd.DataFrame(data=df)
    return df


def get_all_streams():
    all_tracks = request({})
    total_streams = 0
    i=0
    for item in all_tracks:
        i+=1
        total_streams += item["streams"]
    print(i)
    return total_streams


if __name__ == '__main__':
    print(get_all_streams())

