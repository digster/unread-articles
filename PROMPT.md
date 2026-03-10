# Prompts

## 2026-03-09

Implement the following plan:

Plan: Unread Articles — Raindrop URL Fetcher + GitHub Pages Random Redirect

Context: The user wants a simple utility that pulls bookmarked URLs from Raindrop.io by tag(s), saves them to a text file, and optionally commits+pushes. The repo doubles as a GitHub Pages site that redirects visitors to a random saved URL.

File structure includes: pyproject.toml, src/unread_articles/ (cli.py, raindrop.py, git_ops.py), tests/, index.html, urls.txt.

Implementation: Raindrop API client with pagination, Typer CLI with fetch/sync commands, git operations module, GitHub Pages index.html with random redirect, pytest tests with httpx mocking.
