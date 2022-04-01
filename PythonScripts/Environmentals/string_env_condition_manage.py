from .env_condition_cache_manager import EnvironmentConditionCacheManager
from Helpers.instances import InstanceFactory
from PVCInfo.device_manager import DeviceManager
from Environmentals.vmin_voltage_setter import VminSetter

class StringEnvironmentCondition():
    
    def __init__(self):
        self.cache_manager = EnvironmentConditionCacheManager()
        self.device_manager = DeviceManager.getInstance()
        self.api = InstanceFactory.getInstance().get_fusion_instance()
        self.vmin_setter = VminSetter()
        return
    
    def get_supported_conditions(self):
        return ['TILESTOAPPLY','LOADDRIVER', 'TARGETOS'] # if any more string board condition needs to be handled add it here first
    
    def set_condition(self, name, value):
        name = name.upper()
        if self.is_condition_supported(name):
            print("Setting condition {} to value {}".format(name, value))
            if name in "TILESTOAPPLY":
                if self.validate_set_value(name, value):
                    cached_data = self.cache_manager.read_environment_condition_cache()
                    setattr(cached_data,name.upper(),value)
                    self.cache_manager.update_environment_condition_cache(cached_data)
                    return True
                else:
                    raise Exception("Condition:- {} Value:- {} is not a valid one for current unit".format(name, value))
            elif name in "LOADDRIVER":
                return self.load_driver(value)
            elif name in "TARGETOS":
                return self.cache_target_os(value)
            elif name in "SETVMIN_OS" or name in 'SETVMIN_EFI':
                self.vmin_setter.set_vmin()
                return True

    def cache_target_os(self,value):
        print("Caching target os to {}".format(value))
        cached_data = self.cache_manager.read_environment_condition_cache()
        setattr(cached_data,"TARGETOS",value)
        self.cache_manager.update_environment_condition_cache(cached_data)
        return True

    def load_driver(self,value):
        driver_load_status = ''
        driver_to_load = value
        print("Driver load set to {}".format(value))
        if value == "Auto":
            if self.device_manager.populated_tile_count() == 2:
                driver_to_load = '2T'
        self.api.marionette.set_ethernet_rcf()
        
        print("collecting soc and GT logs after booting to Ubuntu")
        DeviceManager.getInstance().collect_soc_logs()
        
        if driver_to_load == '1T':
            print("Loading 1T driver for the part")
            driver_load_status = self.api.marionette.execute_command('ocelot --flow /home/gfx-test/ppv/OS-Content/REL2021WW09/DRIVER_CHECK/1.1/DRIVER_CHECK/flows/load_driver_tile1.xml')
        else:
            print("Loading 2T driver for the part")
            driver_load_status = self.api.marionette.execute_command('ocelot --flow /home/gfx-test/ppv/OS-Content/REL2021WW09/DRIVER_CHECK/1.1/DRIVER_CHECK/flows/load_driver_tile2.xml')
                   
        print("Driver load Status:-  {}".format(driver_load_status))
        if 'ocelot main: result=success' in driver_load_status.lower():
            return True
        raise RuntimeError("Failed to load driver. {}".format(driver_to_load))

    def read_condition(self, name):
        if name.upper() in ['SETVMIN_OS','SETVMIN_EFI']:
            return True
        if self.is_condition_supported(name):
            cached_data = self.cache_manager.read_environment_condition_cache()
            return getattr(cached_data,name.upper())
        return False
    
    def validate_set_value(self, name, value):
        if name in 'TILESTOAPPLY':
            current_tile_count = self.device_manager.populated_tile_count()
            if current_tile_count == 1 and "2" in value:
                print("Condition:- {} Value:- {} is not a valid one for {} Tile unit".format(name, value, current_tile_count))
                return False
        elif name in 'LoadDriver':
            current_os = self.api.marionette.get_connected_os()
            if current_os == 'LINUX':
                return True
            else:
                return False
        return True

    def is_condition_supported(self, condition_name):
        if condition_name.upper() not in self.get_supported_conditions():
            raise Exception("Condition {} is not supported in python".format(condition_name))
        else:
            return True