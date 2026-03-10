"""Tests for Raindrop.io API client and URL persistence."""

import json
import tempfile
from pathlib import Path

import httpx
import pytest

from unread_articles.raindrop import (
    BASE_URL,
    PER_PAGE,
    build_search_query,
    fetch_all_urls,
    save_urls,
)


# ── build_search_query ──────────────────────────────────────────────


class TestBuildSearchQuery:
    def test_single_tag(self):
        assert build_search_query(["python"]) == '#"python"'

    def test_multiple_tags(self):
        result = build_search_query(["python", "ai"])
        assert result == '#"python" #"ai"'

    def test_tag_with_spaces(self):
        result = build_search_query(["machine learning"])
        assert result == '#"machine learning"'

    def test_empty_tags(self):
        assert build_search_query([]) == ""


# ── save_urls ────────────────────────────────────────────────────────


class TestSaveUrls:
    def test_writes_urls_one_per_line(self, tmp_path: Path):
        urls = ["https://example.com/a", "https://example.com/b"]
        path = str(tmp_path / "urls.txt")

        save_urls(urls, path=path)

        content = Path(path).read_text()
        assert content == "https://example.com/a\nhttps://example.com/b\n"

    def test_overwrites_existing_file(self, tmp_path: Path):
        path = str(tmp_path / "urls.txt")

        save_urls(["https://old.com"], path=path)
        save_urls(["https://new.com"], path=path)

        content = Path(path).read_text()
        assert content == "https://new.com\n"

    def test_empty_list_writes_empty_file(self, tmp_path: Path):
        path = str(tmp_path / "urls.txt")

        save_urls([], path=path)

        content = Path(path).read_text()
        assert content == ""


# ── fetch_all_urls ───────────────────────────────────────────────────


def _make_raindrop_response(urls: list[str]) -> dict:
    """Helper to build a Raindrop API response body."""
    return {"items": [{"link": url, "title": f"Title for {url}"} for url in urls]}


class TestFetchAllUrls:
    def test_single_page(self, httpx_mock):
        """Fetches URLs from a single page of results."""
        urls = [f"https://example.com/{i}" for i in range(3)]
        httpx_mock.add_response(json=_make_raindrop_response(urls))

        result = fetch_all_urls("test-token", ["python"])

        assert result == urls

    def test_pagination(self, httpx_mock):
        """Fetches URLs across multiple pages."""
        # First page: full page of results
        page1_urls = [f"https://example.com/{i}" for i in range(PER_PAGE)]
        httpx_mock.add_response(json=_make_raindrop_response(page1_urls))

        # Second page: partial results (end of pagination)
        page2_urls = [f"https://example.com/{PER_PAGE + i}" for i in range(5)]
        httpx_mock.add_response(json=_make_raindrop_response(page2_urls))

        result = fetch_all_urls("test-token", ["python"])

        assert len(result) == PER_PAGE + 5
        assert result == page1_urls + page2_urls

    def test_empty_results(self, httpx_mock):
        """Returns empty list when no bookmarks match."""
        httpx_mock.add_response(json={"items": []})

        result = fetch_all_urls("test-token", ["nonexistent"])

        assert result == []

    def test_sends_correct_auth_header(self, httpx_mock):
        """Verifies the Authorization header is sent correctly."""
        httpx_mock.add_response(json={"items": []})

        fetch_all_urls("my-secret-token", ["python"])

        request = httpx_mock.get_request()
        assert request.headers["Authorization"] == "Bearer my-secret-token"

    def test_sends_correct_search_params(self, httpx_mock):
        """Verifies search query and collection ID in the request."""
        httpx_mock.add_response(json={"items": []})

        fetch_all_urls("token", ["python", "ai"], collection_id=42)

        request = httpx_mock.get_request()
        assert request.url.path == "/rest/v1/raindrops/42"
        assert '#"python" #"ai"' in str(request.url.params.get("search"))

    def test_api_error_raises(self, httpx_mock):
        """Raises on non-2xx API responses."""
        httpx_mock.add_response(status_code=401)

        with pytest.raises(httpx.HTTPStatusError):
            fetch_all_urls("bad-token", ["python"])
