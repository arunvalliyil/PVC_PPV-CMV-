from abc import ABC, abstractmethod
import datetime
import time
from Helpers.instances import InstanceFactory
from Helpers.Profilers.pvc_profiler import PVCProfiler

class TargetPowerControl(ABC):
 
    def __init__(self, value):
        self.value = value
        super().__init__()
        
    def power_on_jtag(self):
        print ("JTAG is off, set JTAG voltage...")
        self._api.power_distribution.set_jtag_voltage(self.get_jtag_power_on_voltage())   

        timeout = self.get_jtag_power_on_timeout()
        starttime = datetime.datetime.now()
        print ("Powering on JTAG...")
        self._api.power_distribution.power_on_jtag()
        while not self._api.power_distribution.is_jtag_power_on():
            time.sleep(0.1)
            if (datetime.datetime.now() - starttime) > datetime.timedelta(seconds=timeout):
                raise RuntimeError("Timed out while waiting for JTAG power to go high")
    
    def cell_power_on(self):
        print("Turning on cell power")
        if not self._api.power_distribution.is_jtag_power_on():
            self.power_on_jtag()
        
    def cell_power_off(self):
        '''
        Turns the cell power off.
        '''
        print("Turning JTAG power off")
        self._api.power_distribution.power_off_jtag()
       
    def is_cell_power_on(self):
        return self._api.power_distribution.is_jtag_power_on()
    
    def is_cell_power_off(self):
        return self._api.power_distribution.is_jtag_power_on()
    
    def target_power_off_control(self, environment=None):
        self._api.power_distribution.power_off_motherboard(0)
        self._api.power_distribution.power_off_motherboard(1)
      
        itp = InstanceFactory.getInstance().get_itp_instance()
        wait_time = 0
        PVCProfiler.getInstance().StopProfiling()

        while not itp.cv.targpower and wait_time <= 50:
            time.sleep(1)
            wait_time += 1
        print('Waited for {} sec for pvc rvp to power down!!!'.format(wait_time))

        
    @abstractmethod
    def get_jtag_power_on_voltage(self):
        pass
    
    @abstractmethod
    def get_jtag_power_on_timeout(self):
        pass
    
    @abstractmethod
    def is_target_power_off(self,environment):
        pass;
    
    @abstractmethod
    def is_target_power_on(self,environment):
        pass;
    
    @abstractmethod
    def target_power_on_control(self):
        pass

    @abstractmethod
    def supported_mode():
        pass
    
    @abstractmethod
    def supported_platform():
        pass