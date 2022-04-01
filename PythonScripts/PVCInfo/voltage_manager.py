import sys
if r'C:\PythonSV\pontevecchio\fivr\scripts' not in sys.path: sys.path.append(r'C:\PythonSV\pontevecchio\fivr\scripts')
from os.path import exists
import BasicTools as bt
import os.path
from Helpers.instances import InstanceFactory
from Environmentals.parallel_voltage_generator import ParallelVoltageGenerator
from Environmentals.env_condition_cache_manager import EnvironmentConditionCacheManager
from Environmentals.env_condition_cache_manager import EnvironmentConditionCache
import threading


class VoltageManager():

    def __init__(self):
        self.instance = InstanceFactory.getInstance()
        self.fusion_api = self.instance.get_fusion_instance()
        self.FIVR_Lookup = self.populate_fivr_lookup()
        self.supported_conditions = self.FIVR_Lookup.keys()
        self.parallel_voltage_generator = ParallelVoltageGenerator(self.FIVR_Lookup)
        self.cache_manager = EnvironmentConditionCacheManager()
        self.path_to_file = r'C:\sthi\fusion\cache\vid_under_test.txt'
        pass

    def verify_device_info(self, condition_name, expected_value):
        return self.read_device_condition(condition_name) == expected_value
    
    def read_rail_voltage(self, rail, tile):
        tool = bt.BasicTools(rail, tile)
        tool.Enable_logger = False
        returnval =  round(tool.VoltageGet(),3)
        #print("Read Voltage {} for rail {} and tile {}".format(returnval, rail, tile))
        return returnval

    def read_device_condition(self, condition_name):
        print("Trying to read voltage condition {} from the device".format(condition_name))
        #cached_data = self.cache_manager.read_environment_condition_cache()
        
        if 'vcceu' in condition_name.lower():
            rail_to_set, tile_to_set = self.extract_rail_tile_to_process()
            print("Reading Set Voltage for tile {} and rail {}".format(tile_to_set, rail_to_set))
            if tile_to_set and rail_to_set:
                return self.read_rail_voltage(rail_to_set,tile_to_set)
        elif 'vccbase' in condition_name.lower():
            rail_to_set, tile_to_set = self.extract_rail_tile_to_process()
            if tile_to_set and rail_to_set:
                return self.read_rail_voltage('FIVR_BASE2', tile_to_set)
        
        # if there are no tiles/ rails specified return the lowest voltage across all chiplets across all tiles
        rails_to_process = self.FIVR_Lookup[condition_name]['Leader']
        min_voltage = 1
        tiles_to_apply  = self.calculate_tiles_to_apply()
        for tile in tiles_to_apply:
            for rail in rails_to_process:
                tool = bt.BasicTools(rail, tile)
                voltage  = tool.VoltageGet()
                if voltage < min_voltage:
                    min_voltage = voltage
        print("Minimum voltage recorded across all chiplet is {}".format(min_voltage))
        return round(min_voltage,3)
    
    def enable_fivr_list(self, rails , voltage, tile):
        try:
            print("Invoking Enable to set voltage {} for tile {}".format(voltage, tile))
            bt._tile_index = tile
            tool = bt.BasicTools()
            bt.Enable_protection = False
            tool.enable_list(rails,voltage)
        except Exception as ex:
            print("Failed to enable the rails to voltage {} for tile {} :- {}".format(voltage, tile, ex))

    # Set Voltage for rail  in tille to voltage
    def set_voltage_condition(self, rail, voltage, tile):
        print("Setting Voltage {} for rail {} for tile {}".format(voltage, rail, tile))
        try:
            tool = bt.BasicTools(rail, tile)
            tool.Enable_protection = False
            tool.Enable_logger = False
            tool.VoltageSet(voltage) 
        except Exception as ex:
            print("Failed to set voltage: Trying again "+ ex)

    def set_eu_rails(self,condition_name, voltage, tile):
        rail_to_set , tile_to_set = self.extract_rail_tile_to_process()
        #cached_data = self.cache_manager.read_environment_condition_cache()
        rails_to_process = self.FIVR_Lookup[condition_name]['Leader'] + self.FIVR_Lookup[condition_name]['Follower']
        
        if rail_to_set and tile_to_set:
            #print("Enabling all FIVRs to {}v for tile {} before setting chiplet voltage to {}".format(0.9, tile, voltage))
            #self.enable_fivr_list(rails_to_process, 0.9, tile)
            print("Setting voltage {}v for rail {} on tile {}".format(voltage, rail_to_set, tile_to_set))
            self.set_voltage_condition(rail_to_set, voltage, tile_to_set)
        else:
            print("Enabling all FIVRs to {}v for tile {}".format(voltage, tile))
            visual_id = ''
            if exists(self.path_to_file):
                with open(self.path_to_file,'r') as reader:
                    visual_id = reader.read()
                print("Read Visual id as {}from cache".format(visual_id))            
                
            parallel_voltages = self.parallel_voltage_generator.generate_parallel_voltage_set(visual_id,condition_name,voltage, tile)
         
            for rail in rails_to_process:
                voltage_to_set = parallel_voltages[self.get_leader_for_rail(rail)]
                print("Setting Voltage {} to rail {} on tile {}".format(voltage_to_set, rail, tile))
                self.set_voltage_condition(rail, voltage_to_set, tile)
            print("All Voltages set for rails reading them back now")
            self.read_voltage()
            #self.enable_fivr_list(rails_to_process, voltage, tile)

    def set_base_rails(self,condition_name, voltage, tile):
        rail_to_set , tile_to_set = self.extract_rail_tile_to_process()
        cached_data = self.cache_manager.read_environment_condition_cache()
        parallel_voltages = self.parallel_voltage_generator.generate_parallel_voltage_set("visual_id",condition_name,voltage, tile)
        rail = self.determine_rails_to_process(condition_name, cached_data, tile)[0]
        slave_rails = self.FIVR_Lookup[condition_name]['Follower']
        if tile_to_set:
            if str(tile_to_set) == str(tile) :
                self.set_voltage_condition(rail, parallel_voltages[rail], tile)
                for slave_rail in slave_rails:
                    self.set_voltage_condition(slave_rail, parallel_voltages[rail], tile)
            else:
                self.set_voltage_condition(rail, .9, tile)
                for slave_rail in slave_rails:
                    self.set_voltage_condition(slave_rail, .9, tile)
        else:
            self.set_voltage_condition(rail, parallel_voltages[rail], tile)
            for slave_rail in slave_rails:
                self.set_voltage_condition(slave_rail, parallel_voltages[rail] , tile)
    
    def calculate_tiles_to_apply(self):
        cached_data = self.cache_manager.read_environment_condition_cache()
        tiles_to_apply = []
        if not cached_data.TILESTOAPPLY:
             sv = self.instance.get_python_sv_instance()
             for tile in range(len(sv.gfxcard0.tiles)):
                tiles_to_apply.append(tile)
        else:
            for tile in cached_data.TILESTOAPPLY.split(','):
                tiles_to_apply.append(tile)
        print("Voltage needs to be set on tiles {}".format(tiles_to_apply))
        return tiles_to_apply

    def set_device_condition(self,condition_name, voltage):
        print("Setting voltage condition {} to {}".format(condition_name, voltage))
        cached_data = self.cache_manager.read_environment_condition_cache()
        tiles_to_apply = self.calculate_tiles_to_apply()
        retry_count = 3
        while retry_count >0:
            for tile in tiles_to_apply:
                if "VCCEU"in condition_name.upper():
                    self.set_eu_rails(condition_name,voltage, tile)
                elif "VCCBASE" in condition_name.upper():
                    self.set_base_rails(condition_name,voltage, tile)
                
            
            read_condition = self.read_device_condition(condition_name)
            if round(read_condition,3) != round(voltage,3):
                retry_count = retry_count - 1
                print("While setting condition {} to voltage {} read back value {}. Will retry {} times".format(condition_name, voltage, read_condition, retry_count))
            else:
                retry_count = 0

    def read_chiplet_disable(self, tile):
        sv = self.instance.get_python_sv_instance()
        fuse_value = ''
        if str(tile) == 0:
            fuse_value = sv.gfxcard0.tile0.fuses.punit.pcode_gt_chiplet_disable
        else:
            fuse_value = sv.gfxcard0.tile1.fuses.punit.pcode_gt_chiplet_disable

        return bin(fuse_value).replace('0b','')

    def determine_rails_to_process(self, condition_name, cached_data, tile):
        print("Determining the rails to set for condition name {}".format(condition_name))
        chiplet_disable = ''
        rails_to_process = self.FIVR_Lookup[condition_name]['Leader']

        if condition_name.upper() in "VCCEU":
            chiplet_disable = self.read_chiplet_disable(tile)
            print("Chiplet disable is {}".format(chiplet_disable))
            count = 0
            for chiplet in chiplet_disable:
                if chiplet == '1':
                    rails_to_process.remove('FIVR_EU{}'.format(count *2))
                count +=1
          
        if not rails_to_process or len(rails_to_process) == 0:
            print("Voltage rail to process is not overriden updating all leader rails")
            return self.FIVR_Lookup[condition_name]["Leader"]
        
        return rails_to_process

    def extract_rail_tile_to_process(self):
        rail_to_set = ''
        tile_to_set = ''
        rail_selector = r'C:\Sthi\Fusion\Cache\railselector.txt'
        tile_selector = r'C:\Sthi\Fusion\Cache\tileselector.txt'

        if os.path.exists(rail_selector):
            with open(rail_selector, 'r') as f:
                rail_to_set = f.read()
                print("Voltage for rail {}".format(rail_to_set))
        
        if os.path.exists(tile_selector):
            with open(tile_selector, 'r') as f:
                tile_to_set = f.read()
                print("Voltage for tile {}".format(tile_to_set))
        
        return rail_to_set, tile_to_set

    def populate_fivr_lookup(self):
        return {
            "VCCEU":{
                        "Leader":["FIVR_EU0","FIVR_EU2","FIVR_EU4","FIVR_EU6","FIVR_EU8","FIVR_EU10","FIVR_EU12","FIVR_EU14"],
                        "Follower":["FIVR_EU1","FIVR_EU3","FIVR_EU5","FIVR_EU7","FIVR_EU9","FIVR_EU11","FIVR_EU13","FIVR_EU15"]
                        },
            "VCCBASE":{
                        "Leader":["FIVR_BASE2","FIVR_BASE0","FIVR_BASE1","FIVR_BASE3"],
                        "Follower":["FIVR_BASE0","FIVR_BASE1","FIVR_BASE3"]
            },
             "VCCEU_OS":{
                        "Leader":["FIVR_EU0","FIVR_EU2","FIVR_EU4","FIVR_EU6","FIVR_EU8","FIVR_EU10","FIVR_EU12","FIVR_EU14"],
                        "Follower":["FIVR_EU1","FIVR_EU3","FIVR_EU5","FIVR_EU7","FIVR_EU9","FIVR_EU11","FIVR_EU13","FIVR_EU15"]
                        },
            "VCCBASE_OS":{
                        "Leader":["FIVR_BASE2","FIVR_BASE0","FIVR_BASE1","FIVR_BASE3"],
                        "Follower":["FIVR_BASE0","FIVR_BASE1","FIVR_BASE3"]
            },
            "VCCHBM":{
                        "Leader":["FIVR_HBM0","FIVR_HBM1","FIVR_HBM2","FIVR_HBM3"]
            },
            "VCCHBMHV":{
                        "Leader" :["FIVR_HBMHV0","FIVR_HBMHV1","FIVR_HBMHV2","FIVR_HBMHV3"]
            },
            "VCCMDFI":{"Leader":["FIVR_MDFIA_C","FIVR_MDFIA_T"]}
        }

    def get_leader_for_rail(self, rail):
        return_val = rail
        if 'base' in rail.lower():
            return_val = 'FIVR_BASE2'

        if rail in self.FIVR_Lookup['VCCEU']['Follower']:
            rail_count = int(rail.replace('FIVR_EU',''))
            return_val = 'FIVR_EU{}'.format(rail_count -1)
        
        return return_val
    
    def read_voltage(self):
        try:
            tool = bt.BasicTools()
            return tool.Get_AllVoltages()
        except:
            print("")
