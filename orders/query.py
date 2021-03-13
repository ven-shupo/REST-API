import datetime
from django.core.exceptions import ValidationError
from django.db import IntegrityError

from orders.models import Order, Delivery_time, Order_to_Worker
from couriers.models import Worker, Region, Schedule


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


def assign_orders(courier_id):
    # get courier
    courier = Worker.objects.get(courier_id=courier_id)
    courier_type = courier.courier_type
    # find regions for these courier
    courier_regions = []
    for i in Region.objects.filter(couriers__courier_id=courier_id):
        courier_regions.append(i.place)
    # find working time for these courier
    courier_time = Schedule.objects.filter(courier_id=courier_id)

    # prepare ans
    assign_time = datetime.datetime.now()
    assign_order_id = []
    time = None

    # find suitable order
    for order in Order.objects.all():  # sorting out orders
        ans = find_suitable_order(order, courier, courier_regions, courier_type, courier_time, assign_time)
        if isinstance(ans, list):
            assign_order_id.append({"id": ans[0]})
            time = ans[1]

    return assign_order_id, time


def find_suitable_order(order, courier, courier_regions, courier_type, courier_time, assign_time):
    if order.region in courier_regions:  # compare region
        if compare_weight_type(order, courier_type):  # compare weight
            for delivery_time in Delivery_time.objects.all():  # sorting out delivery time
                for free_time in courier_time:  # sorting out working hours
                    if compare_delivery_working_time(delivery_time, free_time):  # compare time
                        try:
                            try:
                                task = Order_to_Worker.objects.get(order=order, courier=courier)
                            except:
                                task = Order_to_Worker.objects.create(order=order, courier=courier,
                                                                      time_order=assign_time)
                                task.save()
                            return [order.order_id, task.time_order]
                        except IntegrityError:
                            pass


def compare_weight_type(order, courier_type):
    if courier_type == "foot":
        if order.weight <= 10:
            return True
    if courier_type == "bike":
        if order.weight <= 15:
            return True
    if courier_type == "car":
        if order.weight <= 50:
            return True
    return False


def compare_delivery_working_time(delivery_time, working_time):
    if delivery_time.begin >= working_time.begin or delivery_time.end <= working_time.end:
        return True
    return False
