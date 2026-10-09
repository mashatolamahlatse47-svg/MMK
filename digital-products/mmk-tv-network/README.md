# MMK TV Network

Version: 0.1.0
Status: Initial local prototype

## Purpose
A lightweight, mobile-first website for MMK interviews and real people's stories.

## Current features
- Responsive homepage
- Show introduction and episode preview
- Mobile navigation
- Community and contact previews

## Not implemented yet
- Podbean player integration
- Published video episodes
- Member registration, login and discussions
- Contact form and backend

## Run locally
From the project directory:

    python -m http.server 8088 --bind 127.0.0.1

Open http://127.0.0.1:8088 in the phone browser.

Stop the server with Ctrl+C in Termux.

## Quality checks
Run:

    sh tests/check.sh

## Preservation
Keep original recordings and project backups separate. Never place secrets,
passwords, API keys or private member data in public website files.
