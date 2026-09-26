from .engine import SmallBusinessEngine


class ReportsEngine:
    def __init__(self, engine=None):
        self.engine = engine or SmallBusinessEngine()

    def financial_summary(self, business_id, start_date=None, end_date=None):
        filters = ["s.business_id = ?"]
        params = [business_id]

        if start_date:
            filters.append("s.sale_date >= ?")
            params.append(start_date)

        if end_date:
            filters.append("s.sale_date <= ?")
            params.append(end_date)

        where_sales = " AND ".join(filters)

        expense_filters = ["e.business_id = ?"]
        expense_params = [business_id]

        if start_date:
            expense_filters.append("e.expense_date >= ?")
            expense_params.append(start_date)

        if end_date:
            expense_filters.append("e.expense_date <= ?")
            expense_params.append(end_date)

        where_expenses = " AND ".join(expense_filters)

        with self.engine.connect() as conn:
            revenue = conn.execute(
                f"""
                SELECT COALESCE(SUM(s.total_amount_cents), 0) AS total
                FROM sales s
                WHERE {where_sales}
                """,
                params,
            ).fetchone()["total"]

            cash_sales = conn.execute(
                f"""
                SELECT COALESCE(SUM(s.total_amount_cents), 0) AS total
                FROM sales s
                WHERE {where_sales}
                  AND s.sale_type = 'CASH'
                """,
                params,
            ).fetchone()["total"]

            credit_sales = conn.execute(
                f"""
                SELECT COALESCE(SUM(s.total_amount_cents), 0) AS total
                FROM sales s
                WHERE {where_sales}
                  AND s.sale_type = 'CREDIT'
                """,
                params,
            ).fetchone()["total"]

            payments_filters = ["p.business_id = ?"]
            payments_params = [business_id]

            if start_date:
                payments_filters.append("p.payment_date >= ?")
                payments_params.append(start_date)

            if end_date:
                payments_filters.append("p.payment_date <= ?")
                payments_params.append(end_date)

            where_payments = " AND ".join(payments_filters)

            debt_payments = conn.execute(
                f"""
                SELECT COALESCE(SUM(p.amount_cents), 0) AS total
                FROM payments p
                WHERE {where_payments}
                """,
                payments_params,
            ).fetchone()["total"]

            expenses = conn.execute(
                f"""
                SELECT COALESCE(SUM(e.amount_cents), 0) AS total
                FROM expenses e
                WHERE {where_expenses}
                """,
                expense_params,
            ).fetchone()["total"]

            cogs = conn.execute(
                f"""
                SELECT COALESCE(
                    SUM(
                        ROUND(
                            sb.production_cost_cents
                            * si.quantity
                            / sb.quantity_produced
                        )
                    ),
                    0
                ) AS total
                FROM sale_items si
                JOIN sales s
                    ON s.id = si.sale_id
                JOIN stock_batches sb
                    ON sb.id = si.stock_batch_id
                WHERE {where_sales}
                """,
                params,
            ).fetchone()["total"]

            outstanding = conn.execute(
                """
                SELECT COALESCE(
                    SUM(amount_owed_cents - amount_paid_cents),
                    0
                ) AS total
                FROM credit_accounts
                WHERE business_id = ?
                """,
                (business_id,),
            ).fetchone()["total"]

        gross_profit = revenue - cogs
        net_profit = gross_profit - expenses
        cash_collected = cash_sales + debt_payments

        return {
            "revenue_cents": revenue,
            "cash_sales_cents": cash_sales,
            "credit_sales_cents": credit_sales,
            "debt_payments_cents": debt_payments,
            "cash_collected_cents": cash_collected,
            "credit_outstanding_cents": outstanding,
            "cogs_cents": cogs,
            "expenses_cents": expenses,
            "gross_profit_cents": gross_profit,
            "net_profit_cents": net_profit,
        }

    def batch_report(self, business_id, batch_id):
        with self.engine.connect() as conn:
            batch = conn.execute(
                """
                SELECT
                    sb.id,
                    sb.batch_reference,
                    sb.quantity_produced,
                    sb.production_cost_cents,
                    COALESCE(
                        SUM(
                            CASE
                                WHEN sm.movement_type = 'SALE'
                                THEN -sm.quantity_delta
                                ELSE 0
                            END
                        ),
                        0
                    ) AS quantity_sold,
                    COALESCE(SUM(sm.quantity_delta), 0)
                        AS quantity_remaining
                FROM stock_batches sb
                LEFT JOIN stock_movements sm
                    ON sm.stock_batch_id = sb.id
                WHERE sb.business_id = ?
                  AND sb.id = ?
                GROUP BY sb.id
                """,
                (business_id, batch_id),
            ).fetchone()

            if batch is None:
                raise ValueError("Stock batch not found.")

            sales = conn.execute(
                """
                SELECT
                    COALESCE(SUM(si.line_total_cents), 0) AS revenue,
                    COALESCE(
                        SUM(
                            ROUND(
                                sb.production_cost_cents
                                * si.quantity
                                / sb.quantity_produced
                            )
                        ),
                        0
                    ) AS cogs
                FROM sale_items si
                JOIN sales s
                    ON s.id = si.sale_id
                JOIN stock_batches sb
                    ON sb.id = si.stock_batch_id
                WHERE s.business_id = ?
                  AND si.stock_batch_id = ?
                """,
                (business_id, batch_id),
            ).fetchone()

        revenue = sales["revenue"]
        cogs = sales["cogs"]

        return {
            "batch_id": batch["id"],
            "batch_reference": batch["batch_reference"],
            "quantity_produced": batch["quantity_produced"],
            "quantity_sold": batch["quantity_sold"],
            "quantity_remaining": batch["quantity_remaining"],
            "production_cost_cents": batch["production_cost_cents"],
            "revenue_cents": revenue,
            "cogs_cents": cogs,
            "gross_profit_cents": revenue - cogs,
        }

    @staticmethod
    def money(cents):
        return f"R{cents / 100:.2f}"
