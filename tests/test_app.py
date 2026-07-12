import os
from unittest.mock import patch, MagicMock

import requests

os.environ.setdefault("HF_API_TOKEN", "test-token")

from app import summarizer


def _mock_response(status_code=200, json_data=None, headers=None, raise_for_status_error=None):
    response = MagicMock()
    response.status_code = status_code
    response.headers = headers or {}
    response.json.return_value = json_data
    if raise_for_status_error:
        response.raise_for_status.side_effect = raise_for_status_error
    return response


def test_summarizer_missing_token():
    with patch.dict(os.environ, {}, clear=True):
        assert summarizer("some text") == "Error: HF_API_TOKEN environment variable is not set."


@patch("app.requests.post")
def test_summarizer_success(mock_post):
    mock_post.return_value = _mock_response(json_data=[{"summary_text": "a short summary"}])
    assert summarizer("some long text") == "a short summary"


@patch("app.requests.post")
def test_summarizer_timeout(mock_post):
    mock_post.side_effect = requests.exceptions.Timeout()
    assert summarizer("some text") == "Error: The request timed out. Please try again later."


@patch("app.requests.post")
def test_summarizer_model_loading(mock_post):
    response = _mock_response(
        status_code=503,
        json_data={"estimated_time": 12.5},
        raise_for_status_error=requests.exceptions.HTTPError(response=MagicMock(status_code=503)),
    )
    mock_post.return_value = response
    result = summarizer("some text")
    assert "12 seconds" in result


@patch("app.requests.post")
def test_summarizer_rate_limited(mock_post):
    response = _mock_response(
        status_code=429,
        headers={"Retry-After": "30"},
        raise_for_status_error=requests.exceptions.HTTPError(),
    )
    mock_post.return_value = response
    result = summarizer("some text")
    assert "30 seconds" in result


@patch("app.requests.post")
def test_summarizer_generic_http_error(mock_post):
    response = _mock_response(
        status_code=500,
        raise_for_status_error=requests.exceptions.HTTPError(),
    )
    response.text = "internal error"
    mock_post.return_value = response
    result = summarizer("some text")
    assert result == "Error summarizing text. Please try again later."
