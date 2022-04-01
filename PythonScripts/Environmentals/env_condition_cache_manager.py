import os,sys,json,os.path
from collections import namedtuple
from Helpers.Configuration import Configuration

class EnvironmentConditionCacheManager():

    def __init__(self):
        self.config = Configuration.getInstance()
        self.cache_path = self.config.get_config_value('EnvironmentCondition','ENVIRONMENT_CONDITION_FLAG')
        if not os.path.isfile(self.cache_path):
            self.initiate_cache()
        pass

    def initiate_cache(self) :
        print("Initiating cache with default values")
        try:
            self.update_environment_condition_cache(EnvironmentConditionCache())
        except Exception as ex:
            print("Failed to initiate cache {}".format(ex))
        return "Passed"

    def read_environment_condition_cache(self):
        return_val = None
        if os.path.isfile(self.cache_path):
            with open(self.cache_path, 'r') as reader:
                return_val = json.loads(reader.read())
        else:
            return EnvironmentConditionCache()
        
        return EnvironmentConditionCache(return_val['VOLTAGE_OVERRIDE'],return_val['TILESTOAPPLY'],return_val['SET_FREQUENCY'] , return_val['DSS_OPTION'],return_val['TESTED_DSS'], return_val['REPORTED_DSS'], return_val['BYPASS_ENABLED'], return_val['TARGETOS'], return_val['TESTED_QDF'], return_val['BOOT_FREQUENCY'], return_val['TDIODE_TEMP'], return_val['MEML3'],return_val['DEVICEID'],return_val['FLAG_BIOS_FLASH'])
        

    def update_environment_condition_cache(self, cache_to_update):
        """
        updates environment condition cache.
        Parameters:
        EnvironmentConditionCache
        """
        if not isinstance(cache_to_update, EnvironmentConditionCache):
             raise Exception("Invalid parameter passed cache_to_update should be of type {}".format(type(EnvironmentConditionCache)))
        current_value = self.read_environment_condition_cache()
        for property in current_value.__dict__:
            if property in cache_to_update.__dict__:
                if cache_to_update.__dict__[property] is not None:
                    if isinstance(cache_to_update.__dict__[property],dict):         
                        current_value.__dict__[property].update(cache_to_update.__dict__[property])
                    else:
                        current_value.__dict__[property] = cache_to_update.__dict__[property]
            
        print("Updating cache value with {}".format(current_value.__dict__))
        with open(self.cache_path,'w', encoding="utf-8") as writer:
            json.dump(vars(current_value), writer)

class EnvironmentConditionCache():

    def __init__(self,voltage_override = {}, tiles = '', freq = {}, dss_option = {},test_dss= {}, reported_dss ={}, bypass = False,target_os = 'EFI',test_qdf = '',boot_frequency = '', tdiode_temp = '', meml3 = {},deviceid = '', bios_flash_flag = 'True'):
        self.VOLTAGE_OVERRIDE = voltage_override # a Dictionary of rails to set voltage for each domain
        self.TILESTOAPPLY = tiles # Comma seperated tile list. e.g 0 for just tile 0 and 0,1 for both tiles
        self.SET_FREQUENCY = freq # A dictionary of frequency to be set for each domain.
        self.DSS_OPTION = dss_option
        self.TESTED_DSS = test_dss
        self.TESTED_QDF = test_qdf
        self.BOOT_FREQUENCY = boot_frequency
        self.REPORTED_DSS = reported_dss
        self.TARGETOS = target_os
        self.BYPASS_ENABLED = bypass
        self.TDIODE_TEMP = tdiode_temp
        self.MEML3 = meml3
        self.DEVICEID = deviceid
        self.FLAG_BIOS_FLASH = bios_flash_flag