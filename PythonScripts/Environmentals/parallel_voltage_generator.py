import os,sys
import pandas as pd
from Helpers.Configuration import Configuration
from Environmentals.env_condition_cache_manager import EnvironmentConditionCacheManager
from Environmentals.env_condition_cache_manager import EnvironmentConditionCache

class ParallelVoltageGenerator():

    def __init__(self, fivr_lookup):
        self.config = Configuration.getInstance()
        self.fivr_lookup = fivr_lookup
        self.cache_manager = EnvironmentConditionCacheManager()
        pass

    def generate_parallel_voltage_set(self, visual_id, condition_name,voltage, tile):
        cached_data = self.cache_manager.read_environment_condition_cache()
        print("Calculating parallel voltages that needs to be set for visual id {} condition {} for tile {} to be set at {}".format(visual_id, condition_name, tile, voltage))
        return_val = {}
        vmin_store_path = self.config.get_config_value('EnvironmentCondition','CLASS_VMIN_STORE')
        rails_to_set = self.fivr_lookup[condition_name]['Leader']# +self.fivr_lookup[condition_name]['Follower'] 
        for rail in rails_to_set:
            return_val[rail] = voltage

        if os.path.isfile(vmin_store_path):
            f = pd.read_csv(vmin_store_path)
            if f.empty:
                return return_val
            
            freq_key =  ''

            if 'base' in condition_name.lower():
                condition_name = 'base'
                freq_key = 'base'
            elif 'eu' in condition_name.lower():
                condition_name = 'nonsystolic'
                freq_key = 'compute'
            
            
            #f["Domain"] = str(f["Domain"]).lower()
            frequency = int(cached_data.SET_FREQUENCY[freq_key])
            print("Visualid {}; freq {};temp {};domain {}; tile {}".format(visual_id,frequency, 80, condition_name, tile))
            filtered_data = f[(f['VisualID'] == visual_id) & (f['Frequency'] == frequency) & (f['Temperature'] == 80) &(f['Domain'] == condition_name) & (f['Tile'] == "T{}".format(tile))]
            if filtered_data.empty:
                print("vmin data filter returned empty returning set voltage for all rails")
                return return_val

            min_vmin = filtered_data.min(axis=1).values[0]
            #min_vmin = float(filtered_data.head(1)['Vmin'])
            print("Min vmin {} for the vid {} : frequency {}: Domain {}".format(min_vmin,visual_id, frequency, condition_name))

            for rail in rails_to_set:
                UID = '{}'.format(rail.replace('FIVR_',''))
                rail_vmin = filtered_data[UID]
                if rail_vmin.empty:
                    return_val[rail] = voltage
                else:
                    rail_voltage = float(rail_vmin.values[0])
                    return_val[rail] = round(float(voltage) + rail_voltage - float(min_vmin),3)
        else:
            print("Could not find class vmin lookup table at {} setting all rails to the actual set voltage of {}".format(vmin_store_path,voltage))
            for rail in rails_to_set:
                return_val[rail] = voltage
        print(return_val)
        return return_val
    
    def generate_parallel_voltage_read(self, visual_id, condition_name,voltage, tile):
        print("Calculating parallel voltages that needs to be read for visual id {} condition {} for tile {}".format(visual_id, condition_name, tile))
        return_val = {}
        vmin_store_path = self.config.get_config_value('EnvironmentCondition','CLASS_VMIN_STORE')
        rails_to_set = self.fivr_lookup[condition_name]['Leader']
        if os.path.isfile(vmin_store_path):
            vmin_data = pd.read_csv(vmin_store_path)
            for rail in rails_to_set:
                return_val[rail] = voltage - vmin_data["T{}_{}".format(tile,rail)][0]
        else:
            print("Could not find class vmin lookup table at {} setting all rails to the actual read voltage of {}".format(vmin_store_path,voltage))
            for rail in rails_to_set:
                return_val[rail] = voltage
        return return_val
                









