import sys
from PVCInfo.voltage_manager import VoltageManager
from Profilers.base_profiler import BaseProfiler


class VoltageProfiler(BaseProfiler):

    def __init__(self):
        self.voltage_manager = VoltageManager()
        pass
    
    def get_data_to_log(self):
        return_val = voltagedata()
        try:
            for prop in dir(return_val):
                if '__' not in prop:
                    tile = prop.split('_')[2].replace('T','').strip()
                    rail = prop.replace("_T{}".format(tile),'').strip()
                    voltage = self.voltage_manager.read_rail_voltage(rail,tile)
                    setattr(return_val,prop,voltage)
        except Exception as ex:
            print("Failed to collect voltage information {}".format(ex))
        return return_val

class voltagedata:
    FIVR_EU0_T0 = 'Empty'
    FIVR_EU2_T0 = 'Empty'
    FIVR_EU4_T0 = 'Empty'
    FIVR_EU6_T0 = 'Empty'
    FIVR_EU8_T0 = 'Empty'
    FIVR_EU10_T0 = 'Empty'
    FIVR_EU12_T0 = 'Empty'
    FIVR_EU14_T0 = 'Empty'
    FIVR_BASE2_T0 = 'Empty'
    FIVR_EU0_T1 = 'Empty'
    FIVR_EU2_T1 = 'Empty'
    FIVR_EU4_T1 = 'Empty'
    FIVR_EU6_T1 = 'Empty'
    FIVR_EU8_T1 = 'Empty'
    FIVR_EU10_T1 = 'Empty'
    FIVR_EU12_T1 = 'Empty'
    FIVR_EU14_T1 = 'Empty'
    FIVR_BASE2_T1 = 'Empty'