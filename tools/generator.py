from datetime import datetime, timedelta

from generator import InstanceBuilder


instance = InstanceBuilder("test_large", datetime(2020, 10, 11, 12, 20, 30), timedelta(hours=3)) \
    .generate_constants(100, 0.9) \
    .generate_ars_and_dtos(100, 50, 10, 50, 70) \
    .generate_paws(20) \
    .generate_dlos(50) \
    .get_instance()

instance.save()
