import json
from django.template import loader
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST, require_GET


@require_POST
def post_couriers(request):
    """
        из тела запроса вытащить json и заполнить бд
    """
    # read json begin
    data = json.loads(request.body)

    title = "HTTP 201 Created"

    # render and create response
    t = loader.get_template('Couriers_POST.html')
    context = {'title': title, 'list_created_id': data}
    return HttpResponse(t.render(context, request), status=200)


def edit_courier(request, id):
    # меняет информацию о курьере с переданным id
    if request.method == "GET":
        return HttpResponse(id, status=200)
