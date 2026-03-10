# Prompts

## 2026-03-09

Implement the following plan:

Plan: Unread Articles — Raindrop URL Fetcher + GitHub Pages Random Redirect

Context: The user wants a simple utility that pulls bookmarked URLs from Raindrop.io by tag(s), saves them to a text file, and optionally commits+pushes. The repo doubles as a GitHub Pages site that redirects visitors to a random saved URL.

File structure includes: pyproject.toml, src/unread_articles/ (cli.py, raindrop.py, git_ops.py), tests/, index.html, urls.txt.

Implementation: Raindrop API client with pagination, Typer CLI with fetch/sync commands, git operations module, GitHub Pages index.html with random redirect, pytest tests with httpx mocking.

---

## 2026-03-09 (2)

Fix: Handle "nothing to commit" gracefully in sync command. When `sync` fetches URLs identical to what's already in `urls.txt`, `git commit` exits with status 1. Modify `git_ops.py` to check for staged changes using `git diff --cached --quiet` before committing, return a boolean, and update `cli.py` to show an appropriate message.
