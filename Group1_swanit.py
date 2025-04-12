import streamlit as st
from google.cloud import bigquery
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import plotly.figure_factory as ff
from streamlit_option_menu import option_menu
import db_dtypes
from google.auth import load_credentials_from_file
from google.cloud.bigquery import Client
import altair as alt

# Set page config
st.set_page_config(layout="wide", page_title="SWANIT Music Festival Planner", page_icon="🎵")

# Load data functions
@st.cache_data
def load_data(table):
    credentials, project_id = load_credentials_from_file('service_account.json')
    client = Client(project=project_id, credentials=credentials)
    query = f"SELECT * FROM `da26-python.music_data.{table}`"
    load_job = client.query(query)
    return load_job.to_dataframe()

def load_and_merge_data():
    audio_features = load_data("audio_features")
    chart_positions = load_data("chart_positions")
    artists = load_data("artists")
    tracks = load_data("tracks")
    tracks_artists = load_data("tracks_artists_mapping")
    
    # Merge data as per original code
    songs = (tracks
        .merge(audio_features, on='track_id', how='left')
        .merge(chart_positions, on='track_id', how='left')
        .merge(tracks_artists, on='track_id', how='left', suffixes=('', '_artist'))
    )
    
    # Data processing as per original code
    songs['release_date'] = pd.to_datetime(songs['release_date'], errors='coerce')
    songs['release_year'] = songs['release_date'].dt.year
    songs['chart_week'] = pd.to_datetime(songs['chart_week'])
    songs['chart_year'] = songs['chart_week'].dt.year
    songs['list_position'] = songs['list_position'].fillna(0)
    
    singers = (artists
        .merge(tracks_artists, on='artist_id', how='left')
        .groupby('artist_id')
        .agg({
            'name': 'first',
            'popularity': 'first',
            'followers': 'first',
            'track_id': 'count'
        })
        .rename(columns={'track_id': 'total_tracks'})
        .reset_index()
    )
    
    return singers, songs

# Load the data
singers, songs = load_and_merge_data()


# Custom CSS for enhanced styling
st.markdown("""
    <style>
    .metric-container {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin: 10px 0;
    }
    .metric-value {
        font-size: 24px;
        font-weight: bold;
        color: #1f77b4;
    }
    .metric-label {
        font-size: 14px;
        color: #666;
    }
    .custom-tab {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 10px 0;
    }
    .section-header {
        font-size: 20px;
        font-weight: bold;
        margin: 20px 0;
        color: #2c3e50;
    }
    </style>
    """, unsafe_allow_html=True)

# [Previous data loading functions remain the same]
MENU_OPTIONS = [
    "Home",
    "Artist Analysis",
    "Song Analysis",
    "Trend Analytics"
]

MENU_ICONS = [
    "house-door-fill",
    "person-circle",
    "music-note-beamed",
    "graph-up"
]

# Sidebar
with st.sidebar:
    # Logo
    st.image("/Users/honghuosheng/Desktop/small_swanit.png", caption="Music Analytics")
    
    # Navigation menu
    selected = option_menu(
        menu_title="Navigation",
        options=MENU_OPTIONS,
        icons=MENU_ICONS,
        default_index=0,
    )

# Main content area
st.title("🎵 SWANIT Music Festival Planner")

if selected == "Home":
    # Key metrics row
    st.image("/Users/honghuosheng/Desktop/Black White Modern Music Concert Banner Landscape.png", caption="Our Story")
    st.image("/Users/honghuosheng/Desktop/111.png")
