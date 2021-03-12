import datetime
from django.core.exceptions import ValidationError
from orders.models import Order, Delivery_time


def set_id(order_info):
    # create order, his id and weight
    order = Order()
    order.order_id = order_info["order_id"]
    order.weight = order_info["weight"]
    order.region = order_info["region"]
    # validation
    order.full_clean()
    return order


def set_interval(order_info, order):
    # validate
    if not isinstance(order_info['delivery_hours'], list):
        raise ValidationError(message='%s must be list' % order_info['delivery_hours'])
    for elem in order_info['delivery_hours']:
        if not isinstance(elem, str):
            raise ValidationError(message='%s elem in list must be str' % order_info['delivery_hours'])
    # prepare ans
    all_interval = []
    # create interval
    for interval in order_info['delivery_hours']:
        # create begin and end point
        if len(interval.split('-')) != 2:
            raise ValidationError(message="delivery hours not valid")
        left, right = interval.split('-')
        left = datetime.datetime.strptime(left, '%H:%M')
        right = datetime.datetime.strptime(right, '%H:%M')
        time = Delivery_time()
        time.begin = left
        time.end = right
        all_interval.append(time)
        time.order = order
    return all_interval

