import sys
from .instances import InstanceFactory
from Environmentals.env_condition_cache_manager import EnvironmentConditionCacheManager
from Environmentals.env_condition_cache_manager import EnvironmentConditionCache 
from .fusionfpdutility import fpdutility

class DeviceIDExtractor():

    def __init__(self):
        self.sv = InstanceFactory.getInstance().get_python_sv_instance()
        self.cache_manager = EnvironmentConditionCacheManager()
        self.device_id = 0x0
        pass

    def extract_device_id(self):
        print("Extracting device id for the part.")
        if self.device_id == 0x0:
            self.sv.gfxcards.tiles.fuses.load_fuse_ram()
            self.device_id =  hex(self.sv.gfxcard0.tile0.fuses.sgunit_pciess_c0_r2.sg_device_id.get_value())
            print("current recorded device id is {}".format(self.device_id))
        return '0'+str(self.device_id)[2:]
    
    def cache_device_id(self):
        try:
            device_id = self.extract_device_id()
            cache = self.cache_manager.read_environment_condition_cache()
            cache.DEVICEID = device_id
            self.cache_manager.update_environment_condition_cache(cache)
            return device_id
        except Exception as ex:
            print("Failed to cache device id:- {}".format(ex))
