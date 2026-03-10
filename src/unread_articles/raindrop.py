"""Raindrop.io API client for fetching bookmarked URLs by tag."""

import httpx

BASE_URL = "https://api.raindrop.io/rest/v1"
PER_PAGE = 50


def build_search_query(tags: list[str]) -> str:
    """Build a Raindrop search query string from tags.

    Raindrop uses `#"tagname"` syntax for tag filters.
    Multiple tags are space-separated (AND logic).
    """
    return " ".join(f'#"{tag}"' for tag in tags)


def fetch_all_urls(
    token: str,
    tags: list[str],
    collection_id: int = 0,
) -> list[str]:
    """Fetch all bookmark URLs matching the given tags from Raindrop.io.

    Paginates through results until all matching bookmarks are retrieved.

    Args:
        token: Raindrop.io API bearer token.
        tags: List of tags to filter by (AND logic).
        collection_id: Raindrop collection ID (0 = all collections).

    Returns:
        List of bookmark URLs.
    """
    search = build_search_query(tags)
    headers = {"Authorization": f"Bearer {token}"}
    urls: list[str] = []
    page = 0

    with httpx.Client(timeout=30) as client:
        while True:
            resp = client.get(
                f"{BASE_URL}/raindrops/{collection_id}",
                headers=headers,
                params={"search": search, "perpage": PER_PAGE, "page": page},
            )
            resp.raise_for_status()

            items = resp.json().get("items", [])
            if not items:
                break

            urls.extend(item["link"] for item in items)

            # Stop if we got fewer items than a full page
            if len(items) < PER_PAGE:
                break

            page += 1

    return urls


def save_urls(urls: list[str], path: str = "urls.txt") -> None:
    """Write URLs to a file, one per line (overwrites existing content)."""
    with open(path, "w") as f:
        f.write("\n".join(urls) + "\n" if urls else "")
