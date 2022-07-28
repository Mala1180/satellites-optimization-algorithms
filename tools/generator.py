from generator import InstanceBuilder


InstanceBuilder("test").generate_constants(100, 0.070) \
    .generate_dtos(300, 20, 0.3, 50) \
    .generate_paws(10) \
    .generate_dlos(10) \
    .save_instance()

print("Instance generated")
