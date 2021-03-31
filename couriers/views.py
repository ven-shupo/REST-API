import datetime
import json
import statistics

import django
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.core.serializers import serialize
from django.core.serializers.json import DjangoJSONEncoder
from django.db import IntegrityError
from django.http import HttpResponse, JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from couriers.models import Region, Courier, Working_hours
from couriers.query import set_id, set_interval, set_regions
from orders.models import Order_to_Courier, Delivery_time, Complete_Order
from orders.query import compare_delivery_working_time


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

    for worker in list_couriers:
        for key in worker:
            if key not in ["courier_id", "courier_type", "regions", "working_hours"]:
                bad_id.append({'id': worker['courier_id']})
    if bad_id:
        data_response = {"validation_error": {"couriers": bad_id}}
        status_response = 400
        return JsonResponse(data_response, status=status_response)

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
        except KeyError as error:
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
                try:
                    reg.save()
                    person["courier_id"].regions.add(reg)
                except IntegrityError:
                    exist_reg = Region.objects.get(place=reg.place)
                    person["courier_id"].regions.add(exist_reg)
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


def get_weight(courier):
    courier_type = courier.courier_type
    if courier_type == "foot":
        return 10
    if courier_type == "bike":
        return 15
    if courier_type == "car":
        return 50


def min_avg_del_time(courier_id):
    courier = Courier.objects.get(courier_id=courier_id)
    regions = [order.region for order in Complete_Order.objects.filter(courier=courier).all()]
    avg_time_for_each_regions = []
    for reg in list(set(regions)):
        time = []
        complete_orders = Complete_Order.objects.filter(courier=courier, region=reg).order_by('time_complete')
        begin_year, begin_month, begin_day = int(complete_orders[0].time_assign.strftime("%Y")),\
                                             int(complete_orders[0].time_assign.strftime("%m")),\
                                             int(complete_orders[0].time_assign.strftime("%d"))
        end_year, end_month, end_day = int(complete_orders[0].time_complete.strftime("%Y")),\
                                       int(complete_orders[0].time_complete.strftime("%m")),\
                                       int(complete_orders[0].time_complete.strftime("%d"))
        day_delta = (end_year-begin_year)*366*24*60 + (end_month-begin_month)*30*24*60 + (end_day-begin_day)*24*60

        begin_hours, begin_minutes = int(complete_orders[0].time_assign.strftime("%H")), \
                                     int(complete_orders[0].time_assign.strftime("%M"))
        end_hours, end_minutes = int(complete_orders[0].time_complete.strftime("%H")), \
                                 int(complete_orders[0].time_complete.strftime("%M"))
        time.append((end_hours - begin_hours) * 60 + (end_minutes - begin_minutes) + day_delta)

        for i in range(1, len(complete_orders)):
            begin_year, begin_month, begin_day = int(complete_orders[i-1].time_complete.strftime("%Y")), \
                                                 int(complete_orders[i-1].time_complete.strftime("%m")), \
                                                 int(complete_orders[i-1].time_complete.strftime("%d"))
            end_year, end_month, end_day = int(complete_orders[i].time_complete.strftime("%Y")), \
                                           int(complete_orders[i].time_complete.strftime("%m")), \
                                           int(complete_orders[i].time_complete.strftime("%d"))
            day_delta = (end_year - begin_year) * 366 * 24 * 60 + (end_month - begin_month) * 30 * 24 * 60 + (
                        end_day - begin_day) * 24 * 60

            begin_hours, begin_minutes = int(complete_orders[i-1].time_complete.strftime("%H")), \
                                         int(complete_orders[i-1].time_complete.strftime("%M"))
            end_hours, end_minutes = int(complete_orders[i].time_complete.strftime("%H")), \
                                     int(complete_orders[i].time_complete.strftime("%M"))
            time.append((end_hours - begin_hours) * 60 + (end_minutes - begin_minutes) + day_delta)

        avg_time_for_each_regions.append(statistics.mean(time))

    for complete_order in Complete_Order.objects.filter(courier=courier):
        for assign_order in Order_to_Courier.objects.filter(courier=courier):
            if complete_order.time_assign == assign_order.time_order:
                raise AssertionError

    if not avg_time_for_each_regions:
        raise AssertionError

    return min(avg_time_for_each_regions)


