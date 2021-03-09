import json
from django.http import HttpResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from couriers.query import create


@csrf_exempt
@require_POST
def post_couriers(request):
    # read json
    list_couriers = json.loads(request.body)["data"]

    # prepare list for response
    bad_id = []
    pretty_id = []

    # fill in db
    for worker in list_couriers:
        try:
            temp = create(worker)
            pretty_id.append({'id': temp})
        except IOError:
            bad_id.append({'id': worker['courier_id']})

    # create response
    if not bad_id:
        data_response = {"couriers": pretty_id}
        status_response = 201
    else:
        data_response = {"validation_error": {"couriers": bad_id}}
        status_response = 400

    return HttpResponse(json.dumps(data_response), status=status_response)


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




