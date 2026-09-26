from .engine import SmallBusinessEngine


class ProfitEngine:
    def __init__(self, engine=None):
        self.engine = engine or SmallBusinessEngine()

    def batch_summary(self, business_id, batch_id):
        with self.engine.connect() as conn:
            batch = conn.execute(
                """
                SELECT
                    sb.id,
                    sb.batch_reference,
                    sb.product_id,
                    sb.quantity_produced,
                    sb.production_cost_cents,
                    sb.production_date,
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
                    COALESCE(
                        SUM(sm.quantity_delta),
                        0
                    ) AS quantity_remaining
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
                    COALESCE(SUM(si.line_total_cents), 0) AS revenue
                FROM sale_items si
                JOIN sales s
                    ON s.id = si.sale_id
                WHERE s.business_id = ?
                  AND si.stock_batch_id = ?
                """,
                (business_id, batch_id),
            ).fetchone()

        quantity_sold = batch["quantity_sold"]
        quantity_produced = batch["quantity_produced"]
        production_cost = batch["production_cost_cents"]
        revenue = sales["revenue"]

        if quantity_produced > 0:
            cost_sold = round(
                production_cost * quantity_sold / quantity_produced
            )
        else:
            cost_sold = 0

        gross_profit = revenue - cost_sold

        return {
            "batch_id": batch["id"],
            "batch_reference": batch["batch_reference"],
            "quantity_produced": quantity_produced,
            "quantity_sold": quantity_sold,
            "quantity_remaining": batch["quantity_remaining"],
            "production_cost_cents": production_cost,
            "revenue_cents": revenue,
            "cost_of_goods_sold_cents": cost_sold,
            "gross_profit_cents": gross_profit,
        }

    def business_summary(self, business_id):
        with self.engine.connect() as conn:
            revenue = conn.execute(
                """
                SELECT COALESCE(SUM(total_amount_cents), 0) AS total
                FROM sales
                WHERE business_id = ?
                """,
                (business_id,),
            ).fetchone()["total"]

            expenses = conn.execute(
                """
                SELECT COALESCE(SUM(amount_cents), 0) AS total
                FROM expenses
                WHERE business_id = ?
                """,
                (business_id,),
            ).fetchone()["total"]

            credit_outstanding = conn.execute(
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

            cash_collected = conn.execute(
                """
                SELECT
                    COALESCE(
                        (SELECT SUM(total_amount_cents)
                         FROM sales
                         WHERE business_id = ?
                           AND sale_type = 'CASH'),
                        0
                    )
                    +
                    COALESCE(
                        (SELECT SUM(amount_cents)
                         FROM payments
                         WHERE business_id = ?),
                        0
                    ) AS total
                """,
                (business_id, business_id),
            ).fetchone()["total"]

        return {
            "revenue_cents": revenue,
            "cash_collected_cents": cash_collected,
            "credit_outstanding_cents": credit_outstanding,
            "expenses_cents": expenses,
            "profit_before_expenses_cents": None,
        }
