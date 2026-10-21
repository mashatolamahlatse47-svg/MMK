# MMK WhatsApp Order Forms
Version: 0.3.0

A lightweight order-taking product for small businesses, built by MMK.

## Two versions

### 1. Static demo
The static demo lets a business configure a menu in the browser and prepare
customer orders for WhatsApp. Browser settings do not automatically sync
between devices.

To open it locally:
```bash
python -m http.server 8080 --bind 127.0.0.1
```
Open http://127.0.0.1:8080/index.html

Public demo: https://admirable-salamander-b102eb.netlify.app/

### 2. Authenticated local prototype
The Flask prototype includes:
- Owner registration and login
- Business-specific product management
- Customer order forms and WhatsApp order links
- Order listing and status updates
- Printable order receipts, including a Save PDF option
- Shop-scoped order access and CSRF protection

To start the local prototype:
```bash
python server/auth_app.py
```
Open http://127.0.0.1:8091

Stop the server with Ctrl+C.

## Important safety notice
The Flask app is a local prototype, not production-ready. Do not enter real
customer information or use it for live business transactions yet.
The local database and session key are stored under `instance/`; keep them
private and back up the database safely.

Do not deploy the Flask app publicly until production security, hosting,
persistent storage, database backups, and acceptance testing are completed.

## Checks
Run from this project directory:
```bash
python -m py_compile server/auth_app.py tests/check_auth.py
python tests/check_auth.py
sh tests/check.sh
```

## Before selling or launching
- Test registration, login, product management, ordering and order totals.
- Verify order status changes and receipt contents.
- Confirm users cannot access another shop's orders or receipts.
- Test on another phone and confirm the business owner's WhatsApp number.
- Set up secure hosting, persistent storage and tested backups.
- Complete privacy, security and real-business acceptance testing.
- Agree on pricing, hosting, support and changes with the customer.
