# :package: REST-API "Сласти от всех напастей" :credit_card: 
## Что это?
Это REST-API сервис, который позволяет нанимать курьеров на работу,
принимать заказы и оптимально распределять заказы между курьерами, попутно считая их рейтинг и заработок.
Сервис реализован в рамках отбора в летнюю школу Яндекса.
## Что умеет?
Приложение умеет обрабатывать три вида запросов: GET, POST и PATCH
### GET
- Возвращает информацию о курьере и дополнительную статистику: рейтинг и заработок.
```python
GET /couriers/2
    {
    "courier_id": 2,
    "courier_type": "foot",
    "regions": [11, 33, 2],
    "working_hours": ["09:00-18:00"],
    "rating": 4.93,
    "earnings": 10000
    }
```
### POST
- Загружает в систему информацию о курьерах
```python
POST /couriers
  {
  "data": [
      {
      "courier_id": 1,
      "courier_type": "foot",
      "regions": [1, 12, 22],
      "working_hours": ["11:35-14:05", "09:00-11:00"]
      },
      {
      "courier_id": 2,
      "courier_type": "bike",
      "regions": [22],
      "working_hours": ["09:00-18:00"]
      },
      {
      "courier_id": 3,
      "courier_type": "car",
      "regions": [12, 22, 23, 33],
      "working_hours": []
      },
  ...
  ]
  }
```
- Загружает в систему информацию о заказах
```python
POST /orders
  {
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
      },
  ...
  ]
  }
```
- Принимает id курьера и назначает максимальное количество заказов, подходящих по весу, району и графику работы.
```python
POST /orders/assign
  {
  "courier_id": 2
  }
```
- Принимает 3 параметра: id курьера, id заказа и время выполнения заказа, отмечает заказ выполненным.
```python
POST /orders/complete
  {
  "courier_id": 2,
  "order_id": 33,
  "complete_time": "2021-01-10T10:33:01.42Z"
  }
```
### PATCH
- Позволяет изменять информацию о курьере.
```python
PATCH /couriers/2
  {
  "regions": [11, 33, 2]
  }
```
## :electric_plug: Как запустить? :computer:
1) скачать проект: git clone https://github.com/ven-shupo/REST-API
2) установить зависимости: pip install -r requirements.txt
3) создать и применить миграции: python manage.py makemigrations, python manage.py migrate
4) создать суперюзера для администрирования сервиса: python manage.py createsuperuser
5) запустить сервис: python manage.py runserver

