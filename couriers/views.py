import json
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt

from couriers.models import Region
from couriers.query import set_id, set_interval, set_regions


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
    have_not_valid_data = 0

    # fill in db
    for worker in list_couriers:
        try:
            courier = set_id(worker)
            all_regions = set_regions(worker, courier)
            all_interval = set_interval(worker, courier)
        except ValueError as error:
            have_not_valid_data = 1
            print(error)
            bad_id.append({'id': worker['courier_id']})
        except IntegrityError as error:
            have_not_valid_data = 1
            print(error)
            bad_id.append({'id': worker['courier_id']})
        except ValidationError as error:
            have_not_valid_data = 1
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
                have_not_valid_data = 1
                bad_id.append({'id': worker['courier_id']})

    # save data if all complete with succeed
    if have_not_valid_data == 0:
        for person in valid_data["valid"]:
            person["courier_id"].save()
            for reg in person["regions"]:
                try:
                    reg.save()
                except:
                    print("\nreg already exists")
                    reg = Region.objects.get(place=reg.place)
                    print("\nreg update")
                finally:
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


@csrf_exempt
def edit_courier(request, courier_id):
    """ меняет информацию о курьере с переданным id"""
    if request.method == "PATCH":

        # read json
        new_feature = json.loads(request.body)

        # edit info in db
        try:
            # ...some code...
            data_response = new_feature

            # ...some code...

            return HttpResponse(json.dumps(data_response), status=200)

        except IOError:
            return HttpResponse(status=400)

