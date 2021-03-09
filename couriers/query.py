from couriers.models import Worker, Region


def create(people):

    # create courier, his id and type
    try:
        worker = Worker.objects.create(courier_id=people["courier_id"],
                                       courier_type=people['courier_type'])
    except:
        print(people, "id or type is not valid")
        raise IOError

    # create all regions
    for reg in people['regions']:
        try:
            # save reg
            place = Region.objects.create(place=reg)
            place.save()
            # link with couriers
            worker.regions.add(place)
        except:
            pass

        # save worker
        worker.save()
    return people["courier_id"]









    # """fill in db with couriers"""
    # ...create...
    # try:
    #     worker = Worker.objects.create(courier_id=people["courier_id"],
    #                                    courier_type=people['courier_type'])
    #     region = Regions.objects.create(courier=worker)
    #     table = Table.objects.create(courier=worker)
    #     worker.save()
    #     region.save()
    #     table.save()
    # except:
    #     pass
    # one to many
    # table.add(*people["working_hours"])
    # many to many
    # region.region.add(*people['regions'])
    # ...save...
