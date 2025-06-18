import requests
import streamlit as st
import pandas as pd
import pickle
import os

st.title('🎬 Movie Recommender System')

# --- Download the Pickle Files if Missing using requests ---
def download_file_from_google_drive(file_id, destination):
    URL = "https://docs.google.com/uc?export=download"
    session = requests.Session()
    response = session.get(URL, params={'id': file_id}, stream=True)
    token = get_confirm_token(response)
    if token:
        response = session.get(URL, params={'id': file_id, 'confirm': token}, stream=True)
    with open(destination, "wb") as f:
        for chunk in response.iter_content(32768):
            if chunk:
                f.write(chunk)

def get_confirm_token(response):
    for key, value in response.cookies.items():
        if key.startswith('download_warning'):
            return value
    return None

if not os.path.exists("similarity.pkl"):
    similarity_file_id = "1ObBS9BblPCgD8v8HSA4mimjtcPqkEAnm"
    download_file_from_google_drive(similarity_file_id, "similarity.pkl")

if not os.path.exists("movie_dict.pkl"):
    movie_dict_file_id = "1koLPKCppmYo9bSSdPsWutJnqbQol1yUh"
    download_file_from_google_drive(movie_dict_file_id, "movie_dict.pkl")

# --- Load Data Safely ---
try:
    movie_dict = pickle.load(open('movie_dict.pkl', 'rb'))
    similarity = pickle.load(open('similarity.pkl', 'rb'))
    movie = pd.DataFrame(movie_dict)
except Exception as e:
    st.error("❌ Failed to load recommendation data.")
    st.stop()

# ✅ Safe function to fetch posters from TMDB (handles errors)
def fetch_poster(movie_id):
    try:
        api_key = "8265bd1679663a7ea12ac168da84d2e8"
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}&language=en-US"
        response = requests.get(url, timeout=3)  # ⏱️ Wait max 3 seconds
        response.raise_for_status()
        data = response.json()
        poster_path = data.get("poster_path")
        if poster_path:
            return "https://image.tmdb.org/t/p/w500/" + poster_path
        else:
            return "https://via.placeholder.com/500x750?text=No+Image"
    except:
        return "https://via.placeholder.com/500x750?text=Poster+Unavailable"

# ✅ Recommend similar movies
def recommend(mov):
    index = movie[movie['title'] == mov].index[0]
    distances = similarity[index]
    movie_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    recommended_titles = []
    recommended_posters = []

    for i in movie_list:
        movie_id = movie.iloc[i[0]].movie_id
        title = movie.iloc[i[0]].title
        recommended_titles.append(title)
        recommended_posters.append(fetch_poster(movie_id))

    return recommended_titles, recommended_posters

# UI: Dropdown for movie selection
movie_names = movie['title'].values
selected_moviebox = st.selectbox("🎥 Type or select a movie from the list:", movie_names)

# Button to show recommendations
if st.button('🔍 Show Recommendations'):
    movie_recommendations, poster_recommendations = recommend(selected_moviebox)

    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.text(movie_recommendations[0])
        st.image(poster_recommendations[0])
    with col2:
        st.text(movie_recommendations[1])
        st.image(poster_recommendations[1])
    with col3:
        st.text(movie_recommendations[2])
        st.image(poster_recommendations[2])
    with col4:
        st.text(movie_recommendations[3])
        st.image(poster_recommendations[3])
    with col5:
        st.text(movie_recommendations[4])
        st.image(poster_recommendations[4])
