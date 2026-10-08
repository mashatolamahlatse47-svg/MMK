# MMK Café SaaS V0.1

A lightweight, mobile-first café management web application built by MMK.

## V0.1 Modules

- Dashboard
- Menu management
- Customer-facing menu display
- Order recording
- Order status tracking
- Customer management
- Customer/order linking
- Café settings
- Local data storage
- Café data export

## Technology

- HTML
- CSS
- JavaScript
- Browser localStorage
- No external runtime dependencies

## Running Locally

From the project directory:

```bash
serve app -l 8091
cd ~/MMK/digital-products/mmk-cafe-saas-v0.1 && \
printf '0.1.0\n' > VERSION && \
cat > RELEASE_NOTES.md <<'EOF'
# MMK Café SaaS — Release Notes

## Version 0.1.0

Initial MMK Café SaaS release candidate.

### Included
- Dashboard with sales and order summaries
- Menu management
- Order creation and status tracking
- Customer records
- Customer-to-order linking
- Café settings
- Local browser data storage
- JSON data export

### Quality checks
- JavaScript syntax check passed
- Diff/whitespace check passed
- Dashboard, Menu, Orders, Customers and Settings integration passed
- Navigation regression test passed
- Project backups verified
- Secret-file scan completed

### Known limitations
- Data is stored locally in the browser.
- Settings persistence and JSON export were not fully tested.
- JSON import is not included.
- Profit reporting is deferred until ingredient costs can be recorded reliably.
- This release is not yet a multi-user hosted SaaS.

### Release status
V0.1.0 — Initial release candidate.
