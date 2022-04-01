import os,sys
from pathlib import Path
import pickle
import json
from Environmentals.env_condition_cache_manager import EnvironmentConditionCache
from Environmentals.env_condition_cache_manager import EnvironmentConditionCacheManager

class RecoveryStore():

    def __init__(self, configuration):
        print("Initializing recovery store()")
        self.cache_manager = EnvironmentConditionCacheManager()
        self.config = configuration
        self.store_path = os.path.join(Path(os.path.realpath(__file__)).parent.parent,"Cache")
        self.recovery_flow_store = "Recovery_plan_{}.csv"
        
    def store_recovery_plan(self,tile, recovery_plan):
        file_path = self.recovery_flow_store.format(tile)
        store_full_path = os.path.join(self.store_path,file_path)
        print("Storing recovery plan to {}".format(store_full_path))
        with open(store_full_path, "w") as outfile:
            json.dump(recovery_plan, outfile)

    def update_recovery_status(self, tile, dss_option, execution_status):
        status =[]
        file_name = self.recovery_flow_store.format(tile)
        store_full_path = os.path.join(self.store_path,file_name)
        if execution_status  in "Passed":
            self.update_tested_dss_cache(tile, dss_option)
        if os.path.isfile(store_full_path) and os.stat(store_full_path).st_size > 0:
            with open(store_full_path) as f:
                plans = json.load(f)
                for data in plans:
                    #print("Processing line {}".format(data))
                    if '-' in data:
                        status.append(data)
                        continue
                    updated_line = ''
                    if data == dss_option:
                        updated_line = "{}-{}".format(data,execution_status)
                        #print("Marking DSS recovery option {} execution status for tile {} as {} updating {}".format(data, tile, execution_status,updated_line))
                    elif execution_status.lower() in "passed" and  '-' not in data and not self.got_additional_recovery(data,dss_option):
                        updated_line = "{}-{}".format(data,execution_status)
                        #print("Marking DSS recovery option {} execution status for tile {} as {} updating {}".format(data, tile, execution_status,updated_line))
                    else:
                        #print("Updated line is {}".format(data))
                        updated_line = data
                    status.append(updated_line)

        with open(store_full_path, "w") as outfile:
            json.dump(status, outfile)
    
    def update_tested_dss_cache(self, tile, dss_option):
        current_tile = str(tile)
        to_update = self.cache_manager.read_environment_condition_cache()
        if current_tile in to_update.TESTED_DSS:
            to_update.TESTED_DSS[current_tile] = self.update_tile_info(to_update.TESTED_DSS[current_tile],dss_option)
        else:
            to_update.TESTED_DSS[current_tile] = dss_option
        self.cache_manager.update_environment_condition_cache(to_update)

        print('Updated tested DSS data to cache')

    def update_tile_info(self,current_dss, dss_to_update):
        print("Current tile info is {}, Updating with {}".format(current_dss, dss_to_update))
        count = 0
        to_update = list(current_dss)
        for bit in list(dss_to_update):
            if bit == '1':
                to_update[count] = '1'
            count += 1

        print("Current tile info {} updated to {}".format(current_dss,"".join(to_update) ))
        return "".join(to_update)

    def get_next_dss_option(self, tile):
        file_name = self.recovery_flow_store.format(tile)
        store_full_path = os.path.join(self.store_path,file_name)
        print('Reading recovery options from {}'.format(store_full_path))
        if os.path.isfile(store_full_path) and os.stat(store_full_path).st_size > 0:
            with open(store_full_path) as f:
                for data in json.load(f):
                    if '-' not in data:
                        return data

                return ''
        else:
            print("No Next DSS option for tile {}".format(tile))
            
    def got_additional_recovery(self, partial_dss, current_dss):
        if not current_dss:
            return True
    
        current_state = list(current_dss)
        count = 0
        for bit in partial_dss:
            if bit == '1' and current_state[count] == '0':
                return True
            count += 1
        
        return False

    def get_recovered_dss(self, tile_id):
        tile = str(tile_id)
        print("Getting recovered dss option for tile {}".format(tile))
        cache = self.cache_manager.read_environment_condition_cache()

        if tile in cache.TESTED_DSS:
            print("Returning final recovered DSS option for tile {} to {}".format(tile, cache.TESTED_DSS[tile]))
            return cache.TESTED_DSS[tile]
        
        print("Execution failed for dss recovery")
        return ""