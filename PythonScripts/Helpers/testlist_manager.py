import os,sys, json
from os.path import exists
from Configuration import Configuration
from instances import InstanceFactory
#sys.path.append(os.path.join(parent, 'Environmentals'))
from env_condition_cache_manager import EnvironmentConditionCacheManager
from env_condition_cache_manager import EnvironmentConditionCache

class TestListManager():

    def __init__(self):
        self.config = Configuration.getInstance()
        self.is2TUnit = None
        self.instance = InstanceFactory.getInstance()
        self.lookup_location = self.config.get_config_value('general','BLACKLIST_LOOKUP')
        self.testlist_cache_location = self.config.get_config_value('general','TESTLIST_CACHE')
        self.testskiplist_cache_location = self.config.get_config_value('general','TEST_SKIP_CACHE')
        self.test_count = 0
        self.can_execute_test_enabled = False
        self.master_skip_list = None
        self._load_skip_list()
        self.cache_manager = EnvironmentConditionCacheManager()

    def _load_skip_list(self):
        if exists(self.testskiplist_cache_location):
            try:
                with open(self.testskiplist_cache_location, 'r') as reader:
                    self.master_skip_list = json.load(reader)
                print("Loaded skip list from {}".format(self.testskiplist_cache_location))
            except Exception as ex:
                print("Failed to load skip list {}".format(ex))
        else:
            print("Skip list file not found.")

    def can_execute_lsn_test(self, tile):
        return_val = True
        tile_list = []
        try:
            api = self.instance.get_fusion_instance()
            current_test = api.test_iteration.Test.Name.strip()
            print("Checking whether to run test {}".format(current_test))
            cache = self.cache_manager.read_environment_condition_cache()
            if not cache.MEML3:
                print("Cache MEML3 data is empty")
                return return_val

            if str(tile).lower() == 'm':
                tile_list = [0,1]
            else:
                tile_list = [tile]
            print("tile list is {}".format(tile_list))

            for tile in tile_list:
                if "T{}".format(str(tile)) not in cache.MEML3:
                    print("Cache Empty or tile cache information is missing current cache is {}".format(cache.MEML3))
                    return return_val
                else:
                    print("Found MEML3 cache information for tile {}".format(tile))

                mem_l3 = str(cache.MEML3["T{}".format(str(tile))])
                print("Current unit config is {}".format(mem_l3))
                skip_list = {}
                skip_list = self.master_skip_list['MEM_L3_SKIP_LIST']['Tile{}'.format(tile)]
                print(skip_list)
                if mem_l3 in skip_list:
                    print("skip list for current config is ")
                    print(skip_list[mem_l3])
                    if current_test in skip_list[mem_l3]:
                        print("Skipping test {} for the unit since meml3_en is {}".format(current_test, mem_l3))
                        return False
            else:
                print("Missing {} in skip_list".format(current_test))
        except Exception as ex:
            print("Failed to check if the test can be executed :{}".format(ex))
        return return_val

    def can_run_test(self):
        return_val = True
        try:
            api = self.instance.get_fusion_instance()
            current_test = api.test_iteration.Test.Name 
            print("Checking whether to run test {}".format(current_test))
            blacklist_test_list = []
            if not os.path.exists(self.lookup_location):
                return return_val
                
            with open(self.lookup_location) as test_list:
                for test in test_list.readlines():
                    if test and test.lower() == current_test.lower():
                        return_val =  False
                        break

        except Exception as ex:
            print("Failed to verify if the test was black listed :- {}".format(ex))
        
        return return_val
    
    def prepare_lsn_blacklist(self):
        print("Preparing LSN black list test based on current unit ")
        sv = self.instance.get_python_sv_instance()
        sv.gfxcard0.tiles.f
    
    def can_execute_2T_test(self):
        if self.can_execute_test_enabled and  not self.can_execute_test(): # while checking for can execute for 2T unit also check if we can execute as well
            return False

        if not self.is2TUnit:
            sv = self.instance.get_python_sv_instance()
            if len(sv.gfxcard0.tiles) == 2:
                self.is2TUnit = True
            else:
                self.is2TUnit = False
        return self.is2TUnit

    def update_reboot(self):
        self.test_count = self.test_count+1
        print("test count is {}".format(self.test_count))
        return "Passed"

    def null_operation(self):
        return "Passed"

    def Timetoreboot(self):
        if self.test_count == 4:
            self.test_count = 0
            print("Its time to reboot after 4 tests")
            return True
        return False
    
    def can_execute_test(self):
        self.can_execute_test_enabled = True
        api = self.instance.get_fusion_instance()
        qdf = api.lot_info.ProductID.Sspec
        previous_iteration_result = ''
        if api.previous_iteration:
            previous_iteration_result = api.previous_iteration.IterationResult
        
        current_test_list = api.test_iteration.TestList
        print("[Can Execute Test] Current test list is {}".format(current_test_list))
        cached_test_list  = ''
        if not os.path.exists(self.testlist_cache_location):
            with open(self.testlist_cache_location, 'w') as writer:
                writer.write(current_test_list)
        
        with open(self.testlist_cache_location, 'r') as reader:
            cached_test_list = reader.readline()
        print("[Can Execute Test] Cached test list is {}".format(cached_test_list))
        
        if cached_test_list == current_test_list:
            print("[Can Execute Test] Still in same test list")
            if not previous_iteration_result or previous_iteration_result.lower() == 'passed':
                print(" [Can Execute Test] Previous test passed!!!")
                return True
            else:
                print("[Can Execute Test] Previous test failed skipping all remaining tests in the testlist")
                return False
        else:
            print("[Can Execute Test] New Test list to execute")
            with open(self.testlist_cache_location, 'w') as writer:
                writer.write(current_test_list)
            return True
