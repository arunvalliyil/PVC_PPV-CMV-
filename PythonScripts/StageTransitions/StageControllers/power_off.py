from FusionBaseClass.boot_stage_controller import BootStageController
from Helpers.instances import InstanceFactory
from Helpers.Configuration import Configuration
import supported_boot_stages as stage
import supported_modes as modes
import time
import datetime
from Helpers.boot_helpers import BootHelper

class PowerOffStageController(BootStageController):
    
    Stage_Handled = stage.PowerOffStage

    def __init__(self):
        self.PWRGOODWAITTIME = 30
        self.DELAY = 1
        self.pysv_loaded = False
        self.wait_time = 0
        self.boot_helper = BootHelper()

    def get_supported_next_stage(self):
        return [stage.FivrBreak]
    
    def is_in_boot_stage(self, boot_stage):
        print("Checking if target is in {}".format(PowerOffStageController.Stage_Handled))
        instance = InstanceFactory.getInstance()
        return instance.get_power_control().is_target_power_off('')
    
    def start_transition(self, from_stage, to_stage):
        print("Initiating transition from {} to {}".format(from_stage, to_stage))
        InstanceFactory.getInstance().get_power_control().target_power_on_control()
        #time.sleep(60) # remove
        itp = InstanceFactory.getInstance().get_itp_instance()
        
        self.boot_helper.wait_for_power_on(itp)
        print("Power on detected")
        self.boot_helper.wait_for_itp_refresh(itp)
        print("itp refreshed loading python sv..")
        
        #self.do_startup(r'C:\PythonSV\pontevecchio\startpvc_auto.py')

        print("Transition from %s to %s Successful" % (from_stage, to_stage))
    
    def do_startup(self, startup_script):
        print("PythonSV will be loaded post powering on the platform")
        try:
            import os
            if not os.path.exists(startup_script):
                print ("Fatal Error: start up script not found at {}".format(startup_script))
                return
        
            print("Initiating the start up script at {0}".format(startup_script))
            import runpy
            d = runpy.run_path(startup_script, run_name='__main__')
            globals().update(d)
        except Exception as inst:
            print ("Exception caught: %s" % inst) 
            print ('Warning: pythonsv for pvc not started with: "%s" ' % startup_script)
        

