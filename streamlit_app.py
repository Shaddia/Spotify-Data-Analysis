import datetime
import streamlit as st
import pandas as pd
import plotly.express as px
import functionalities as tools
from PIL import Image
image = Image.open('spotify_logo.png')

locations = {'Italy': [12.674297, 42.6384261], 'Philippines': [122.7312101, 12.7503486],
             'Taiwan': [120.9820179, 23.9739374], 'Portugal': [-8.1353519, 39.6621648],
             'Hong Kong': [114.1628131, 22.2793278], 'Peru': [-75.0458515, -6.8699697],
             'Colombia': [-72.9088133, 4.099917], 'Costa Rica': [-84.0739102, 10.2735633],
             'Uruguay': [-56.0201525, -32.8755548], 'Brazil': [-53.2, -10.3333333],
             'United States': [-100.445882, 39.7837304], 'Canada': [-107.991707, 61.0666922],
             'Sweden': [14.5208584, 59.6749712], 'Norway': [9.0999715, 60.5000209],
             'Denmark': [10.3333283, 55.670249], 'Poland': [19.134422, 52.215933],
             'Greece': [21.9877132, 38.9953683], 'United Kingdom': [-3.2765753, 54.7023545],
             'Australia': [134.755, -24.7761086], 'Netherlands': [5.6343227, 52.2434979],
             'Belgium': [4.6667145, 50.6402809], 'Ireland': [-7.9794599, 52.865196],
             'Switzerland': [8.2319736, 46.7985624], 'Czechia': [15.3381061, 49.7439047],
             'Austria': [14.12456, 47.59397], 'Israel': [34.8594762, 30.8124247],
             'New Zealand': [172.8344077, -41.5000831], 'South Africa': [24.991639, -28.8166236],
             'Hungary': [19.5060937, 47.1817585], 'Romania': [24.6859225, 45.9852129],
             'Germany': [10.4478313, 51.1638175], 'Finland': [25.9209164, 63.2467777],
             'Slovakia': [19.4528646, 48.7411522], 'Estonia': [25.3319078, 58.7523778],
             'Mexico': [-102.0077097, 23.6585116], 'Chile': [-71.3187697, -31.7613365],
             'Spain': [-4.8379791, 39.3260685], 'Argentina': [-64.9672817, -34.9964963],
             'Paraguay': [-58.1693445, -23.3165935], 'Ecuador': [-79.3666965, -1.3397668],
             'Guatemala': [-90.345759, 15.5855545], 'El Salvador': [-88.9140683, 13.8000382],
             'Dominican Republic': [-70.3028026, 19.0974031], 'Honduras': [-86.0755145, 15.2572432],
             'Panama': [-81.1308434, 8.559559], 'Bolivia': [-64.9912286, -17.0568696],
             'Nicaragua': [-85.2936911, 12.6090157], 'Malaysia': [102.2656823, 4.5693754],
             'Iceland': [-18.1059013, 64.9841821], 'Latvia': [24.7537645, 56.8406494],
             'United Arab Emirates': [53.9994829, 24.0002488], 'Bulgaria': [25.4856617, 42.6073975],
             'Lithuania': [23.7499997, 55.3500003], 'Singapore': [103.8194992, 1.357107],
             'Indonesia': [117.8902853, -2.4833826], 'Thailand': [100.83273, 14.8971921],
             'Japan': [139.2394179, 36.5748441], 'France': [1.8883335, 46.603354],
             'Saudi Arabia': [42.3528328, 25.6242618], 'Luxembourg': [6.1296751, 49.8158683],
             'Vietnam': [107.9650855, 15.9266657], 'Egypt': [29.2675469, 26.2540493],
             'South Korea': [127.6961188, 36.638392], 'Morocco': [-7.3362482, 31.1728205],
             'Turkey': [34.9249653, 38.9597594], 'Russia': [97.7453061, 64.6863136],
             'Ukraine': [31.2718321, 49.4871968], 'India': [78.6677428, 22.3511148],
             'Malta': [14.4476911, 35.8885993], 'Cyprus': [33.1451285, 34.9823018]}

