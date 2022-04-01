import sys

from Environmentals.env_condition_cache_manager import EnvironmentConditionCacheManager
from Environmentals.env_condition_cache_manager import EnvironmentConditionCache
from PVCInfo.voltage_manager import VoltageManager

class VminSetter:

    def __init__(self):
        self.voltage_manager = VoltageManager()
        pass

    def get_current_unit_vid(self):
        with open (r'C:\Sthi\Fusion\Cache\vid_under_test.txt', 'r') as reader:
            return reader.readline().strip()

    def set_vmin(self):
        try:
            vid = self.get_current_unit_vid()
            corner = 'compute'
            cache = EnvironmentConditionCacheManager().read_environment_condition_cache()
            if 'compute' in cache.SET_FREQUENCY:
                corner = cache.SET_FREQUENCY['compute']
            elif 'base' in cache.SET_FREQUENCY:
                corner = cache.SET_FREQUENCY['base']
        
            print("Extracting Vmin information for Unit {} for corner {}".format(vid, corner))
            sys.path.append(r'C:\Source\Tools\Execute')
            from sql_data_extract import extract_collected_data as vmin_extractor
            vmin_data = vmin_extractor().get_all_rail_vmins(vid, corner)
            sql_data_collector = vmin_extractor()
            domain_list = sql_data_collector.get_domain_list(vid)
            c = sql_data_collector.get_all_rail_vmins(vid, corner)
            print(c)
            for x in domain_list.Domain:
                print("Updating Domain {}".format(x))
                data = c[c.Domain == x][['VisualID','Domain','Vmin']].values[0]
                print(data)

                tile = data[1].split('_')[1].replace('T','')
                print(tile)
                voltage = data[2]
                print(voltage)
                rail = 'FIVR_{}'.format(data[1].split('_')[0])
                print(rail)
                self.voltage_manager.set_voltage_condition(rail, float(voltage), int(tile))
            
            self.voltage_manager.read_voltage()
            return "Passed"
        except Exception as ex:
            print("Failed to Set Vmins {}".format(ex))
            return "Failed"
