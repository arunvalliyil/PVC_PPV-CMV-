from .DssRecovery import DssRecovery
from Environmentals.env_condition_cache_manager import EnvironmentConditionCacheManager
from Environmentals.env_condition_cache_manager import EnvironmentConditionCache

class DSSManager():

    def __init__(self, device_manager):
        self.device_manager = device_manager
        self.dss_recovery = DssRecovery()
        self.cache_manager = EnvironmentConditionCacheManager()
        pass
    
    def set_multi_tile_dss_flag(self):
        dss_list = []
        tile_count = self.device_manager.populated_tile_count()
        dss_to_enable = 64
        for t in range(tile_count):
            dss = self.get_reported_dss()[str(t)]
            setBits = [ones for ones in dss if ones=='1'] 
            if len(setBits) < dss_to_enable:
                dss_to_enable = len(setBits)
        
        print("Found the lowest dss enabled tile to be with {} DSS".format(dss_to_enable))
        self.set_dss_flag(dss_to_enable)



    def set_dss_flag(self,dss_count, tile = ''):
        tile_count = self.device_manager.populated_tile_count()
        print("Limiting the unit to DSS Count {} for tiles {}".format(dss_count, tile))
        tile_to_set = []
        dss_to_set ={}
        if not tile:
            print("tile to apply not specified applying DSS fuse to all tiles")
            for t in range(tile_count):
                tile_to_set.append(t)
        else:
            tile_to_set.append(tile)
        
        for t in tile_to_set:
            enabled_dss = self.get_reported_dss()[str(t)]
            dss_to_set[str(t)] = self.dss_recovery.get_first_pass(enabled_dss, dss_count).partial_dss

        to_update = EnvironmentConditionCache()
        to_update.DSS_OPTION = dss_to_set
        self.cache_manager.update_environment_condition_cache(to_update)
        print('Flag set to set DSS option to {} on next boot'.format(dss_to_set))
        return "Passed"

    def verify_set_dss(self):
        print("Verifying if previously configured DSS is already applied on the unit")
        try:
            set_dss_option = self.cache_manager.read_environment_condition_cache().DSS_OPTION
            tile0_unit_DSS = self.device_manager.read_current_dss_info()
            if set_dss_option["0"] == tile0_unit_DSS:
                tile1_unit_DSS = self.device_manager.read_current_dss_info("1")
                if set_dss_option["1"] == tile1_unit_DSS:
                    return "Passed"
                else:
                    print("Tile1 DSS expected {} but returned {}".format(set_dss_option["1"], tile1_unit_DSS))
            else:
                print("Tile0 DSS expected {} but returned {}".format(set_dss_option["0"], tile0_unit_DSS))
            return "Failed"
        except Exception as ex:
                return "Failed"

    def record_reported_dss(self):
        print('Recording current reported dss to cace')
        try:
            tile_count = self.device_manager.populated_tile_count()
            reported_dss= {}
            for tile in range(tile_count):
                reported_dss[str(tile)]= self.device_manager.read_current_dss_info(tile)
        
            to_update = EnvironmentConditionCache()
            to_update.REPORTED_DSS = reported_dss
            self.cache_manager.update_environment_condition_cache(to_update)
            return "Passed"
        except Exception as ex:
            print("Failed to record reported dss :{}".format(ex))
            return "Failed"

    def set_first_pass_dss(self, tile = 0 ):
        try:
            print("Setting first pass dss configuration for tile {}".format(tile))
            enabled_dss = self.device_manager.read_current_dss_info(tile)
            dss_count = self.device_manager.get_enabled_dss_count(enabled_dss)
            possible_dss_count= self.dss_recovery.next_level_dss(dss_count)
            print("Setting fuses for first pass ")
            dss_to_set = self.dss_recovery.get_first_pass(enabled_dss, possible_dss_count)
            to_update = EnvironmentConditionCache()
            to_update.DSS_OPTION[str(tile)] = dss_to_set.partial_dss
            self.cache_manager.update_environment_condition_cache(to_update)
            return "Passed"
        except Exception as ex:
            print("Failed to set first pass dss configuration {}".format(ex))
            return "Failed"

    def set_second_pass_dss(self, tile = 0 ):
        try:
            print("Setting second pass dss configuration for tile {}".format(tile))
            enabled_dss = self.device_manager.read_current_dss_info(tile)
            print(enabled_dss)
            dss_count = self.device_manager.get_enabled_dss_count(enabled_dss)
            print(dss_count)
            possible_dss_count= self.dss_recovery.next_level_dss(dss_count)
            print(possible_dss_count)
            dss_to_set = self.dss_recovery.get_second_pass(enabled_dss, possible_dss_count)
            to_update = EnvironmentConditionCache()
            to_update.DSS_OPTION[str(tile)] = dss_to_set.partial_dss
            self.cache_manager.update_environment_condition_cache(to_update)
            return "Passed"
        except Exception as ex:
            print("Failed to set second pass dss configuration {}".format(ex))
            return "Failed"

    def get_reported_dss(self):
        reported_dss= {}
        tile_count = self.device_manager.populated_tile_count()
        reported_dss = self.cache_manager.read_environment_condition_cache().REPORTED_DSS
        if not reported_dss:
            for tile in range(tile_count):
                reported_dss[str(tile)]= self.device_manager.read_current_dss_info(tile)
        return reported_dss
            



