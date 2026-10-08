# MMK BUSINESS STARTER SYSTEM

## MMK Digital Business Tool

**Product Owner:** MMK
**Product Name:** MMK Business Starter System
**Category:** Digital Business Tools
**Version:** 1.1.0
**Status:** Tested Product

## About the Product

MMK Business Starter is a simple reusable digital business management system built by MMK for small and growing businesses.

The system brings business information, products, stock, customers, sales, debt tracking and reports into one lightweight browser-based tool.

This version was built as a practical standalone web product that can run locally in a browser.

## Version 1.1.0 Improvements

### Sales
- Available products are displayed directly in Sales.
- Products can be selected from the Sales product list.
- Products can be added from the Sales screen.
- Sales total is calculated automatically.
- Cost total is calculated automatically.
- Gross profit is calculated automatically.
- Stock remaining is calculated automatically.
- Stock is reduced automatically after a successful sale.

## What We Built

### Business Information
Records:
- Business name
- Owner name
- Phone / WhatsApp
- Email
- Website
- Business category

### Products
Records:
- Product name
- Category
- Selling price
- Cost price
- Stock quantity

Profit per unit is calculated automatically.

### Customers
Records:
- Customer name
- Money owed
- Debt history
- Notes

Debt transactions can include the date taken.

### Sales
Supports:
- Cash
- Credit
- Partial Payment

The system automatically calculates:
- Sales total
- Cost total
- Profit
- Amount owed

Stock is reduced automatically after a sale.

Credit and partial-payment sales update customer debt history.

### Reports
Reports provide:
- Total sales
- Total cost
- Total profit
- Cash received
- Outstanding debt
- Customers
- Products
- Units sold
- Current stock
- Sales history
- Customer debt report
- Product and stock report

## MMK Product Architecture

MASTER PRODUCT
→ GENERIC COMMERCIAL VERSION
→ MMK-BRANDED VERSION
→ CLIENT-CUSTOMIZED VERSION

The purpose is to build reusable products that can be customized and delivered to different customers.

## Technology

- HTML
- CSS
- JavaScript
- Browser localStorage
- Python HTTP server for local testing

## Running the Product

From this directory:

```bash
python -m http.server 8080 --directory web
echo "MMK TERMINAL OK"
