# Boitsholo Surplus & Change Tracker

A mobile-friendly Flask and SQLite application built by MMK for Boitsholo Catering & Event Services.

## Current features

- Staff login before accessing protected pages.
- Record customers or workers, locations, serving staff and optional approvers.
- Add multiple items, quantities and unit prices to a transaction.
- Calculate transaction totals, payments and change owed.
- Keep change pending until staff confirm it was physically handed over.
- Record the confirming staff member and confirmation timestamp.
- View transaction history and clear history through a protected action.

This application does not currently provide expected-cash balances, cash-float monitoring, denomination tracking or cash reconciliation.

## Requirements

- Python 3
- Flask and the dependencies listed in `requirements.txt`
- Termux or another compatible Python environment

## Run locally in Termux

From this project directory:

```bash
python -m pip install -r requirements.txt
python app.py
```

Open this address in the browser on the same phone:

`http://127.0.0.1:8065`

Stop the development server with `Ctrl+C`.

## Staff login and secrets

The local `.env` file holds the staff username, password hash and application secret key. The password itself should never be written into project documentation or committed to Git.

`auth_setup.py` is the local setup utility for creating private login settings. Keep `.env` private. Never paste its contents into chats, screenshots, logs or public repositories.

Before sharing or committing project files, check that `.env`, database files and backups are excluded. Share only files that have been reviewed.

## Run automated tests

From the project directory:

```bash
python -m py_compile app.py auth_setup.py tests/test_auth.py tests/test_history.py tests/test_money.py
python -m unittest discover -s tests -v
```

The tests use test credentials and temporary databases. Passing tests is necessary but does not by itself certify the application as production-ready.

## Database and backups

The local database is stored at:

`instance/boitsholo.db`

Before backing up or restoring the database:

1. Stop the application.
2. Copy the database to a private, secure backup location.
3. Keep backup files out of Git and public hosting uploads.
4. To restore, stop the application, preserve a copy of the current database, then copy the selected backup back to `instance/boitsholo.db`.
5. Start the application and verify that expected records are present.

Do not delete the original database as part of a backup or restore operation. Test the backup-and-restore procedure before relying on it for real business records.

## Deployment status

**This is an authenticated MVP, not yet approved for public internet use or live business operations.**

Before deployment or staff use, MMK must verify:

- Hosting suitability, persistence and service limits.
- HTTPS and secure cookie configuration.
- Secret management without uploading `.env`.
- Login abuse protection and appropriate access permissions.
- Database backup and successful restoration.
- Live testing of login, record creation, change confirmation, history and logout.
- Client approval and an agreed data-handling procedure.

Set `BOITSHOLO_COOKIE_SECURE=1` only after HTTPS is correctly configured. Keep it at `0` for local HTTP development.

Free hosting may have usage limits, expiry conditions or storage restrictions. A host that permits SQLite for testing does not necessarily recommend it for production. Confirm the current host terms before deployment. No public deployment is authorized by this README.

## Money handling

Amounts are stored as integer cents to avoid floating-point arithmetic errors. Payments below the transaction total are rejected. Staff must physically hand over the change before confirming that it was given.
