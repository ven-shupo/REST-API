import datetime
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from couriers.models import Courier, Region, Working_hours


def set_id(people):
    # create courier, his id and type
    worker = Courier()
    worker.courier_id = people["courier_id"]
    worker.courier_type = people['courier_type']
    worker.currently_weight = 0
    # validation
    worker.full_clean()
    return worker


def set_interval(people, courier):

    # validation
    if not isinstance(people['working_hours'], list):
        raise ValidationError(message='%s must be list' % people['working_hours'])
    for elem in people['working_hours']:
        if not isinstance(elem, str):
            raise ValidationError(message='%s elem in list must be str' % people['working_hours'])

    # prepare ans
    all_interval = []
    # create interval
    for interval in people['working_hours']:
        # create begin and end point
        if len(interval.split('-')) != 2:
            raise ValidationError(message="working hours not valid")
        left, right = interval.split('-')
        left = datetime.datetime.strptime(left, '%H:%M')
        right = datetime.datetime.strptime(right, '%H:%M')
        time = Working_hours()
        time.begin = left
        time.end = right
        all_interval.append(time)
        time.courier = courier

    return all_interval


def set_regions(people):

    # validation
    if not isinstance(people['regions'], list):
        raise ValidationError(message='%s must be list' % people['regions'])
    for elem in people['regions']:
        if not isinstance(elem, int):
            raise ValidationError(message='%s elem in list must be integer' % people['regions'])

    # prepare ans
    all_regions = []
    # create or get regions
    for reg in people['regions']:
        try:
            temp_place = Region.objects.get(place=reg)
        except ObjectDoesNotExist:
            temp_place = Region()
            temp_place.place = reg
            temp_place.full_clean()
        finally:
            all_regions.append(temp_place)
    return all_regions
