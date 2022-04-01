import sys
import json
import os
from PVCInfo.device_manager import DeviceManager
from .instances import InstanceFactory
from Helpers.Configuration import Configuration
from Environmentals.env_condition_cache_manager import EnvironmentConditionCacheManager
from Environmentals.env_condition_cache_manager import EnvironmentConditionCache


class ItuffTokenHelper():

    def __init__(self):
        self.device_manager = DeviceManager.getInstance()
        self.api = InstanceFactory.getInstance().get_fusion_instance()
        pass

    def upload_ituff_data(self):
        try:
            print("Uploading collected ituff data")
            screen_output = Configuration.getInstance().get_config_value('general','BOOTSCRIPT_OUTPUT')

            print(screen_output)
            screen_data = ''
            if os.path.exists(screen_output):
                print("Got screen out put info file at {}".format(screen_output))
                with open(screen_output, 'r') as file:
                    screen_data = file.read()

            self.upload_screening_info(screen_data)
            self.upload_IFWI_Details()
            
        except Exception as e:
            print("Failed to upload ituff data {}".format(e))
        return "Passed"

    def upload_IFWI_Details(self):
        try:
            pvc_ifwi = Configuration.getInstance().get_config_value('lcbeconfigs','LCBE0_BIOS_PATH')
            self.api.misc_data.add_misc_data_to_run_result('PVC_IFWI',pvc_ifwi)
        except Exception as ex:
            print("Failed to update IFWI information to ituff: {}".format(ex))
    
    def upload_screening_info(self, screening_output):
        self.api.ituff_log("PPVScreenInfo", str(screening_output))
        cacheManager = EnvironmentConditionCacheManager()
        cache = cacheManager.read_environment_condition_cache()
        if not cache.REPORTED_DSS:
            return
        
        self.api.dff.add_dff_data('QDF', cache.TESTED_QDF)
        self.api.dff.add_dff_data('FREQ', cache.BOOT_FREQUENCY)
        
        for tile in range(2):
            if str(tile) in cache.REPORTED_DSS:
                if cache.REPORTED_DSS[str(tile)]:
                    hex_value = hex(int(cache.REPORTED_DSS[str(tile)],2))
                    print("Updating ituff data for  tile {} DSS :- {}".format(tile, hex_value))
                    self.api.dff.add_dff_data('GTEN{}'.format(tile), hex_value)