elif selected == "Artist Analysis":
    st.subheader("👨‍🎤 Billboard Artist Deep Dive")

    col1, col2, col3, col4 = st.columns(4)
    # Artist metrics
    with col1:
        st.markdown("""
            <div class="metric-container">
                <div class="metric-value">702 🎤</div>
                <div class="metric-label">Total Artists</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
            <div class="metric-container">
                <div class="metric-value">1,284 🎧</div>
                <div class="metric-label">Total Songs</div>
            </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
            <div class="metric-container">
                <div class="metric-value">70.8 ⭐</div>
                <div class="metric-label">Average Popularity</div>
            </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown("""
            <div class="metric-container">
                <div class="metric-value">6,944K 👥</div>
                <div class="metric-label">Average Followers</div>
            </div>
        """, unsafe_allow_html=True)

    # Artist visualizations
    tabs = st.tabs(["⭐ Top 50 Artists"])  # Define tabs as a list
    tab1 = tabs[0]  # Access the first tab

    with tab1:
    # Top 50 popularity 
        top_artists = singers.sort_values(by="popularity", ascending=False).head(50)
    # Top 1 
        top_artist = top_artists.iloc[0]

    # Create two columns
        left_col, right_col = st.columns([0.4, 0.6])  # 40:60 ratio

        with left_col:
    # Get top 50 artists sorted by popularity
            top_artists = singers.sort_values(by="popularity", ascending=False).head(50).reset_index(drop=True)
            
            
            st.dataframe(
                top_artists[["name", "popularity", "followers"]],
                height=600  # Increased height to match right column content
            )

        # Right column - Image and Video
        with right_col:
            # Get top artist for the image caption
            top_artist = top_artists.iloc[0]
            
            # Image section
            st.image(
                "https://images.seattletimes.com/wp-content/uploads/2023/07/07222023_swift_213100.jpg?d=2048x1485",
                caption="Taylor Swift", width=604  # Updated from use_column_width to use_container_width
            )
            
            # Add some spacing
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Video section
            video_url = "https://www.youtube.com/watch?v=ic8j13piAhQ"
            st.video(video_url, start_time=0)
            st.markdown(
            """
           
            
            """,
            unsafe_allow_html=True,
)


elif selected == "Song Analysis":
    st.subheader("🎵 Song Features Analysis")
    
    # Load chart position 1 songs
    chart_position_1_songs = songs[songs["list_position"] == 1]

    # Song metrics
    metrics_col1, metrics_col2, metrics_col3 = st.columns(3)
    with metrics_col1:
        st.metric("Average Duration", "3:43 ⏱️")
    with metrics_col2:
        st.metric("Average Energy", "0.65 ⚡")
    with metrics_col3:
        st.metric("Average Danceability", "0.68 💃")

    # Feature correlations heatmap
    #features = ['danceability', 'energy', 'valence', 'acousticness']
    #corr_matrix = songs[features].corr()
    
    #fig = px.imshow(
    #    corr_matrix,
    #    title="Feature Correlations",
    #    labels=dict(color="Correlation")
    #)
    #st.plotly_chart(fig, use_container_width=True)

# ILENIA
# Function to calculate average features and create a radar chart
    @st.cache_data
    def create_radar_chart(top_n, title):
        top_singers = singers[['artist_id', 'name', 'popularity', 'followers']].sort_values(by='popularity', ascending=False).head(top_n)
        chart_position_1_songs = songs[songs["list_position"] == 1]
        chart_list1_with_artists = chart_position_1_songs.merge(
            top_singers, on="artist_id", how="inner"
        ).rename(columns={"name_x": "song_name", "name_y": "artist_name"})
        columns_to_drop = ['chart_week', 'list_position', 'release_year', 'chart_year', 'popularity', 'followers', 'loudness', "artist_id", "artist_name"]
        songs_top_n_singers_dirty = chart_list1_with_artists.drop(columns=columns_to_drop)
        songs_top_n_singers = songs_top_n_singers_dirty.drop_duplicates()
        song_features = ['danceability', 'energy', 'speechiness', 'acousticness', 'instrumentalness', 'valence']
        average_features = songs_top_n_singers[song_features].mean()
        fig = go.Figure()
        fig.add_trace(
            go.Scatterpolar(
                r=average_features.values,
                theta=average_features.index,
                fill='toself',
                name='Average Features'
            )
        )
        fig.update_layout(
            title=title,
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 1]
                )
            ),
            showlegend=True
        )
        return fig
    # Streamlit UI
    # Tabs for navigation
    tab1, tab2, tab3 = st.tabs(["Top 10 Artists", "Top 25 Artists", "Top 50 Artists"])
    # Top 10 Artists tab
    with tab1:
        st.subheader("Average Audio Features for Songs of the Top 10 Artists")
        radar_chart_10 = create_radar_chart(10, " ")
        st.plotly_chart(radar_chart_10)
    # Top 25 Artists tab
    with tab2:
        st.subheader("Average Audio Features for Songs of the Top 25 Artists")
        radar_chart_25 = create_radar_chart(25, " ")
        st.plotly_chart(radar_chart_25)
    # Top 50 Artists tab
    with tab3:
        st.subheader("Average Audio Features for Songs of the Top 50 Artists")
        radar_chart_50 = create_radar_chart(50, " ")
        st.plotly_chart(radar_chart_50)



    st.write ("Chart-Topping Hits: #1 Tracks and Artists")
    year = st.selectbox("Select Year",[x for x in range(2000,2025)])
    chart_position_1_songs = songs[songs["list_position"] == 1]
    chart_list1_with_artists = chart_position_1_songs.merge(
        singers, on='artist_id', how='left'
    ).rename(columns={'name_x':'song_name','name_y':'artist'})
    active_year = chart_list1_with_artists.loc[chart_list1_with_artists.chart_year == year]
    #Group by track and chart year, then count occurrences
    chart_position_with_art_analysis = (
        active_year
        .groupby(['song_name','artist','chart_year'], as_index=False)
        .agg(total_weeks=('list_position', 'count'))
    )

    chart_position_with_art_analysis = (
        chart_position_with_art_analysis
        .groupby(['song_name', 'chart_year','total_weeks'], as_index=False)
        .agg(
            artist_name=('artist', lambda x: ', '.join(x.unique())),
            
        )

    )
    #Sort by chart year and total weeks at position 1 for better readability
    chart_position_with_art_analysis = chart_position_with_art_analysis.sort_values(
        by=['chart_year', 'total_weeks'], ascending=[False, False]
    ).reset_index(drop=True)
    st.dataframe(chart_position_with_art_analysis)


elif selected == "Trend Analytics":

    st.subheader("Danceability and Energy")
    st.write("### Danceability and Energy Trends Over Time")
        
    # Filter data for tracks in list_position 1-40 and from 2000 onwards
    top40 = songs[(songs['list_position'] <= 40) & (songs['chart_year'] >= 2000)]
        
    yearly_trends = (

        top40.groupby('chart_year')[['danceability', 'energy']]
        .mean()
        .reset_index()
    )
        
    melted_trends = yearly_trends.melt(
        id_vars=['chart_year'],
        var_name='Feature',
        value_name='Average Value'
    )
        
        # Create the line chart
    line_chart = alt.Chart(melted_trends).mark_line(point=True).encode(
        x=alt.X('chart_year:O',
        title='Year',
        axis=alt.Axis(
            values=[2000, 2002, 2004, 2006, 2008, 2010, 2012, 2014, 2016, 2018, 2020, 2022, 2024],
            labelAngle=-45
            )
        ),
        y=alt.Y(
            'Average Value:Q',
            title='Average Value',
            scale=alt.Scale(domain=[0.5, 1]),
            axis=alt.Axis(values=[0.6, 0.62, 0.64, 0.66, 0.68, 0.7, 0.72, 0.74, 0.76])
        ),
        color=alt.Color('Feature:N', 
            legend=alt.Legend(
                orient='right',
                offset=10,
                title=None
            )
        ),
        tooltip=['chart_year', 'Feature', 'Average Value']
        ).properties(
            width=1000,
            height=400
        ).configure_title(
            fontSize=22,
            anchor='start'
        ).configure_axis(
            labelFontSize=16,
            titleFontSize=18
        )
        
    st.altair_chart(line_chart)

  
    st.write("### Danceability vs Energy Distribution")
        
        # Create scatter plot
    scatter_plot = px.scatter(
        songs,
        x="danceability",
        y="energy",
        labels={"danceability": 'Danceability', 'energy': 'Energy'},
        opacity=0.7
    )
        
        # Update layout for better appearance
    scatter_plot.update_layout(
        showlegend=False,
        height=450,  # Match the height of line chart
        margin=dict(l=20, r=20, t=20, b=20)
    )
        
    st.plotly_chart(scatter_plot, use_container_width=True)    
  
       


# Add export functionality
if st.sidebar.button("📥 Export Master Data"):
    st.sidebar.download_button(
        label="Download CSV",
        data=songs.to_csv().encode('utf-8'),
        file_name='music_data.csv',
        mime='text/csv'
    )

# Footer
st.markdown("---")
st.markdown("""
    <div style='text-align: center'>
        <p>Made with ❤️ for Music Analysis</p>
    </div>
""", unsafe_allow_html=True)