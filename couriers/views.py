import datetime
import json
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.db import IntegrityError
from django.http import HttpResponse, JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from couriers.models import Region, Courier, Working_hours
from couriers.query import set_id, set_interval, set_regions
from orders.models import Order_to_Courier, Delivery_time


@csrf_exempt
@require_POST
def post_couriers(request):
    # read json
    list_couriers = json.loads(request.body)["data"]

    # prepare list for response
    bad_id = []
    pretty_id = []
    valid_data = {"valid": []}

    # flags
    have_not_valid_data = 1

    # fill in db
    for worker in list_couriers:
        try:
            courier = set_id(worker)
            all_regions = set_regions(worker)
            all_interval = set_interval(worker, courier)
        except ValueError as error:
            have_not_valid_data = 0
            print(error)
            bad_id.append({'id': worker['courier_id']})
        except IntegrityError as error:
            have_not_valid_data = 0
            print(error)
            bad_id.append({'id': worker['courier_id']})
        except ValidationError as error:
            have_not_valid_data = 0
            print(error)
            bad_id.append({'id': worker['courier_id']})
        else:
            if all_interval != [] and all_regions != [] and courier:
                valid_data["valid"].append({"courier_id": courier,
                                            "regions": all_regions,
                                            "working_hours": all_interval
                                            })
                pretty_id.append({'id': worker['courier_id']})
            else:
                have_not_valid_data = 0
                bad_id.append({'id': worker['courier_id']})

    # save data if all complete with succeed
    if have_not_valid_data == 1:
        for person in valid_data["valid"]:
            person["courier_id"].save()
            for reg in person["regions"]:
                reg.save()
                person["courier_id"].regions.add(reg)
            for interval in person["working_hours"]:
                interval.save()

    # create response
    if not bad_id:
        data_response = {"couriers": pretty_id}
        status_response = 201
    else:
        data_response = {"validation_error": {"couriers": bad_id}}
        status_response = 400

    return JsonResponse(data_response, status=status_response)


@method_decorator(csrf_exempt, name='dispatch')
class CourierUpdateView(View):

    def patch(self, request, courier_id):
        # read request
        data = json.loads(request.body)

        # validation
        try:
            Courier.objects.get(courier_id=courier_id)
        except ObjectDoesNotExist as error:
            print(error)
            return HttpResponse(status=400)

        # find regions
        courier_regions = []
        for i in Region.objects.filter(couriers__courier_id=courier_id):
            courier_regions.append(i.place)

        # flags
        not_valid = 1

        # UPDATE
        if data.get("courier_type"):
            # CHANGE TYPE
            not_valid = 0
            Courier.objects.filter(courier_id=courier_id).update(courier_type=data.get("courier_type"))
            try:
                Courier.objects.get(courier_id=courier_id).full_clean()
            except ValidationError as error:
                print(error)
                return HttpResponse(status=400)
        if data.get("regions"):
            # CHANGE REGION
            not_valid = 0
            new_regs = []
            courier = Courier.objects.get(courier_id=courier_id)
            for reg in courier.regions.all():
                courier.regions.remove(reg)
            for new_reg in data.get("regions"):
                try:
                    elem = Region.objects.get(place=new_reg)
                    new_regs.append(elem)
                except ObjectDoesNotExist:
                    elem = Region()
                    elem.place = new_reg
                    new_regs.append(elem)
                    try:
                        elem.full_clean()
                    except ValidationError as error:
                        print(error)
                        return HttpResponse(status=400)
            for new_reg in new_regs:
                new_reg.save()
                courier.regions.add(new_reg)
            # EDIT ORDER_TO_WORKER
            for i in Order_to_Courier.objects.filter(courier=courier):
                if i.order.region not in courier_regions:
                    i.delete()
        if data.get("working_hours"):
            valid_time = []
            not_valid = 0
            # CHANGE
            new_time = data.get("working_hours")
            courier = Courier.objects.get(courier_id=courier_id)
            for time in Working_hours.objects.filter(courier=courier).all():
                time.delete()
            for elem in new_time:
                try:
                    left, right = elem.split('-')
                    left = datetime.datetime.strptime(left, '%H:%M')
                    right = datetime.datetime.strptime(right, '%H:%M')
                    time_temp = Working_hours()
                    time_temp.begin = left
                    time_temp.end = right
                    time_temp.courier = courier
                    valid_time.append(time_temp)
                except TypeError as error:
                    print(error)
                    return HttpResponse(status=400)
                except ValueError as error:
                    print(error)
                    return HttpResponse(status=400)
                except AttributeError as error:
                    print(error)
                    return HttpResponse(status=400)
            for vt in valid_time:
                vt.save()
            # EDIT ORDER TO WORKER
            courier = Courier.objects.get(courier_id=courier_id)
            for i in Order_to_Courier.objects.filter(courier=courier):
                for ctime in Working_hours.objects.filter(courier=courier).all():
                    for t in Delivery_time.objects.filter(order=i.order).all():
                        if ctime.end < t.begin or ctime.begin > t.end:
                            i.delete()
        if not_valid:
            return HttpResponse(status=400)

        # prepare response
        courier = Courier.objects.get(courier_id=courier_id)
        courier_regions = []
        courier_time = []
        for time in Working_hours.objects.filter(courier=courier).all():
            courier_time.append("{}-{}".format(time.begin, time.end))
        for i in Region.objects.filter(couriers__courier_id=courier_id):
            courier_regions.append(i.place)
        response_data = {
            "courier_id": courier.courier_id,
            "courier_type": courier.courier_type,
            "regions": courier_regions,
            "working_hours": courier_time
        }
        return JsonResponse(response_data)
