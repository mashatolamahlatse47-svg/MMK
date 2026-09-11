def calculate_profit(quantity, cost_price, selling_price):
    total_cost = quantity * cost_price
    total_sales = quantity * selling_price
    profit = total_sales - total_cost

    return {
        "quantity": quantity,
        "total_cost": total_cost,
        "total_sales": total_sales,
        "profit": profit
    }


if __name__ == "__main__":
    result = calculate_profit(
        quantity=10,
        cost_price=20,
        selling_price=35
    )

    print("MMK STOCK PROFIT CALCULATOR")
    print("---------------------------")
    print(f"Quantity:    {result['quantity']}")
    print(f"Total cost:  R{result['total_cost']:.2f}")
    print(f"Total sales: R{result['total_sales']:.2f}")
    print(f"Profit:      R{result['profit']:.2f}")
