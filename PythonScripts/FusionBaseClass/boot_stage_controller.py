from abc import ABC, abstractmethod
import datetime
import time

class BootStageController(ABC):
 
    Stage_Handled = ""

    def __init__(self):
        super().__init__()
    
    @abstractmethod    
    def is_in_boot_stage(self, boot_stage):
        pass

    @abstractmethod
    def start_transition(self, from_Stage, to_Ssage):
        pass
    
    @abstractmethod
    def get_supported_next_stage(self):
        pass
    
    def start_transition_method(self, from_stage, to_stage):
        if not self.is_in_boot_stage(from_stage):
            raise Exception("Currently not in {} this controller cannot handle start transition".format(from_stage))
        
        if from_stage == to_stage:
            print("Already at {}".format(to_stage))
            return
        
        if not to_stage in self.get_supported_next_stage():
            raise Exception("Transition from {} to {} is not defined in python".format(from_stage, to_stage))

        self.start_transition(from_stage, to_stage)



    
    