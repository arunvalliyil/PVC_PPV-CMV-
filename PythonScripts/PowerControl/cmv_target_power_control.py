from FusionBaseClass.target_power_control import TargetPowerControl
from Helpers.Configuration import Configuration
from Helpers.power_control import BasePowerControl
import supported_platforms as platforms
import supported_modes as mode

import time
import Helpers.lcbe_programmer as lcbe

class CMVPowerControl(TargetPowerControl):
 
    def __init__(self):
        self.lcbe_programmed = False
        self.cell_poweron_status = False
        self.config = Configuration.getInstance()
        self.power_control = BasePowerControl()
        self.powersplitter_port = int(self.config.get_config_value('general','POWERSPLITTER_PORT')) -1
       
    def cell_power_on(self):
        self.cell_poweron_status = True
        print("No need to handle power on for CMV")

    def cell_power_off(self):
        self.cell_poweron_status = False
        print("No need to handle power off for CMV")
    
    def is_cell_power_on(self):
        return self.cell_poweron_status
    
    def is_cell_power_off(self):
        return not self.cell_poweron_status
    
    def target_power_off_control(self, environment):
        print("Turning off target power using power splitter port {}".format(self.powersplitter_port))
        self.power_control.turn_off_power_splitter(self.powersplitter_port)
        from Helpers.Profilers.pvc_profiler import PVCProfiler
        PVCProfiler.getInstance().StopProfiling()
        time.sleep(20) # wait for the platform to settle after a power down
      
    def is_target_power_on(self,environment):
        return_val = False
        try:
            return_val =  self.power_control.is_port_on(self.powersplitter_port)
        except:
            print("Failed to check power control port status")
        return return_val
    
    def is_target_power_off(self, environment):
        return not self.is_target_power_on(environment)

    def target_power_on_control(self):
        print("Turning on power splitter port {} to turn on platform".format(self.powersplitter_port))
        if lcbe.emulate_bios(lcbe.mid_target) == lcbe._strPass:
           print("Updated Mid target BIOS for emulation")
        else:
            raise("Failed to emulate BIOS for Mid target") 
        
        try:
            if lcbe.emulate_bios(lcbe.target) == lcbe._strPass:
                print("Updated target BIOS for emulation")
            else:
                raise("Failed to emulate BIOS for target") 
        except:
            print("LCBE flash failed for Target, is it SPI?")

        print("Turning on power splitter port {} to turn on platform".format(self.powersplitter_port))
        self.power_control.turn_on_power_splitter(self.powersplitter_port)
        return

    def get_jtag_power_on_voltage(self):
        # does not matter for CMV
        return 0
    
    def get_jtag_power_on_timeout(self):
        # does not matter for CMV
        return 100

    def supported_platform():
        return [platforms.ArcherCity, platforms.WilsonCity]

    def supported_mode():
        return mode.CMV
        