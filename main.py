from typing import Final

import requests
import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.background import BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import ValidationError

from crud import get_order, order_completed
from models import Order

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000/"],
    allow_methods=["*"],
    allow_headers=["*"],
)

FEE: Final[float] = 20 / 100


@app.get("/orders/{pk}")
def get(pk: str):
    order = get_order(pk)
    return order


@app.post("/orders")
async def create(request: Request, background_tasks: BackgroundTasks):
    body = await request.json()
    if body["id"] is None:
        message = "Bad Request Body"
        raise HTTPException(status_code=400, detail=message)

    if body["quantity"] is None:
        message = "Bad Request Body"
        raise HTTPException(status_code=400, detail=message)

    try:
        req = requests.get("http://localhost:8000/products/%s" % body["id"])
    except requests.exceptions.RequestException:
        message = "Internal Server Error"
        raise HTTPException(status_code=500, detail=message)

    product = req.json()

    try:
        order = Order(
            product_id=body["id"],
            price=product["price"],
            fee=FEE * product["price"],
            total=(1 + FEE) * product["price"],
            quantity=body["quantity"],
            status="pending",
        )
    except ValidationError:
        message = "Internal Server Error"
        raise HTTPException(status_code=500, detail=message)

    background_tasks.add_task(order_completed, order)

    new_order = order_completed(order)

    return new_order


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8001)
