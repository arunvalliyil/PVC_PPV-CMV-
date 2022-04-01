import time
from FusionBaseClass.target_power_control import TargetPowerControl
from Helpers.Configuration import Configuration
from Helpers.instances import InstanceFactory
import supported_platforms as platforms
import supported_modes as mode


class WCTargetPowerControl(TargetPowerControl):
 
    config_section = "WC"
    power_on_check_channel = "P5V_AUX_WC"
    power_on_threshold = 2.0
    
    power_off_check_channel = "P3V3_AUX_WC"
    power_off_threshold = .475
    
    jtag_power_on_voltage = 1 #0=0V, 1=5V, 2=8V, 3=12V
    jtag_power_on_timeout = 10
    
    
    def __init__(self):
        instance = InstanceFactory.getInstance()
        self._api = instance.get_fusion_instance()
        self.config = Configuration.getInstance()
    
    def target_power_on_control(self):
        print ("target_power_on_control: turn on ATX")
        self._api.power_distribution.power_on_motherboard(0)
        self._api.power_distribution.power_on_motherboard(1)
        while self._api.read_dvm(WCTargetPowerControl.power_off_check_channel) < 3.0:
            time.sleep(1)
            print ("P3V3_PowerControl value is %s" % self._api.read_dvm(WCTargetPowerControl.power_off_check_channel))
            
        time.sleep(15)
 
    def get_jtag_power_on_voltage(self):
        return WCTargetPowerControl.jtag_power_on_voltage

    def get_jtag_power_on_timeout(self):
        return WCTargetPowerControl.jtag_power_on_timeout

    def is_target_power_off(self, environment):
        try:
            print ("WCTargetPowerControl.is_target_power_off.\n")
            V3P3_DEBUG = self._api.read_dvm(WCTargetPowerControl.power_on_check_channel)
            print ("V5P0_DEBUG value is %s" % V3P3_DEBUG)
            return (V3P3_DEBUG < float(WCTargetPowerControl.power_off_threshold))
        except Exception as ex:
            print ("{}:- Power on status check failed.Message {}".format(self.__class__.__name__, ex.message))
            return False

    def is_target_power_on(self,environment):
        try:
            print ("WCTargetPowerControl.is_target_power_on.\n")
            V5P0_DEBUG = self._api.read_dvm(WCTargetPowerControl.power_on_check_channel)
            print ("V5P0_DEBUG value is %s" % V5P0_DEBUG)
            return (V5P0_DEBUG > float(WCTargetPowerControl.power_on_threshold))
        except Exception as ex:
            print ("{}:- power status off check failed.Message {}".format(self.__class__.__name__, ex.message))
            return False
    
    def supported_platform():
            return [platforms.WilsonCity]

    def supported_mode():
        return mode.PPV
