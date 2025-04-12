from google.cloud import bigquery
from google.auth import load_credentials_from_file
from google.cloud.bigquery import Client
import pandas as pd
import streamlit as st
import plotly.express as px

# 设置页面配置
st.set_page_config(
    page_title="Swanit Music Channel",
    page_icon="🎵",
    layout="wide"
)

# 加载 BigQuery 凭证和数据
credentials, project_id = load_credentials_from_file('service_account.json')

client = Client(
    project=project_id,
    credentials=credentials
)

# 加载数据函数
def load_data(table):
    query = f"SELECT * FROM `da26-python.music_data.{table}`"
    load_job = client.query(query)
    return load_job.to_dataframe()

# 加载所有数据
audio_features = load_data("audio_features")
chart_positions = load_data("chart_positions")
artists = load_data("artists")
tracks = load_data("tracks")
tracks_artists_mapping = load_data("tracks_artists_mapping")

print(chart_positions.columns)
print(tracks_artists_mapping.columns)
print(artists.columns)
print(tracks.columns)
print(audio_features.columns)


# 合并数据
tracks_with_artists = chart_positions.merge(tracks_artists_mapping, on="track_id", how="inner")
artist_tracks = tracks_with_artists.merge(artists, on="artist_id", how="inner")
# 确保track_id为字符串类型
chart_positions['track_id'] = chart_positions['track_id'].astype(str)
    
# 合并所有相关数据
chart_tracks = (artist_tracks.merge(chart_positions, on="track_id", how="inner")
                   .merge(tracks, on="track_id", how="inner"))
    
chart_tracks = chart_tracks.rename(columns={
    "name_x": "artist_name",
    "name_y": "track_name",
    "list_position": "chart_position",  # 重命名以避免混淆
    "chart_week": "chart_date"  # 重命名以保持一致性
})
print(chart_tracks.columns)

# 添加年份列
chart_tracks['year'] = pd.to_datetime(chart_tracks['chart_week_x']).dt.year

# 页面内容开始
st.title("🎵 Swanit Music Channel")

# 创建年份选择器（放在页面顶部）
col1, col2 = st.columns([2, 3])
with col1:
    available_years = sorted(chart_tracks['year'].unique())
    selected_year = st.selectbox("Select Year", available_years, index=len(available_years)-1)

# 过滤选定年份的数据
yearly_data = chart_tracks[chart_tracks['year'] == selected_year]

yearly_data.columns = yearly_data.columns.str.strip()

print(yearly_data.columns)
# 找到每年的排名第一的歌曲
number_one_songs = yearly_data[yearly_data["list_position_x"] == 1]  # 修改这里使用正确的列名

print(number_one_songs["artist_name"])

# 计算统计数据
song_weeks = (number_one_songs.groupby("track_name")
             .size()
             .reset_index(name="weeks_at_number_one")
             .sort_values(by="weeks_at_number_one", ascending=False))

artist_weeks = (number_one_songs.groupby("artist_name")
               .size()
               .reset_index(name="weeks_at_number_one")
               .sort_values(by="weeks_at_number_one", ascending=False))

# 在顶部显示年度概览
st.subheader(f"📊 {selected_year} Billboard Overview")
top_col1, top_col2, top_col3 = st.columns(3)

with top_col1:
    total_number_ones = len(song_weeks)
    st.metric("Number of #1 Songs", total_number_ones)

with top_col2:
    total_artists = len(artist_weeks)
    st.metric("Number of #1 Artists", total_artists)

with top_col3:
    if not song_weeks.empty:
        top_song = song_weeks.iloc[0]
        st.metric("Longest Running #1", 
                  f"{top_song['track_name']}", 
                  f"{top_song['weeks_at_number_one']} weeks")

# 侧边栏选择
with st.sidebar:
    st.header("Analysis Options")
    analysis_type = st.radio(
        "Choose an analysis type:",
        ["Artists by #1 Weeks", "Songs by #1 Weeks", "Top Tracks"]
    )

# 显示主要内容
if analysis_type == "Songs by #1 Weeks":
    st.subheader(f"🎵 {selected_year} Songs by #1 Weeks")
    if not song_weeks.empty:
        # 显示前10首歌
        top_songs = song_weeks.head(10)
        fig = px.bar(
            top_songs,
            x="track_name",
            y="weeks_at_number_one",
            title=f"Top Songs by Weeks at #1 in {selected_year}",
            labels={"track_name": "Track Name", "weeks_at_number_one": "Weeks at #1"}
        )
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)

        # 显示详细数据
        st.dataframe(song_weeks, use_container_width=True)
    else:
        st.write("No #1 songs data available for this year.")

elif analysis_type == "Artists by #1 Weeks":
    st.subheader(f"🎤 {selected_year} Artists by #1 Weeks")
    if not artist_weeks.empty:
        # 显示前10位艺术家
        top_artists = artist_weeks.head(10)
        fig = px.bar(
            top_artists,
            x="artist_name",
            y="weeks_at_number_one",
            title=f"Top Artists by Weeks at #1 in {selected_year}",
            labels={"artist_name": "Artist Name", "weeks_at_number_one": "Weeks at #1"}
        )
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)

        # 显示详细数据
        st.dataframe(artist_weeks, use_container_width=True)
    else:
        st.write("No #1 artists data available for this year.")

else:  # Top Tracks
    st.subheader(f"📈 {selected_year} Chart Performance")
    # 显示当年所有曲目的表现
    yearly_tracks = yearly_data[["artist_name", "track_name", "list_position_x", "chart_week_x"]]
    yearly_tracks = yearly_tracks.sort_values(["chart_week_x", "list_position_x"])

    print(yearly_tracks.columns)

    st.dataframe(yearly_tracks, use_container_width=True)