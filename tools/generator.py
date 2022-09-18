from datetime import datetime, timedelta

from generator import InstanceBuilder


InstanceBuilder("test_partial", datetime(2020, 10, 11, 12, 20, 30), timedelta(hours=3)) \
    .generate_constants(1000) \
    .generate_ars_and_dtos(500, 10, 5, 30, 70) \
    .generate_paws(20) \
    .get_instance() \
    .save()


InstanceBuilder("test_complete", datetime(2020, 10, 11, 12, 20, 30), timedelta(hours=3)) \
    .generate_constants(50, 0.6) \
    .generate_ars_and_dtos(500, 10, 5, 30, 70) \
    .generate_paws(20) \
    .generate_dlos(20) \
    .get_instance() \
    .save()

InstanceBuilder("test_large_partial", datetime(2020, 10, 11, 12, 20, 30), timedelta(hours=3)) \
    .generate_constants(2000) \
    .generate_ars_and_dtos(1000, 10, 5, 30, 70) \
    .generate_paws(50) \
    .get_instance() \
    .save()

InstanceBuilder("test_large_complete", datetime(2020, 10, 11, 12, 20, 30), timedelta(hours=3)) \
    .generate_constants(100, 0.6) \
    .generate_ars_and_dtos(1000, 10, 5, 30, 70) \
    .generate_paws(20) \
    .generate_dlos(50) \
    .get_instance() \
    .save()
