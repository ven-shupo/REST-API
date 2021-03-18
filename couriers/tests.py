import json
from django.test import TestCase
from couriers.models import Courier
from orders.models import Order_to_Courier


class CourierTestCase(TestCase):

    def test_post_201(self):
        data = {
            "data": [
                {
                    "courier_id": 1,
                    "courier_type": "foot",
                    "regions": [
                        1,
                        12,
                        22
                    ],
                    "working_hours": [
                        "11:35-14:05",
                        "09:00-11:00"
                    ]
                }
            ]
        }
        response = self.client.generic('POST', '/couriers', json.dumps(data), host='localhost:8080')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(len(Courier.objects.filter(courier_id=1).all()), 1)

    def test_post_400(self):
        data = {
            "data": [
                {
                    "courier_id": 1,
                    "courier_type": "fot",
                    "regions": [
                        1,
                        -12,
                        22
                    ],
                    "working_hours": [
                        "11:3514:05",
                        "09:00-11:00"
                    ]
                }
            ]
        }
        response = self.client.generic('POST', '/couriers', json.dumps(data), host='localhost:8080')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(len(Courier.objects.filter(courier_id=1).all()), 0)

    def create_order(self):
        data_for_post = {
            "data": [
                {
                    "order_id": 1,
                    "weight": 5,
                    "region": 11,
                    "delivery_hours": ["09:00-11:00"]
                },
                {
                    "order_id": 2,
                    "weight": 5,
                    "region": 33,
                    "delivery_hours": ["08:59-11:01"]
                },
                {
                    "order_id": 3,
                    "weight": 4,
                    "region": 2,
                    "delivery_hours": ["10:30-12:00"]
                },
                {
                    "order_id": 4,
                    "weight": 11,
                    "region": 2,
                    "delivery_hours": ["6:30-21:00"]
                }
            ]
        }
        response_post = self.client.generic('POST', '/orders', json.dumps(data_for_post), host='localhost:8080')

    def assign_order(self):
        data_for_assign = {
            "courier_id": 1
        }
        response_assign = self.client.generic('POST', '/orders/assign', json.dumps(data_for_assign),
                                              host='localhost:8080')

    def test_patch(self):
        data_for_post = {
            "data": [
                {
                    "courier_id": 1,
                    "courier_type": "bike",
                    "regions": [
                        1,
                        12
                    ],
                    "working_hours": [
                        "09:00-11:00"
                    ]
                }
            ]
        }
        data_for_patch = {
            "regions": [11, 33, 2]
        }
        response_post = self.client.generic('POST', '/couriers', json.dumps(data_for_post), host='localhost:8080')
        self.create_order()
        self.assign_order()
        list_orders = [x.order for x in Order_to_Courier.objects.filter(courier_id=1).all()]
        if list_orders:
            raise AssertionError("problem with assign orders")
        response_patch = self.client.generic('PATCH', '/couriers/1', json.dumps(data_for_patch), host='localhost:8080')
        self.assertEqual(response_patch.status_code, 200)
        for region in [reg.place for reg in Courier.objects.get(courier_id=1).regions.all()]:
            if region not in [11, 33, 2]:
                raise AssertionError("problem with patch regions")
        self.assign_order()
        list_tasks = [x for x in Order_to_Courier.objects.filter(courier_id=1).all()]
        for task in list_tasks:
            if task.courier.currently_weight != 14:
                raise AssertionError("problem with currently weight")
        data_for_patch = {
            "regions": [2]
        }
        response_patch = self.client.generic('PATCH', '/couriers/1', json.dumps(data_for_patch), host='localhost:8080')
        list_orders = [x.order for x in Order_to_Courier.objects.filter(courier_id=1).all()]
        if len(list_orders) != 1:
            raise AssertionError("problem with assign orders (regions)")
        data_for_patch = {
            "working_hours": ["12:01-18:00"]
        }
        response_patch = self.client.generic('PATCH', '/couriers/1', json.dumps(data_for_patch), host='localhost:8080')
        list_orders = [x.order for x in Order_to_Courier.objects.filter(courier_id=1).all()]
        if len(list_orders) != 0:
            raise AssertionError("problem with assign orders (working_hours)")

        courier = Courier.objects.get(courier_id=1)
        courier.currently_weight=0
        courier.save()
        data_for_patch = {
            "regions": [2],
            "working_hours": ["5:01-22:00"],
            "courier_type": "bike"
        }
        response_patch = self.client.generic('PATCH', '/couriers/1', json.dumps(data_for_patch), host='localhost:8080')
        self.assign_order()
        list_orders = [x.order for x in Order_to_Courier.objects.filter(courier_id=1).all()]
        if len(list_orders) != 2:
            raise AssertionError("problem with assign orders")

        data_for_patch = {
            "working_hours": ["13:01-22:00"],
        }
        response_patch = self.client.generic('PATCH', '/couriers/1', json.dumps(data_for_patch), host='localhost:8080')
        list_orders = [x.order for x in Order_to_Courier.objects.filter(courier_id=1).all()]
        if len(list_orders) != 1:
            raise AssertionError("problem with assign orders")

        data_for_patch = {
            "courier_type": "foot",
        }
        response_patch = self.client.generic('PATCH', '/couriers/1', json.dumps(data_for_patch), host='localhost:8080')
        list_orders = [x.order for x in Order_to_Courier.objects.filter(courier_id=1).all()]
        if len(list_orders) != 0:
            raise AssertionError("problem with assign orders")

        data_for_patch = {
            "regions": ["1"],
        }
        response_patch = self.client.generic('PATCH', '/couriers/1', json.dumps(data_for_patch), host='localhost:8080')
        self.assertEqual(response_patch.status_code, 400)

        data_for_patch = {
            "courier_type": 123,
        }
        response_patch = self.client.generic('PATCH', '/couriers/1', json.dumps(data_for_patch), host='localhost:8080')
        self.assertEqual(response_patch.status_code, 400)

        data_for_patch = {
            "working_hours": 123,
        }
        response_patch = self.client.generic('PATCH', '/couriers/1', json.dumps(data_for_patch), host='localhost:8080')
        self.assertEqual(response_patch.status_code, 400)
