import time

from models import Order
from produser import send_data


def get_order(pk: str):
    order = Order.get(pk)
    return order


def create_order(order: Order):
    new_order = order.save()
    return new_order


def order_completed(order: Order):
    time.sleep(5)
    order.status = "completed"
    new_order = create_order(order)
    create_order_stream(order)
    return new_order


def create_order_stream(order: Order):
    stream_name = "order_completed"
    send_data(stream_name, order.dict())
