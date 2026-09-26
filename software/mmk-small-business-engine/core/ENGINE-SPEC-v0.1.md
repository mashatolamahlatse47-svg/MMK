# MMK Small Business Engine — Engine Specification v0.1

## 1. Purpose

A reusable business engine for small businesses that need to manage:

- Products
- Stock
- Sales
- Customers
- Credit / Take Now, Pay Later
- Payments
- Expenses
- Profit
- Reports
- Audit history

The engine must be reusable across different business types.

Examples:

- Vetkoek
- Kota
- Spaza
- Catering
- Small retail
- Other micro-businesses

---

## 2. Core Business Flow

BUSINESS
→ PRODUCTS
→ STOCK
→ SALES
→ CASH OR CREDIT
→ PAYMENTS
→ EXPENSES
→ PROFIT
→ REPORTS

---

## 3. Core Records

### Business

Stores business-level configuration.

Example fields:

- id
- name
- currency
- created_at
- updated_at

### Product

Stores products sold by the business.

Example fields:

- id
- name
- unit
- selling_price
- active
- created_at
- updated_at

### Stock Batch

Stores stock entering the business.

Example fields:

- id
- product_id
- batch_reference
- quantity_produced
- quantity_remaining
- production_cost
- production_date
- created_at

### Sale

Records stock leaving the business.

Example fields:

- id
- product_id
- quantity
- unit_price
- total_amount
- sale_type
- customer_id
- sale_date
- created_at

Sale types:

- CASH
- CREDIT

### Customer

Stores customers who may owe money.

Example fields:

- id
- name
- phone
- notes
- active
- created_at
- updated_at

### Credit Account / Credit Sale

Tracks money owed by customers.

Example fields:

- id
- customer_id
- sale_id
- amount_owed
- amount_paid
- balance
- due_date
- status
- created_at
- updated_at

Statuses:

- OPEN
- PARTIALLY_PAID
- PAID
- OVERDUE

### Payment

Records money received.

Example fields:

- id
- customer_id
- credit_id
- amount
- payment_method
- payment_date
- notes
- created_at

### Expense

Records business expenses.

Example fields:

- id
- category
- description
- amount
- expense_date
- created_at

Examples:

- Ingredients
- Oil
- Gas
- Electricity
- Packaging
- Transport
- Other

---

## 4. Stock Rules

When stock is created:

quantity_remaining = quantity_produced

When a cash sale occurs:

quantity_remaining decreases.

When a credit sale occurs:

quantity_remaining decreases.

A sale must never reduce stock below zero.

---

## 5. Sales Rules

### Cash Sale

Stock decreases.

Sales revenue increases.

Cash received increases.

Customer debt does not increase.

### Credit Sale

Stock decreases.

Sales revenue increases.

Cash received does not increase immediately.

Customer debt increases.

---

## 6. Payment Rules

When a customer pays a credit balance:

customer balance decreases.

cash received increases.

Payment history is recorded.

A credit account becomes PAID when balance reaches zero.

---

## 7. Profit Rules

Revenue:

sum of completed sales.

Business costs:

production costs + recorded expenses, according to the selected reporting method.

Basic profit:

revenue - costs

The engine must keep revenue, cash received and outstanding credit separate.

---

## 8. Important Business Distinctions

SALES ≠ CASH

CASH ≠ PROFIT

CREDIT ≠ CASH RECEIVED

PROFIT must be calculated from recorded revenue and costs.

---

## 9. Reporting Requirements

The engine should eventually provide:

- Current stock
- Stock movement
- Sales
- Cash received
- Credit sales
- Customer balances
- Payments
- Expenses
- Revenue
- Costs
- Profit
- Batch summary
- Daily summary
- Weekly summary
- Monthly summary

---

## 10. Security Requirements

Important business actions should be traceable.

The engine should support:

- Validation
- Audit events
- Safe database operations
- No negative stock
- No invalid payments
- Controlled data updates
- Backup/export capability

---

## 11. Reusability Principle

Business-specific names, products and workflows should be configurable.

The core engine should not contain hard-coded Vetkoek-only logic.

Vetkoek is a customised product built on the engine.

---

## Version

Engine Version: 0.1.0

Stage: Specification

Status: Foundation specification created.
