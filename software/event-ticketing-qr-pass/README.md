# MMK Event Ticketing & QR Pass Generator

**MMK Asset | Version 1.0.0**

A reusable event-ticketing web app for clubs, lounges, churches, promoters, schools and community events. Create an event, issue unique tickets, generate QR-code PDF passes, share ticket links through WhatsApp, and validate tickets at the door.

## Core flow

`Create Event → Issue Ticket → Generate PDF → WhatsApp Share → Scan QR → Check In`

## Included

- Multi-event SQLite database
- Unique, signed ticket codes
- QR-code PDF ticket generation
- Public ticket/check-in endpoint
- Duplicate-scan protection
- Ticket status tracking: issued / checked-in / cancelled
- Capacity checks
- Bulk ticket issuing from CSV text
- Event PDF + attendance ledger ZIP export
- WhatsApp-ready share links
- Admin-key protection for management actions
- South African Rand (ZAR) defaults
- Mobile-friendly admin interface

## Product position

This is an installable MMK software asset. It can be sold as a hosted service, installed for a client, or customized with the client's branding.

## Important v1.0 scope note

The WhatsApp feature uses a WhatsApp share link. It opens WhatsApp with a prepared message containing the ticket link; the operator still chooses the recipient and sends the message. Fully automated WhatsApp Business Cloud API delivery is intentionally reserved for a future integration.

## Quick start on Termux

```bash
cd ~/MMK/software/event-ticketing-qr-pass
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export MMK_ADMIN_KEY='replace-with-a-long-random-admin-key'
export MMK_PUBLIC_BASE_URL='http://127.0.0.1:5055'
python app.py
```

Open `http://127.0.0.1:5055`.

## Suggested production environment variables

- `MMK_ADMIN_KEY` — required for admin API actions
- `MMK_TICKET_SECRET` — persistent HMAC signing secret; set this in production
- `MMK_PUBLIC_BASE_URL` — public HTTPS base URL used inside QR links and WhatsApp messages
- `MMK_HOST` — bind host; default `127.0.0.1`
- `MMK_PORT` — bind port; default `5055`

## Security

Do not commit the SQLite database, `.ticket-secret`, or production secrets. Use HTTPS for any public deployment. Protect admin actions behind the admin key and rotate keys when staff access changes.
