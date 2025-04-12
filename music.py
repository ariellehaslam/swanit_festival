from google.cloud import bigquery
from google.auth import load_credentials_from_file
from google.cloud.bigquery import Client

credentials, project_id = load_credentials_from_file('service_account.json')

# Load data from BigQuery
client = Client(
    project = project_id,
    credentials=credentials
)

# This is how to list the tables
database_id = "music_data"
tables = client.list_tables(database_id)

print(f"Tables contained in '{database_id}':")
for table in tables:
    print(f"{table.project}.{table.dataset_id}.{table.table_id}")

query = "SELECT * FROM `da26-python.music_data.tracks`"
load_job = client.query(query)
data = load_job.to_dataframe()

def load_data(table):
    query = f"SELECT * FROM `da26-python.music_data.{table}`"
    load_job = client.query(query)
    data = load_job.to_dataframe()
    return data

#  Load data 
def load_all_data():
    audio_features = load_data("audio_features")
    chart_positions = load_data("chart_positions")
    artists = load_data("artists")
    tracks = load_data("tracks")
    tracks_artists_mapping = load_data("tracks_artists_mapping")
    
    
    return audio_features, chart_positions, artists, tracks, tracks_artists_mapping



# import libraries
import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime


# Load all data
audio_features, chart_positions, artists, tracks, tracks_artists_mapping = load_all_data()


# 设置侧边栏背景颜色
sidebar_style = """
    <style>
    [data-testid="stSidebar"] {
        background-color: #f5f5dc;
    }
    </style>
"""
st.markdown(sidebar_style, unsafe_allow_html=True)


st.title("Swanit Music Festival")

# merge the data
tracks_with_artists = chart_positions.merge(tracks_artists_mapping, on="track_id", how="inner")

# Merge the result with artists on artist_id
artist_tracks = tracks_with_artists.merge(artists, on="artist_id", how="inner")

# Rename columns to avoid ambiguity
artist_tracks = artist_tracks.rename(columns={ "name_x": "track_name",  "name_y": "artist_name"}) 
# Filter for number-one entries
chart_positions['track_id'] = chart_positions['track_id'].astype(str)
chart_tracks = chart_positions.merge(artist_tracks, on="track_id", how="inner").merge(tracks, on="track_id", how="inner")
number_one_songs = chart_tracks[chart_tracks["list_position"] == 1]

# 分析数据准备
song_weeks = (
    number_one_songs.groupby("track_name")
    .size()
    .reset_index(name="weeks_at_number_one")
    .sort_values(by="weeks_at_number_one", ascending=False)
)
artist_weeks = (
    number_one_songs.groupby("artist_name")
    .size()
    .reset_index(name="weeks_at_number_one")
    .sort_values(by="weeks_at_number_one", ascending=False)
)

# 侧边栏选择
with st.sidebar:
    st.header("Analysis Options")
    analysis_type = st.radio(
        "Choose an analysis type:",
        ["Songs by #1 Weeks", "Artists by #1 Weeks", "Top Tracks"]
    )

# 动态内容更新
if analysis_type == "Songs by #1 Weeks":
    st.subheader("🎵 Songs by #1 Weeks")
    st.write("This section analyzes songs that stayed at the #1 position the longest.")
    st.dataframe(song_weeks)
    fig = px.bar(
        song_weeks,
        x="track_name",
        y="weeks_at_number_one",
        title="Songs by Weeks at #1",
        labels={"track_name": "Track Name", "weeks_at_number_one": "Weeks at #1"},
    )
    st.plotly_chart(fig)

elif analysis_type == "Artists by #1 Weeks":
    st.subheader("🎤 Artists by #1 Weeks")
    st.write("This section analyzes artists with the most cumulative weeks at #1.")
    st.dataframe(artist_weeks)
    fig = px.bar(
        artist_weeks,
        x="artist_name",
        y="weeks_at_number_one",
        title="Artists by Weeks at #1",
        labels={"artist_name": "Artist Name", "weeks_at_number_one": "Weeks at #1"},
    )
    st.plotly_chart(fig)

else:
    st.subheader("📊 Top Tracks")
    st.write("This section lists all tracks with their chart performance data.")
    st.dataframe(artist_tracks[["track_name", "artist_name", "list_position", "chart_week"]])