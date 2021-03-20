import datetime
import json
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.db import IntegrityError
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from couriers.models import Courier
from orders.models import Order_to_Courier
from orders.query import set_id, set_interval, assign_orders, complete_order


@csrf_exempt
@require_POST
def post_orders(request):
    # read json
    list_order = json.loads(request.body)["data"]
    # prepare list for response
    bad_id = []
    pretty_id = []
    valid_data = {"valid": []}

    # validation
    all_id = []
    not_unique_id = []
    for order in list_order:
        if order['order_id'] in all_id:
            not_unique_id.append(order['order_id'])
        else:
            all_id.append(order['order_id'])

    if not_unique_id:
        bad_id = list(set(not_unique_id))
        data_response = {"validation_error": {"orders": bad_id}}
        status_response = 400
        return JsonResponse(data_response, status=status_response)

    # flags
    have_not_valid_data = 0

    # fill in db
    for order_info in list_order:
        try:
            order = set_id(order_info)
            all_interval = set_interval(order_info, order)
        except ValueError as error:
            have_not_valid_data = 1
            print(error)
            bad_id.append({'id': order_info['order_id']})
        except IntegrityError as error:
            have_not_valid_data = 1
            print(error)
            bad_id.append({'id': order_info['order_id']})
        except ValidationError as error:
            have_not_valid_data = 1
            print(error)
            bad_id.append({'id': order_info['order_id']})
        except KeyError as error:
            have_not_valid_data = 1
            print(error)
            bad_id.append({'id': order_info['order_id']})
        else:
            if order:
                valid_data["valid"].append({"order_id": order,
                                            "delivery_hours": all_interval
                                            })
                pretty_id.append({'id': order_info['order_id']})
            else:
                have_not_valid_data = 1
                bad_id.append({'id': order_info['order_id']})

    # save data if all complete with succeed
    if have_not_valid_data == 0:
        for order_info in valid_data["valid"]:
            order_info["order_id"].save()
            for interval in order_info["delivery_hours"]:
                interval.save()

    # create response
    if not bad_id:
        data_response = {"orders": pretty_id}
        status_response = 201
    else:
        data_response = {"validation_error": {"orders": bad_id}}
        status_response = 400

    return JsonResponse(data_response, status=status_response)


@csrf_exempt
@require_POST
def assign(request):
    # read json
    courier_id = json.loads(request.body)["courier_id"]
    # validation
    try:
        courier = Courier.objects.get(courier_id=courier_id)
    except ObjectDoesNotExist as error:
        print(error)
        return HttpResponse(status=400)
    else:
        if len(Order_to_Courier.objects.filter(courier=courier)) > 0:
            not_complete_order_list = []
            not_complete_assign_time = None
            for task in Order_to_Courier.objects.filter(courier=courier):
                not_complete_order_list.append({"id": task.order.order_id})
                not_complete_assign_time = task.time_order
            data_response = {"orders": not_complete_order_list,
                             "assign_time": not_complete_assign_time}
            return JsonResponse(data_response, status=200)
    # assign orders
    try:
        # assign orders
        order_id_list, assign_time = assign_orders(courier_id)

        if not assign_time:
            # prepare response
            data_response = {"orders": []}
        else:
            # prepare response
            data_response = {"orders": order_id_list,
                             "assign_time": assign_time}
        return JsonResponse(data_response,
                            status=200)
    except ObjectDoesNotExist as error:
        print(error)
        return HttpResponse(status=400)
    except ValueError as error:
        print(error)
        return HttpResponse(status=400)


@csrf_exempt
@require_POST
def complete(request):
    # read json
    data = json.loads(request.body)
    courier_id = data["courier_id"]
    order_id = data["order_id"]
    # read DateTime
    try:
        complete_time = datetime.datetime.strptime(data["complete_time"], '%Y-%m-%dT%H:%M:%S.%fZ')
    except ValueError as error:
        print(error)
        return HttpResponse(status=400)
    except ObjectDoesNotExist as error:
        print(error)
        return HttpResponse(status=400)
    except KeyError as error:
        print(error)
        return HttpResponse(status=400)
    # add complete order
    try:
        complete_order(courier_id, order_id, complete_time)
    except ValidationError as error:
        print(error)
        return HttpResponse(status=400)
    except ObjectDoesNotExist as error:
        print(error)
        return HttpResponse(status=400)
    except KeyError as error:
        print(error)
        return HttpResponse(status=400)
    else:
        data_response = {"order_id": order_id}
        return JsonResponse(data_response, status=200)


