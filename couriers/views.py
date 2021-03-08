import json
from django.http import HttpResponse
from django.views.decorators.http import require_POST, require_GET
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
@require_POST
def post_couriers(request):
    """
        из тела запроса вытащить json, заполнить бд
        и вернуть json
    """
    # read json
    list_couriers = json.loads(request.body)["data"]

    # prepare list for response
    bad_id = []
    pretty_id = []

    # fill in db
    for worker in list_couriers:
        try:
            # ...some code...
            pretty_id.append({'id': worker['courier_id']})
            pass
        except IOError:
            pass

    # ...some code...

    # create response
    if not bad_id:
        response = {"couriers": pretty_id}
    else:
        response = {"couriers": bad_id}

    return HttpResponse(json.dumps(response), status=201)


def edit_courier(request, id):
    # меняет информацию о курьере с переданным id
    if request.method == "GET":
        return HttpResponse(id, status=200)
