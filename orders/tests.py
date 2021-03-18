import json

from django.test import TestCase

from orders.models import Complete_Order, Order_to_Courier


class OrderTestCase(TestCase):

    def test_post_201(self):
        data = {
            "data": [
                {
                    "order_id": 1,
                    "weight": 0.23,
                    "region": 12,
                    "delivery_hours": ["09:00-18:00"]
                },
                {
                    "order_id": 2,
                    "weight": 15,
                    "region": 1,
                    "delivery_hours": ["09:00-18:00"]
                },
                {
                    "order_id": 3,
                    "weight": 0.01,
                    "region": 22,
                    "delivery_hours": ["09:00-12:00", "16:00-21:30"]
                }
            ]
        }
        response = self.client.generic('POST', '/orders', json.dumps(data), host='localhost:8080')
        self.assertEqual(response.status_code, 201)

    def test_post_400(self):
        data = {
            "data": [
                {
                    "order_id": -1,
                    "weight": ["sadasd"],
                    "region": None,
                    "delivery_hours": ["09:00-18:00"]
                },
                {
                    "order_id": 2,
                    "weight": ["sadasd"],
                    "region": 1,
                    "delivery_hours": ["09:0018:00"]
                },
                {
                    "order_id": 3,
                    "weight": 0.01,
                    "region": None,
                    "delivery_hours": ["09:00-12:00", "16:00-21:30"]
                }
            ]
        }
        response = self.client.generic('POST', '/orders', json.dumps(data), host='localhost:8080')
        self.assertEqual(response.status_code, 400)

    def test_complete(self):
        data_couriers = {
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
        response_post = self.client.generic('POST', '/couriers', json.dumps(data_couriers), host='localhost:8080')
        data_orders = {
            "data": [
                {
                    "order_id": 1,
                    "weight": 1,
                    "region": 1,
                    "delivery_hours": ["09:00-11:00"]
                },
                {
                    "order_id": 2,
                    "weight": 1,
                    "region": 12,
                    "delivery_hours": ["08:59-11:01"]
                },
                {
                    "order_id": 3,
                    "weight": 4,
                    "region": 12,
                    "delivery_hours": ["10:30-12:00"]
                },
                {
                    "order_id": 4,
                    "weight": 11,
                    "region": 1,
                    "delivery_hours": ["6:30-21:00"]
                }
            ]
        }
        response_post = self.client.generic('POST', '/orders', json.dumps(data_orders), host='localhost:8080')
        data_for_assign = {
            "courier_id": 1
        }
        response_assign = self.client.generic('POST', '/orders/assign', json.dumps(data_for_assign),
                                              host='localhost:8080')
        data_for_complete = {
            "courier_id": 134124534,
            "order_id": 33,
            "complete_time": "2021-0110T10:33:01.42Z"
        }
        response_complete = self.client.generic('POST', '/orders/complete', json.dumps(data_for_complete),
                                                host='localhost:8080')
        self.assertEqual(response_complete.status_code, 400)

        data_for_complete = {
            "courier_id": 1,
            "order_id": 33,
            "complete_time": "2021-01-10T10:33:01.42Z"
        }
        response_complete = self.client.generic('POST', '/orders/complete', json.dumps(data_for_complete),
                                                host='localhost:8080')
        self.assertEqual(response_complete.status_code, 400)

        data_for_complete = {
            "courier_id": 1,
            "order_id": 1,
            "complete_time": "2021-01-10T10:33:01.42Z"
        }
        response_complete = self.client.generic('POST', '/orders/complete', json.dumps(data_for_complete),
                                                host='localhost:8080')
        self.assertEqual(response_complete.status_code, 200)

        if len(Complete_Order.objects.all()) != 1:
            raise AssertionError("problem with complete")
        if Order_to_Courier.objects.filter(order__order_id=1):
            raise AssertionError("problem with complete")