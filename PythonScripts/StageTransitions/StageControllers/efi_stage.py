from FusionBaseClass.boot_stage_controller import BootStageController
from Helpers.instances import InstanceFactory
from Helpers.Configuration import Configuration
import supported_boot_stages as stage
import supported_modes as modes
import time
import datetime

class EFIStageController(BootStageController):
    
    Stage_Handled = stage.EFIStage

    def get_supported_next_stage(self):
        return [stage.PowerOffStage]
    
    def is_in_boot_stage(self, boot_stage):
        _api = InstanceFactory.getInstance().get_fusion_instance()
        serial_port = InstanceFactory.getInstance().get_fpd_utilities().get_marionette_serial_port()
        print("Configuring serial port {} to poll for status ".format(serial_port))
        _api.serial_port.configure_then_listen_on_serial_port(serial_port,'BR_115200','DB_8','NO_PARITY','ONE','NONE')
        print("Checking if target is in {}".format(boot_stage.replace('Stage','').lower()))
        return str.lower(_api.marionette.get_connected_os('Serial',serial_port)) in str.lower(boot_stage)

    def start_transition(self, from_stage, to_stage):
        print("Initiating transition from {} to {}".format(from_stage, to_stage))
        instance = InstanceFactory.getInstance()
        instance.get_power_control().target_power_off_control()
        print("Transition from %s to %s Successful" % (from_stage, to_stage))
         