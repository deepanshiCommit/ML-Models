import streamlit as st
import pickle
import pandas as pd
import requests
import html
from pathlib import Path

# Get the directory where app.py is located
BASE_DIR = Path(__file__).resolve().parent

# Load movie data
with open(BASE_DIR / "movies_dict.pkl", "rb") as f:
    movies_dict = pickle.load(f)

# Load similarity matrix
with open(BASE_DIR / "similarity.pkl", "rb") as f:
    similarity = pickle.load(f)



movies = pd.DataFrame(movies_dict)


def fetch_poster(movie_id):
    url = "https://api.themoviedb.org/3/movie/{}".format(movie_id)

    try:
        response = requests.get(
            url,
            params={
                "api_key": "8265bd1679663a7ea12ac168da84d2e8",
                "language": "en-US",
            },
            timeout=(2, 5),
        )
        response.raise_for_status()
        data = response.json()

        poster_path = data.get("poster_path")
        if not poster_path:
            return None

        return "https://image.tmdb.org/t/p/w500/" + poster_path

    except requests.RequestException:
        return None


def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]
    movies_scores = sorted(list(enumerate(distances)),reverse=True, key=lambda x:x[1])[1:6]

    recommened_movies = []
    recommended_movies_posters = []
    for movie_score_tuple in movies_scores:
        movie_id = movies.iloc[movie_score_tuple[0]].movie_id
        recommened_movies.append(movies.iloc[movie_score_tuple[0]].title)
        recommended_movies_posters.append(fetch_poster(movie_id))
    return recommened_movies, recommended_movies_posters

st.title("🎬 Movie Recommender System")

selected_movie = st.selectbox(
    "Select a movie:",
    movies['title'].values
)
if st.button("Recommend"):
    recommended_movie_names, recommended_movie_posters = recommend(selected_movie)

    cols = st.columns(5, gap="medium")

    for i, col in enumerate(cols):
        if i >= len(recommended_movie_names):
            break

        with col:
            title = html.escape(recommended_movie_names[i])

            # Keep every movie title the same height
            st.markdown(
                f"""
                <div style="
                    height: 100px;
                    display: flex;
                    align-items: flex-start;
                    justify-content: center;
                    text-align: center;
                    font-size: 18px;
                    font-weight: 600;
                    line-height: 1.3;
                    overflow: hidden;
                ">
                    {title}
                </div>
                """,
                unsafe_allow_html=True
            )

            # Display poster at a consistent size
            poster = recommended_movie_posters[i]

            if poster:
                st.image(poster, width="stretch")
            else:
                st.markdown(
                    '<div style="height:220px; display:flex; '
                    'align-items:center; justify-content:center; '
                    'background:#242424; border-radius:10px;">'
                    'Poster unavailable</div>',
                    unsafe_allow_html=True
                )
