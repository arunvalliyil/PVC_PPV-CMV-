
from .instances import InstanceFactory



class AMCReader():

    def __init__(self):
        print("Initiating AMC Reader")
        self.instances = InstanceFactory.getInstance()
        self.api = self.instances.get_fusion_instance()

    def read_rvp_tile_info(self):
        serial_port = 8
        api.serial_port.configure_then_listen_on_serial_port(serial_port,'BR_115200','DB_8','NO_PARITY','ONE','NONE')
        api.serial_port.flush_buffer(serial_port)
        read_value = api.serial_port.read_all_data(serial_port)


