import datetime
import json

from django.http import JsonResponse, HttpResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from couriers.models import Worker, Region, Schedule
from orders.models import Order_to_Worker, Delivery_time


@method_decorator(csrf_exempt, name='dispatch')
class CourierUpdateView(View):

    def patch(self, request, courier_id):
        # read request
        data = json.loads(request.body)
        # get courier
        try:
            courier = Worker.objects.get(courier_id=courier_id)
        except:
            return HttpResponse(status=400)
        # find regions
        courier_regions = []
        for i in Region.objects.filter(couriers__courier_id=courier_id):
            courier_regions.append(i.place)
        #flags
        not_valid = 1

        # UPDATE
        if data.get("courier_type"):
            not_valid = 0
            Worker.objects.filter(courier_id=courier_id).update(courier_type=data.get("courier_type"))
            try:
                Worker.objects.get(courier_id=courier_id).full_clean()
            except:
                return HttpResponse(status=400)
        if data.get("regions"):
            # CHANGE REGION
            not_valid = 0
            new_regs = []
            courier = Worker.objects.get(courier_id=courier_id)
            for reg in courier.regions.all():
                courier.regions.remove(reg)
            for new_reg in data.get("regions"):
                try:
                    elem = Region.objects.get(place=new_reg)
                    new_regs.append(elem)
                except:
                    elem = Region()
                    elem.place = new_reg
                    new_regs.append(elem)
                    try:
                        elem.full_clean()
                    except:
                        return HttpResponse(status=400)
            for r in new_regs:
                r.save()
                courier.regions.add(r)
            # EDIT ORDER_TO_WORKER
            for i in Order_to_Worker.objects.filter(courier=courier):
                if i.order.region not in courier_regions:
                    i.delete()
        if data.get("working_hours"):
            valid_time = []
            not_valid = 0
            # CHANGE
            new_time = data.get("working_hours")
            courier = Worker.objects.get(courier_id=courier_id)
            for time in Schedule.objects.filter(courier=courier).all():
                time.delete()
            for time in new_time:
                try:
                    left, right = time.split('-')
                    left = datetime.datetime.strptime(left, '%H:%M')
                    right = datetime.datetime.strptime(right, '%H:%M')
                    time = Schedule()
                    time.begin = left
                    time.end = right
                    time.courier = courier
                    valid_time.append(time)
                except:
                    return HttpResponse(status=400)
                else:
                    for vt in valid_time:
                        vt.save()
            #EDIT ORDER TO WORKER
            for i in Order_to_Worker.objects.filter(courier=courier):
                for ctime in Schedule.objects.filter(courier=courier).all():
                    for t in Delivery_time.objects.filter(order=i.order).all():
                        if ctime.end < t.begin or ctime.begin > t.end:
                            i.delete()
        if not_valid:
            return HttpResponse(status=400)

        # prepare response
        courier = Worker.objects.get(courier_id=courier_id)
        courier_regions = []
        courier_time = []
        for time in Schedule.objects.filter(courier=courier).all():
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
