import gzip
import html
import inspect
import os
import pickle
from pathlib import Path

import requests
import streamlit as st
from dotenv import load_dotenv
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

PROJECT_DIR = Path(__file__).resolve().parent
load_dotenv(PROJECT_DIR / ".env")


@st.cache_resource
def load_recommender_data():
    with (PROJECT_DIR / "movie_list (1).pkl").open("rb") as movie_file:
        movies = pickle.load(movie_file)
    with gzip.open(
        PROJECT_DIR / "similarity (1).pkl.gz", "rb"
    ) as similarity_file:
        similarity = pickle.load(similarity_file)
    if len(movies) != similarity.shape[0]:
        raise ValueError(
            "Movie data and similarity matrix have different sizes."
        )
    return movies, similarity


def get_tmdb_api_key():
    api_key = os.getenv("TMDB_API_KEY")
    if api_key:
        return api_key
    secrets_files = (
        PROJECT_DIR / ".streamlit" / "secrets.toml",
        Path.cwd() / ".streamlit" / "secrets.toml",
        Path.home() / ".streamlit" / "secrets.toml",
    )
    if not any(path.is_file() for path in secrets_files):
        return None
    return st.secrets.get("TMDB_API_KEY")


def request_tmdb(url, params):
    try:
        return requests.get(url, params=params, timeout=(3.05, 8))
    except requests.ConnectionError:
        retry = Retry(
            total=2,
            connect=2,
            read=1,
            backoff_factor=0.25,
            allowed_methods=frozenset({"GET"}),
        )
        with requests.Session() as session:
            session.trust_env = False
            session.mount("https://", HTTPAdapter(max_retries=retry))
            return session.get(url, params=params, timeout=(3.05, 8))


def fetch_poster(movie_id):
    api_key = get_tmdb_api_key()
    if not api_key:
        return None

    url = f"https://api.themoviedb.org/3/movie/{movie_id}"
    try:
        response = request_tmdb(
            url,
            {"api_key": api_key, "language": "en-US"},
        )
        response.raise_for_status()
        poster_path = response.json().get("poster_path")
        if not poster_path:
            return None
        return "https://image.tmdb.org/t/p/w500/" + poster_path
    except (requests.RequestException, ValueError, AttributeError):
        return None


def recommend(movie):
    index = movies[movies["title"] == movie].index[0]
    distances = sorted(
        enumerate(similarity[index]), reverse=True, key=lambda item: item[1]
    )
    recommended_movie_names = []
    recommended_movie_posters = []
    recommendations = [item for item in distances if item[0] != index][:10]
    for movie_index, _ in recommendations:
        movie_id = movies.iloc[movie_index].movie_id
        recommended_movie_posters.append(fetch_poster(movie_id))
        recommended_movie_names.append(movies.iloc[movie_index].title)

    return recommended_movie_names, recommended_movie_posters


def image_width_options():
    image_parameters = inspect.signature(st.image).parameters
    if "use_container_width" in image_parameters:
        return {"use_container_width": True}
    if "use_column_width" in image_parameters:
        return {"use_column_width": True}
    return {"width": "stretch"}


st.header("Movie Recommender System")
movies, similarity = load_recommender_data()
if not get_tmdb_api_key():
    st.info("Set TMDB_API_KEY in Streamlit secrets to load movie posters.")

movie_list = movies["title"].values
selected_movie = st.selectbox(
    "Type or select a movie from the dropdown",
    movie_list
)

if st.button("Show Recommendation"):

    recommended_movie_names, recommended_movie_posters = recommend(
        selected_movie
    )

    for row_start in range(0, len(recommended_movie_names), 5):
        cols = st.columns(5)
        for column_index, col in enumerate(cols):
            movie_index = row_start + column_index
            if movie_index >= len(recommended_movie_names):
                break

            with col:
                st.markdown(
                    f"""
                    <div style="
                        height: 65px;
                        display: flex;
                        align-items: flex-start;
                        overflow: hidden;
                    ">
                        <div style="
                            font-size: 17px;
                            font-weight: 600;
                            line-height: 1.3;
                            display: -webkit-box;
                            -webkit-line-clamp: 2;
                            -webkit-box-orient: vertical;
                            overflow: hidden;
                        ">
                            {html.escape(str(recommended_movie_names[movie_index]))}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                if recommended_movie_posters[movie_index]:
                    st.image(
                        recommended_movie_posters[movie_index],
                        **image_width_options(),
                    )
                else:
                    st.caption("Poster unavailable")
