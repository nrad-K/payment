import time

from redis import ResponseError

from database import redis
from models import Order

key = "refund_order"
group = "payment-group"


while True:
    print("Checking Refund Order....")
    try:
        redis.xgroup_create(name=key, groupname=group)
    except ResponseError as e:
        print(e)

    try:
        # response = redis.xread(streams={key: last_job_id}, count=1, block=5000)
        responses = redis.xreadgroup(
            groupname=group, consumername="c", count=1, block=5000, streams={key: ">"}
        )

        if len(responses) == 0:
            print("Nothing to do right now, sleeping....")
            time.sleep(5)
            continue

        for response in responses:
            result = response[1][0][1]
            print(result)
            order_id = result["product_id"]
            order = Order.get(order_id)

            # Update Order
            order.status = "refund_order"
            order.save()
            print("Updated Order")

    except Exception as e:
        print(str(e))

    time.sleep(5)
