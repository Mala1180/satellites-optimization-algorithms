from generator import InstanceBuilder


InstanceBuilder("test").generate_constants(100, 0.070) \
    .generate_ars_and_dtos(50, 10, 30, 50, 70) \
    .generate_paws(10) \
    .generate_dlos(10) \
    .save_instance()

print("Instance generated")
