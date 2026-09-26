# MMK Small Business Engine — Database Foundation

Version: 0.1.0

## Database
SQLite-compatible schema.

## Core principle
Stock movements are the source of truth for stock history.

## Money
Money is stored in cents to avoid floating-point calculation errors.

Example:
R20.50 = 2050 cents.

## Main tables
- businesses
- products
- stock_batches
- stock_movements
- sales
- sale_items
- customers
- credit_accounts
- payments
- expenses
- audit_events

## Main views
- current_stock
- credit_balances

## Business flow
STOCK
→ SALE
→ CASH OR CREDIT
→ PAYMENT
→ EXPENSES
→ PROFIT
→ REPORTS