def count_rating(courier_id):
    return (60 * 60 - min(min_avg_del_time(courier_id), 60 * 60)) * 5 / (60 * 60)


def get_C(courier_id):
    courier_type = Courier.objects.get(courier_id=courier_id).courier_type
    if courier_type == "foot":
        return 2
    if courier_type == "bike":
        return 5
    if courier_type == "car":
        return 9


def count_earnings(courier_id):
    complete_orders = Complete_Order.objects.filter(courier__courier_id=courier_id)
    return len(complete_orders) * complete_orders[0].c


@method_decorator(csrf_exempt, name='dispatch')
class CourierGetUpdateView(View):

    def get(self, request, courier_id):
        try:
            courier = Courier.objects.get(courier_id=courier_id)
            courier_regions = [region.place for region in courier.regions.all()]
            courier_time = ["{}-{}".format(time.begin.strftime("%H:%M"), time.end.strftime("%H:%M")) for time
                            in Working_hours.objects.filter(courier=courier).all()]
        except ObjectDoesNotExist as error:
            print(error)
            return HttpResponse(status=400)

        try:
            rating = count_rating(courier_id)
            earnings = count_earnings(courier_id)
        except ObjectDoesNotExist as error:
            print(error)
            return HttpResponse(status=400)
        except AssertionError:
            try:
                earnings = count_earnings(courier_id)
            except IndexError:
                earnings = 0
            response_data = {
                "courier_id": courier_id,
                "courier_type": courier.courier_type,
                "regions": courier_regions,
                "working_hours": courier_time,
                "earnings": earnings
            }
            return JsonResponse(response_data)

        # prepare response
        response_data = {
            "courier_id": courier_id,
            "courier_type": courier.courier_type,
            "regions": courier_regions,
            "working_hours": courier_time,
            "rating": float("%.2f" % rating),
            "earnings": earnings
        }
        return JsonResponse(response_data)

    def patch(self, request, courier_id):
        # read request
        data = json.loads(request.body)

        for key in data:
            if key not in ["courier_type", "regions", "working_hours"]:
                return HttpResponse(status=400)

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
            # EDIT ORDER TO COURIER
            temp_courier = Courier.objects.get(courier_id=courier_id)
            while temp_courier.currently_weight > get_weight(temp_courier):
                temp_courier.currently_weight -= \
                    Order_to_Courier.objects.filter(courier__courier_id=courier_id)[0].order.weight
                Order_to_Courier.objects.filter(courier__courier_id=courier_id)[0].delete()
                temp_courier.save()

        if data.get("regions"):
            # validation
            if not isinstance(data.get("regions"), list):
                print("regions is not valid")
                return HttpResponse(status=400)
            for item in data.get("regions"):
                if not isinstance(item, int):
                    return HttpResponse(status=400)

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
            for i in Order_to_Courier.objects.filter(courier__courier_id=courier_id):
                if i.order.region not in data.get("regions"):
                    i.delete()
        if data.get("working_hours"):
            # validation
            if not isinstance(data.get("working_hours"), list):
                return HttpResponse(status=400)
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
                        if not compare_delivery_working_time(ctime, t):
                            i.delete()
        if not_valid:
            return HttpResponse(status=400)

        # prepare response
        courier = Courier.objects.get(courier_id=courier_id)
        courier_regions = []
        courier_time = []
        for time in Working_hours.objects.filter(courier=courier).all():
            courier_time.append("{}-{}".format(time.begin.strftime("%H:%M"), time.end.strftime("%H:%M")))
        for i in Region.objects.filter(couriers__courier_id=courier_id):
            courier_regions.append(i.place)
        response_data = {
            "courier_id": courier.courier_id,
            "courier_type": courier.courier_type,
            "regions": courier_regions,
            "working_hours": courier_time
        }
        return JsonResponse(response_data)
