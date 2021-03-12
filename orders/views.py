import json
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from orders.query import set_id, set_interval


@csrf_exempt
@require_POST
def post_orders(request):
    # read json
    list_order = json.loads(request.body)["data"]
    # prepare list for response
    bad_id = []
    pretty_id = []
    valid_data = {"valid": []}

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

    return HttpResponse(json.dumps(data_response), status=status_response)