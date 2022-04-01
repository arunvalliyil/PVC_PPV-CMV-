
import sys,os,json
if r'C:\PythonSV\pontevecchio\fivr\scripts' not in sys.path: sys.path.append(r'C:\PythonSV\pontevecchio\fivr\scripts')
import BasicTools as bt
from .decimal_env_condition_manager import DecimalEnvironmentCondition
from .env_condition_cache_manager import EnvironmentConditionCacheManager
from .env_condition_cache_manager import EnvironmentConditionCache

from Helpers.Configuration import Configuration
from PVCInfo.device_manager import DeviceManager
from PVCInfo.voltage_manager import VoltageManager

class VoltageConditionManager(DecimalEnvironmentCondition):
    
    def __init__(self):
        self.device_manager = DeviceManager.getInstance()
        self.config = Configuration.getInstance()
        self.tile_count = 0
        self.cache_manager = EnvironmentConditionCacheManager()
        
    def get_supported_conditions(self):
        return VoltageManager().supported_conditions
    
    def execute_set_condition(self, condition_name, voltage):
        print("Setting Voltage for rail {} to {}".format(condition_name, voltage))
        cached_data = EnvironmentConditionCache()
        cached_data.VOLTAGE_OVERRIDE = {condition_name: voltage}
        self.cache_manager.update_environment_condition_cache(cached_data)
        self.device_manager.set_device_condition(condition_name, voltage)

            
    def execute_read_condition(self, condition_name):
        print("Reading voltage {} ".format(condition_name))
        retry_count = 3
        return_val = None
        cached_data = round(float(self.cache_manager.read_environment_condition_cache().VOLTAGE_OVERRIDE[condition_name]),3)

        while retry_count >0:
            retry_count = retry_count - 1
            read_value = self.device_manager.read_device_condition(condition_name)
            print("{} set to {} and read value is {}".format(condition_name,cached_data,read_value))
            tolerance = .005
            expected_upper_limit = cached_data +.005
            expected_lower_limit = cached_data -.005
            if read_value == cached_data:
                return read_value
            print("Checking if read value is within tolerange range {} - {}".format(expected_lower_limit,expected_upper_limit))
            if expected_lower_limit <= read_value <= expected_upper_limit:
                return read_value
            else:
                return_val = self.reapply_condition_before_verification(condition_name,cached_data)
        return return_val
    
    def reapply_condition_before_verification(self, condition_name, cached_data):
        print("re-applying voltage value for {} to {}".format(condition_name, cached_data))
        self.execute_set_condition(condition_name, cached_data)
        read_value = self.device_manager.read_device_condition(condition_name)
        print("Condition reapplied to {} returning device read value {}".format(cached_data,read_value))
        return read_value

