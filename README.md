# Text Summarizer

A minimal Flask web app that summarizes user-submitted text using Hugging Face's hosted `facebook/bart-large-cnn` model.

## What it does

- Serves a single-page HTML form (`templates/index.html`) where a user pastes text into a textarea.
- On submit, JavaScript sends the text via `fetch` to a Flask backend endpoint (`/process`).
- The backend (`app.py`) forwards the text to the Hugging Face Inference API (BART CNN summarization model) and returns the generated summary as JSON.
- The summary is displayed back in a read-only textarea on the same page.

## Tech stack

- Python 3 / Flask (`app.py`)
- `requests` for calling the Hugging Face Inference API
- Vanilla HTML/CSS/JavaScript for the frontend (`templates/index.html`)
- External API: Hugging Face Inference API (`facebook/bart-large-cnn` model)

## Setup / install

There is no `requirements.txt` in the repo, so dependencies must be installed manually. Based on the imports in `app.py`, you need:

```bash
pip install flask requests
```

You also need a Hugging Face API token. Set it as an environment variable before running the app:

```bash
export HF_API_TOKEN=your_hugging_face_token_here
```

If `HF_API_TOKEN` isn't set, the app returns an error instead of calling the API.

## Usage

Run the Flask app directly:

```bash
python app.py
```

This starts the development server (debug mode is on) at `http://127.0.0.1:5000/`. Open that URL, paste text into the form, and click Submit to see the summarized output.

## Status

**Work in progress** — not production ready:

- No `requirements.txt` (or `pyproject.toml`) is committed, so dependencies aren't pinned or easily installable.
- `app.run(debug=True)` is left on, which is not suitable for production use.
- Git history shows `summarizer.py`, `utils.py`, and `templates/summary.html` were deleted from the repo, and their compiled bytecode (`__pycache__/summarizer.cpython-312.pyc`, `__pycache__/utils.cpython-312.pyc`) is still present — suggesting the project previously had more structure (likely a separate summarizer module and utils) that was since removed, leaving all logic inlined in `app.py`.
- No tests, no input length limits, and no handling of Hugging Face API rate limiting/cold-start responses (the free Inference API often returns a "model loading" response that isn't handled here).
