import time
import supported_boot_stages as boot_stage

class BootStageManager:
    
    def __init__(self, BootStageTransitioner, instance, configuration):
        self.BootStageTransitioner = BootStageTransitioner
        self.config = configuration
        self.instance = instance
        self.power_control = self.instance.get_power_control()


    def reset_unit_for_fuse_update(self):
        boot_try_count = self.config.get_config_value('DSSRecovery','BOOT_TRY_COUNT')
        boot_count = 1
        while(boot_count < int(boot_try_count)):
            try:
                if(self.try_boot_part()):
                   return   
                else :
                    boot_count += 1

            except:
                boot_count += 1
                print("Failed to boot part in attempt {}".format(boot_count))
            
    def try_boot_part(self):
        if self.power_control.is_target_power_on(''):
            print("Target is powered on turning off target")
            self.power_control.target_power_off_control()
            
        while(not self.power_control.is_target_power_off('')):
            time.sleep(5)
            print("Waiting for target to be powered off")
            
        print("Target is powered off. Initiating Boot sequence")
        self.BootStageTransitioner.start_transition_to_boot_stage(boot_stage.PowerOffStage, boot_stage.FivrBreak, 180000)

        self.BootStageTransitioner.wait_for_transition_to_boot_stage(boot_stage.PowerOffStage, boot_stage.FivrBreak, 180000)
            
        print("Unit Booted to Fivr Break Stage. Continuing to Fuse Break to update Fuse overrides")
        self.BootStageTransitioner.start_transition_to_boot_stage(boot_stage.FivrBreak, boot_stage.FuseBreak, 180000)

        self.BootStageTransitioner.wait_for_transition_to_boot_stage(boot_stage.FivrBreak,boot_stage.FuseBreak, 180000) 

        print("Unit Booted to Fivr Break Stage. Continuing to EFI Stage")
            
        self.BootStageTransitioner.start_transition_to_boot_stage(boot_stage.FuseBreak,boot_stage.EFIStage, 180000)

        self.BootStageTransitioner.wait_for_transition_to_boot_stage(boot_stage.FuseBreak,boot_stage.EFIStage, 180000)
        
        return True