page_title = "Spotify tracks analysis"
page_icon = ":musical_note:"

st.set_page_config(page_title=page_title, page_icon=page_icon)
st.title(page_title + " " + page_icon)

song_names = tools.get_names("")
aux_countries = tools.get_countries()
aux_countries.remove("global")
aux_countries = tools.expand_abr(aux_countries)
countries = ["Global"]

for c in aux_countries:
    countries.append(c)
# pd.concat([countries, pd.Series(["global"])])

with st.sidebar:
    st.image(image, width=150)
    st.header("Filters")

    st.metric("Registered songs", len(song_names))
    country = st.selectbox("Select country", countries)
    song = st.selectbox("Select a song to inspect", song_names)
    start_date = st.date_input("Select a date to start",
                               min_value=datetime.date(2014, 8, 10),
                               max_value=datetime.date(2022, 10, 17),
                               value=datetime.date(2014, 8, 10))

with st.container():
    with st.expander("All songs data in " + country):
        if country == "Global":
            all_tracks = tools.request({})
        else:
            country_aux = tools.generate_abr(country)
            all_tracks = tools.request({"country": country_aux})
        streams_by_genre = {}
        total_country_streams = 0
        total_explicit = {"True": 0, "False": 0}
        for t in all_tracks:
            name = t["name"]
            if name in song_names:
                pass
            else:
                song_names.append(name)

            if t["explicit"] == "True":
                total_explicit["True"] += 1
            else:
                total_explicit["False"] += 1

            genres = tools.get_genre(t["artist_genres"])
            for g in genres:
                if g in streams_by_genre.keys():
                    streams_by_genre[g] += t["streams"]
                else:
                    streams_by_genre[g] = t["streams"]
            total_country_streams += t["streams"]
        total_streams = tools.get_all_streams()
        percentage = (total_country_streams / total_streams)*100
        st.metric("Total streams", tools.millify(total_country_streams))
        st.write(str(round(percentage,2)) + "% of global streams")

        # Genre distribution pie chart
        genre_distribution = {"Genre": [], "Streams": []}
        for g in streams_by_genre:
            genre_distribution["Genre"].append(g)
            genre_distribution["Streams"].append(streams_by_genre[g])

        genres_dataframe = pd.DataFrame(data=genre_distribution)
        names = genres_dataframe["Genre"]
        values = genres_dataframe["Streams"]

        fig = px.pie(genres_dataframe, values=values, names=names, title=country + " Genre Distribution")
        fig.update_layout(legend_title_text="Genre")
        fig.update_traces(textposition="inside", textinfo="percent+label")
        st.plotly_chart(fig, use_container_width=True)

        # Explicit proportion pie chart
        explicit_data = {"Explicit": [], "Number of songs": []}
        for s in total_explicit:
            explicit_data["Explicit"].append(s)
            explicit_data["Number of songs"].append(total_explicit[s])

        explicit_dataframe = pd.DataFrame(data=explicit_data)
        names = explicit_dataframe["Explicit"]
        values = explicit_dataframe["Number of songs"]

        fig = px.pie(genres_dataframe, values=values, names=names, title=country + " Explicit Content Proportion")
        fig.update_layout(legend_title_text="Is explicit")
        fig.update_traces(textposition="inside", textinfo="percent+label")
        st.plotly_chart(fig, use_container_width=True)
    with st.expander("'"+song+"'" + " Data"):
        st.write("Selected song to inspec: " + song)
        song_countries = tools.get_countries_by_song(song)

        df = []
        for c in song_countries:
            df.append(locations[c])
        df = pd.DataFrame(df, columns=["lon", "lat"])

        st.subheader("Countries where the song got popular")
        st.map(df)

        st.subheader("Positions changes from " + start_date.strftime("%Y-%m-%d") + " to last registered")
        time_progression = tools.get_time_interval(song, start_date.strftime("%Y-%m-%d"))
        fig = px.line(time_progression, x="Dates", y="Positions")
        st.plotly_chart(fig, use_container_width=True)


