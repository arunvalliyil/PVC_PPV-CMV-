
import sys
from Helpers.instances import InstanceFactory
from PVCInfo.device_manager import DeviceManager
from Environmentals.decimal_env_condition_manager import DecimalEnvironmentCondition
from Environmentals.env_condition_cache_manager import EnvironmentConditionCacheManager
from Environmentals.env_condition_cache_manager import EnvironmentConditionCache

class FrequencyConditionManager(DecimalEnvironmentCondition):
    
    def __init__(self):
        self.cache_manager = EnvironmentConditionCacheManager()
        self.device_manager = DeviceManager.getInstance()
    
    def get_supported_conditions(self):
        return ['media','compute','base','systolic','link', 'hbm']
    
    def execute_set_condition(self, condition_name, frequency):
        print("Setting frequency for domain {} to {}".format(condition_name, frequency))
        condition_to_set = {}
        condition_to_set[condition_name] = frequency
        cache = EnvironmentConditionCache()
        cache.SET_FREQUENCY = condition_to_set
        print("Updating environment condition cache to set {} with frequency {}".format(condition_name, frequency))
        self.cache_manager.update_environment_condition_cache(cache)
        
    def execute_read_condition(self, condition_name):
        return  self.device_manager.read_device_condition(condition_name)
        
    