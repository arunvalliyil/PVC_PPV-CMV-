from PVCInfo.device_manager import DeviceManager
from Profilers.base_profiler import BaseProfiler

class FrequencyProfiler(BaseProfiler):

    def __init__(self):
        pass
    
    def get_data_to_log(self):
        return_val = freqdata()
        try:
            return_val.compute_freq = DeviceManager.getInstance().read_device_condition('compute')
            return_val.base_freq = DeviceManager.getInstance().read_device_condition('base')
            return_val.link_freq = DeviceManager.getInstance().read_device_condition('link')
            return_val.hbm_freq = DeviceManager.getInstance().read_device_condition('hbm')
        except Exception as ex:
            print("Failed to collect frequency information {}".format(ex))
        return return_val


class freqdata:
    compute_freq = 'Empty'
    base_freq = 'Empty'
    link_freq = 'Empty'
    hbm_freq = 'Empty'
    

