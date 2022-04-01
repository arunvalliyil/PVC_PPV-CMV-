import __main__
from Helpers.instances import InstanceFactory
from PVCInfo.device_manager import DeviceManager

class MCECheck(object):
    """
    Collects Machine Check Exceptions on target failure
    
    """
    #from atomcore.common_scripts.utils import set_atomsocket
    
    
    
    MCE_FOUND = 'MCEs were found'
    MCE_NOT_FOUND = 'MCEs were not found'
    
    def __init__(self):
        self._tpc = InstanceFactory.getInstance().get_power_control()
        
    def GetMCEs(self):
        '''
        Gets the Machine Check Exceptions from the target

        Returns
        -------
        str: { 'MCEs were found', 'MCEs were not found' }
            Indicate if valid machine check exceptions were found

        Notes
        -----
        1. The MCE registers must be written to standard out
        2. The string 'Test Started' needs to be written to the standard out
           to distinguish between potential script and target hang
        '''
        if (self._tpc.is_target_power_on('') == True):
            print("MCA found; capturing SOC and GT log")
            DeviceManager.getInstance().collect_soc_logs()
        else:
            raise Exception("Cannot capture soc and GT logs")


