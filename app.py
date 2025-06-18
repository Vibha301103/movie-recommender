import streamlit as st
import pandas as pd
import pickle
import os
import gdown  # ✅ new import

st.title('🎬 Movie Recommender System')

# ✅ Use gdown to download files from Google Drive
if not os.path.exists("movie_dict.pkl"):
    gdown.download(id="1koLPKCppmYo9bSSdPsWutJnqbQol1yUh", output="movie_dict.pkl", quiet=False)

if not os.path.exists("similarity.pkl"):
    gdown.download(id="1ObBS9BblPCgD8v8HSA4mimjtcPqkEAnm", output="similarity.pkl", quiet=False)

# ✅ Load data safely
try:
    with open("movie_dict.pkl", "rb") as f:
        movie_dict = pickle.load(f)
    with open("similarity.pkl", "rb") as f:
        similarity = pickle.load(f)
    movie = pd.DataFrame(movie_dict)
except Exception as e:
    st.error(f"❌ Failed to load files: {e}")
    st.stop()

# ✅ Poster fetch
def fetch_poster(movie_id):
    try:
        api_key = "8265bd1679663a7ea12ac168da84d2e8"
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}&language=en-US"
        response = requests.get(url, timeout=3)
        response.raise_for_status()
        data = response.json()
        poster_path = data.get("poster_path")
        return "https://image.tmdb.org/t/p/w500/" + poster_path if poster_path else "https://via.placeholder.com/500x750?text=No+Image"
    except:
        return "https://via.placeholder.com/500x750?text=Poster+Unavailable"

# ✅ Recommendation logic
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

# ✅ UI
movie_names = movie['title'].values
selected_moviebox = st.selectbox("🎥 Type or select a movie from the list:", movie_names)

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
