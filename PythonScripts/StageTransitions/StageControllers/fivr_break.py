import supported_boot_stages as stage
import process_fle
from FusionBaseClass.boot_stage_controller import BootStageController
from Helpers.Configuration import Configuration
from Helpers.instances import InstanceFactory
import supported_modes as modes
import time
import sys
if r'C:\STHI\Fusion\ptm' not in sys.path: sys.path.append(r'C:\STHI\Fusion\ptm')

class FivrBreakController(BootStageController):
    
    Stage_Handled = stage.FivrBreak
    
    def get_supported_next_stage(self):
        return [stage.FuseBreak, stage.PowerOffStage]
    
    def is_in_boot_stage(self, boot_stage):
        instance = InstanceFactory.getInstance()
        print("Checking if target is in {}".format(FivrBreakController.Stage_Handled))
        return instance.get_power_control().is_target_power_on('')
    
    def start_transition(self, from_stage, to_stage):
        print ("Starting to transition from %s to %s" % (from_stage, to_stage))
        instance = InstanceFactory.getInstance()
        if to_stage == stage.PowerOffStage:
            print("Turning off target power")
            instance.get_power_control().target_power_off_control('')
            return

        try:
            self.TransitionToFuseBreak(instance.get_itp_instance(),instance.get_fusion_instance())
        except Exception as ex:
            print (ex)
            raise ValueError("Failed to transition from %s to %s" % (from_stage, to_stage))

    def TransitionToFuseBreak(self, itp, api):
        return
