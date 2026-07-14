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

Install dependencies from `requirements.txt`:

```bash
pip install -r requirements.txt
```

You also need a Hugging Face API token. Set it as an environment variable before running the app:

```bash
export HF_API_TOKEN=your_hugging_face_token_here
```

If `HF_API_TOKEN` isn't set, the app returns an error instead of calling the API.

## Tests

Install dev dependencies and run the test suite with pytest:

```bash
pip install -r requirements-dev.txt
pytest
```

The tests cover `summarizer()`'s handling of a successful response, a missing API token, a request timeout, the 503 cold-start case, the 429 rate-limit case, and other HTTP errors.

## Usage

Run the Flask app directly:

```bash
python app.py
```

This starts the development server (debug mode is on) at `http://127.0.0.1:5000/`. Open that URL, paste text into the form, and click Submit to see the summarized output.

## Status

**Work in progress** — not production ready:

- `app.run(debug=True)` is left on, which is not suitable for production use.
- Git history shows `summarizer.py`, `utils.py`, and `templates/summary.html` were deleted from the repo — suggesting the project previously had more structure (likely a separate summarizer module and utils) that was since removed, leaving all logic inlined in `app.py`.
- Unit tests exist for `summarizer()` and for the `/process` route's input validation (see `tests/`), but there are still no input length limits and no tests covering the `/` route or a real (non-mocked) API call.
- The Hugging Face "model loading" cold-start response (HTTP 503) and rate limiting (HTTP 429) are both handled with friendly retry messages.
