# Movie Recommender

A content-based movie recommender built with Streamlit and TMDB metadata. The app uses the included movie and cosine-similarity data files; the training notebook is optional.

## Run locally

1. Create and activate a Python environment.
2. Install dependencies with `python -m pip install -r requirements.txt`.
3. Add your TMDB API key to the ignored `.env` file as `TMDB_API_KEY=your-key`.
4. Start the app with `streamlit run app.py`.

The app still shows recommendations if no TMDB key is configured, but posters will be unavailable. You can also configure `TMDB_API_KEY` as an environment variable or in `.streamlit/secrets.toml`.

## Deploy on Streamlit Community Cloud

1. Push this repository to GitHub.
2. Create a Streamlit Community Cloud app that points to `app.py`.
3. Add `TMDB_API_KEY = "your-key"` in the app's **Settings > Secrets**.

Do not commit `.streamlit/secrets.toml` or paste a real key into source code. The key previously embedded in `app.py` should be revoked and replaced before deployment.

## Included data

- `movie_list (1).pkl` contains the movie table used by the app.
- `similarity (1).pkl.gz` is the losslessly compressed float64 similarity matrix. Its recommendation ordering was checked against the original matrix.
- `notebook86c26b4f17.ipynb` contains the original Kaggle-oriented data preparation and training workflow; it is not required to run the app.
