import os
from unittest.mock import patch, MagicMock

import requests

os.environ.setdefault("HF_API_TOKEN", "test-token")

from app import app, summarizer


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


def test_index_route():
    client = app.test_client()
    response = client.get('/')
    assert response.status_code == 200


@patch("app.summarizer")
def test_process_returns_summary(mock_summarizer):
    mock_summarizer.return_value = "a short summary"
    client = app.test_client()
    response = client.post('/process', data={'user_input': 'some long text to summarize'})
    assert response.status_code == 200
    assert response.get_json() == {"summary": "a short summary"}
    mock_summarizer.assert_called_once_with('some long text to summarize')


def test_process_rejects_whitespace_only_input():
    client = app.test_client()
    response = client.post('/process', data={'user_input': '   '})
    assert response.status_code == 400
    assert response.get_json() == {"error": "No input provided"}


def test_process_rejects_missing_input():
    client = app.test_client()
    response = client.post('/process', data={})
    assert response.status_code == 400
    assert response.get_json() == {"error": "No input provided"}


def test_process_rejects_input_over_max_length():
    from app import MAX_INPUT_LENGTH

    client = app.test_client()
    response = client.post('/process', data={'user_input': 'a' * (MAX_INPUT_LENGTH + 1)})
    assert response.status_code == 400
    assert response.get_json() == {
        "error": f"Input exceeds maximum length of {MAX_INPUT_LENGTH} characters"
    }
