from .DssRecovery import DssRecovery
from .recovery_store import RecoveryStore
from .boot_stage_manager import BootStageManager
from .test_executor import TestExecutor
import fusion
import json,os,time,traceback,sys,time
import supported_boot_stages as boot_stage
from Environmentals.env_condition_cache_manager import EnvironmentConditionCacheManager
from Environmentals.env_condition_cache_manager import EnvironmentConditionCache

class RecoveryManager():
    '''
    Manages recovery execution for pvc unit
    '''
    
    def __init__(self, instance,device_manager,configuration, BootStageTransitions):
        print("Initializing Recovery Manager for DSS Recovery")
        self.BootStageManager = BootStageManager(BootStageTransitions, instance, configuration)
        self.env_Cache_manager = EnvironmentConditionCacheManager()
        self.test_executor = TestExecutor(configuration, instance)
        self.config = configuration
        self.instance = instance
        self.api = instance.get_fusion_instance()
        self.power_control = self.instance.get_power_control()
        self.device_manager = device_manager
        self.visualID = "VID"
        self.current_execution_count = 0
        self.execution_limit = self.config.get_config_value('DSSRecovery','RECOVERY_EXECUTION_LIMIT')
        self.recovery_flow_store = "RecoveryStore{}.csv"
        self.tile_count = 0

   
    def create_recovery_flow(self, store):
        d = DssRecovery()
        tile_reported_dss = {}
        tile_recovery_flow = {}

        for tile in range(self.device_manager.populated_tile_count()):
            print('Calculating recovery path for tile {} with recovery resolution {}'.format(tile, d.dss_list[-1]))
            tile_reported_dss[tile] = self.device_manager.read_current_dss_info(tile)
            tile_recovery_flow[tile] = []
            enabled_dss_count = self.device_manager.get_enabled_dss_count(tile_reported_dss[tile])
            if enabled_dss_count == 0:
                print("Tile {} has no enabled dss nothing to recover".format(tile))
                break
            content_dss = d.next_level_dss(enabled_dss_count+1)
            d.chart_recovery(tile_reported_dss[tile],content_dss,tile_recovery_flow[tile])
            store.store_recovery_plan(tile,tile_recovery_flow[tile])
            print("Recovery for tile {} to resolution of {} would take up to {} executions.".format(tile, d.dss_list[-1], len(tile_recovery_flow[tile])))

    def handle_recovery(self , test_flow , test_group = ''):
        self.current_execution_count = 0
        self.tile_count = self.device_manager.populated_tile_count()
        cached_value  = self.env_Cache_manager.read_environment_condition_cache()
        cached_value.TESTED_DSS = {}
        self.env_Cache_manager.update_environment_condition_cache(cached_value)
        
        if self.tile_count == 2:
            print("Identified a two tile unit executing recovery on both tiles")
        else:
            print("Identified a one tile unit executing recovery on the tile")

        store = RecoveryStore(self.config)
        self.create_recovery_flow(store)
        
        while not self.recovery_exec_limit_reached(store):
            for tile in range(self.tile_count):
                self.flag_dss_to_override(store, tile)
            print("Updated Fuse Override flag file for next boot. rebooting unit to take this overrides into effect.")
            
            #self.BootStageManager.reset_unit_for_fuse_update()
            for tile in range(self.tile_count):
                tile_test_result = ''
                applied_dss = self.env_Cache_manager.read_environment_condition_cache().DSS_OPTION[str(tile)]
                if applied_dss:
                    print("Executing tile {} test after setting dss option to {}".format(tile, applied_dss))
                    try:
                        tile_test_result = self.test_executor.execute_test(tile, test_flow, test_group)
                    except (FileNotFoundError,NameError):
                        print("Missing master list file cannot continue with recovery")
                        return "Failed"
                    if tile_test_result:
                        store.update_recovery_status(tile,applied_dss,tile_test_result)
                        if tile_test_result== TestExecutor.Hung:
                            print("Tile{} execution Hung need to reset for recovery before further execution".format(tile))
                            break

        print("Finished recovery execution. Updating DFF tokens in fusion")
        for tile in range(self.tile_count):
            try:
                self.api.dff.add_dff_data("GTEN{}".format(tile),store.get_recovered_dss(tile))
            except Exception as ex:
                print("Failed to update DFF data {}".format(ex))

        return "Passed"

    def recovery_exec_limit_reached(self,store):
        self.current_execution_count +=1
        if int(self.current_execution_count) > int(self.execution_limit):
            print("A maximum execution limit of {} reached ending recovery flow".format(self.execution_limit))
            return True
        
        for tile in range(self.tile_count):
            dss_to_run = store.get_next_dss_option(tile)
            if dss_to_run:
                print("DSS recovery execution limit not reached.Executing recovery iteration #{}".format(self.current_execution_count))
                return False
        return True

    def flag_dss_to_override(self, store, tile):
        try:
            dss_to_run = store.get_next_dss_option(tile)
            print("Executing recovery flow with dss option for tile {} with DSS {}".format(tile , dss_to_run))
            cache = EnvironmentConditionCache()
            cache.DSS_OPTION={str(tile):dss_to_run}
            self.env_Cache_manager.update_environment_condition_cache(cache)
        except:
            print("Failed to update dss override flag for tile {} . trace ".format(tile, traceback.print_exception(*sys.exc_info())))

        return 'Passed'

    