# Security Notes

MMK Event Ticketing & QR Pass Generator signs ticket payloads with HMAC-SHA256. This prevents a user from changing the ticket code/event data inside a QR payload without invalidating the signature.

The server stores a unique ticket code plus a hash for lookup integrity. The code functions as a bearer credential, so protect the SQLite database and server backups. The raw code is embedded in the signed ticket link/PDF.

Production checklist:

1. Set `MMK_TICKET_SECRET` to a long random secret and keep it outside Git.
2. Set `MMK_ADMIN_KEY` to a long random admin key.
3. Use HTTPS when exposing the service to the public internet.
4. Keep the SQLite database out of the repository.
5. Back up the database using your normal MMK backup process.
6. Do not expose admin API endpoints without authentication.
7. Rotate admin access when staff or contractors leave.
