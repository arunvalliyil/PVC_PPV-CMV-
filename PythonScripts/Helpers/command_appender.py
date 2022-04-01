from Environmentals.env_condition_cache_manager import EnvironmentConditionCacheManager
from Environmentals.env_condition_cache_manager import EnvironmentConditionCache 
from PVCInfo.device_manager import DeviceManager

class CommandAppender():

    def __init__(self):
        self.cache_manager = EnvironmentConditionCacheManager()
        self.device_manager = DeviceManager()
        pass
    
    def append_device_id(self):
        cache = self.cache_manager.read_environment_condition_cache()
        return_val = ''
        try:
            if not cache.DEVICEID:
                return_val =  "-did {}".format(self.device_manager.cache_device_id())
            elif cache.DEVICEID:
                return_val =  "-did {}".format(cache.DEVICEID)
        except Exception as ex:
            print("Failed to calculate Command Appender string {}".format(ex))
        return return_val

        

