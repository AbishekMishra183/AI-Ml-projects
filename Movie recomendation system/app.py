import os
import pickle
import streamlit as st
import requests
import gdown

# -----------------------------
# Custom Styling
# -----------------------------
st.set_page_config(page_title="🎬 CineMatch AI", page_icon="🎥", layout="wide")

st.markdown("""
    <style>
        body {
            background-color: #0f1117;
            color: white;
        }
        .title {
            text-align: center;
            font-size: 3rem;
            font-weight: 800;
            color: #39c0ed;
            margin-bottom: 0.5rem;
        }
        .subtitle {
            text-align: center;
            font-size: 1.2rem;
            color: #c9c9c9;
            margin-bottom: 2rem;
        }
        .stSelectbox label {
            color: #39c0ed !important;
            font-weight: bold;
        }
        .movie-card {
            transition: transform 0.2s ease-in-out;
        }
        .movie-card:hover {
            transform: scale(1.05);
        }
        .footer {
            text-align: center;
            margin-top: 2rem;
            font-size: 0.9rem;
            color: #666;
        }
    </style>
""", unsafe_allow_html=True)

# -----------------------------
# Google Drive File IDs
# -----------------------------
SIMILARITY_FILE_ID = "1SHMQbfDk7LViEHPRnzLZf7CLD4L‑KdI4"  # for similarity.pkl
MOVIES_FILE_ID     = "1ab‑Hz7ww3qFgK2QamN7qfQK8BgbKN‑AC"  # for movie_list.pkl

# -----------------------------
# Auto‑download Pickle Files If Missing
# -----------------------------
if not os.path.exists("similarity.pkl"):
    with st.spinner("Downloading similarity data... ⏳"):
        url = f"https://drive.google.com/uc?id={SIMILARITY_FILE_ID}"
        gdown.download(url, "similarity.pkl", quiet=False)

if not os.path.exists("movie_list.pkl"):
    with st.spinner("Downloading movie list... ⏳"):
        url = f"https://drive.google.com/uc?id={MOVIES_FILE_ID}"
        gdown.download(url, "movie_list.pkl", quiet=False)

# -----------------------------
# Load Data
# -----------------------------
movies     = pickle.load(open('movie_list.pkl',    'rb'))
similarity = pickle.load(open('similarity.pkl',     'rb'))

# -----------------------------
# Functions
# -----------------------------
def fetch_poster(movie_id):
    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US"
        data = requests.get(url).json()
        poster_path = data.get('poster_path')
        if poster_path:
            return "https://image.tmdb.org/t/p/w500/" + poster_path
    except:
        pass
    return "https://via.placeholder.com/500x750?text=No+Image"

def recommend(movie):
    index = movies[movies['title'] == movie].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    recommended_movie_names   = []
    recommended_movie_posters = []

    for i in distances[1:6]:
        movie_id = movies.iloc[i[0]].movie_id
        recommended_movie_posters.append(fetch_poster(movie_id))
        recommended_movie_names.append(movies.iloc[i[0]].title)

    return recommended_movie_names, recommended_movie_posters

# -----------------------------
# Header
# -----------------------------
st.markdown("<h1 class='title'>🎬 CineMatch AI</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Find movies you’ll love — powered by machine learning & TMDb API</p>", unsafe_allow_html=True)

# -----------------------------
# Movie Selector
# -----------------------------
movie_list     = movies['title'].values
selected_movie = st.selectbox("🎥 Choose a Movie", movie_list, index=0)

# -----------------------------
# Recommendation Button
# -----------------------------
if st.button("✨ Show Recommendations"):
    with st.spinner("Finding your perfect matches... 🎯"):
        recommended_movie_names, recommended_movie_posters = recommend(selected_movie)

        st.markdown(f"<h3 style='text-align:center;color:#39c0ed;'>Top 5 Similar Movies to <b>{selected_movie}</b></h3>",
                    unsafe_allow_html=True)
        cols = st.columns(5)

        for i, col in enumerate(cols):
            with col:
                st.image(recommended_movie_posters[i], use_container_width=True, caption=recommended_movie_names[i])
                st.markdown(f"<div class='movie-card'><h5 style='text-align:center'>{recommended_movie_names[i]}</h5></div>",
                            unsafe_allow_html=True)

# -----------------------------
# Footer
# -----------------------------
st.markdown("<p class='footer'>Made with ❤️ by Abishek Mishra | Powered by TMDb API & Streamlit</p>",
            unsafe_allow_html=True)
