from fastapi import FastAPI

app = FastAPI(
    title="MMK API Lab",
    version="0.1.0"
)


@app.get("/")
def home():
    return {
        "company": "MMK",
        "system": "API Lab",
        "status": "online"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


@app.get("/calculator")
def calculator(price: float, quantity: int):
    total = price * quantity

    return {
        "price": price,
        "quantity": quantity,
        "total": total
    }
