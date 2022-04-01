import sys
import os
from Helpers.Configuration import Configuration

class ModeIdentifier:
    
    _instance = None
    
    @staticmethod
    def getInstance():
        if ModeIdentifier._instance ==  None:
            ModeIdentifier()
        return ModeIdentifier._instance
        
    def __init__(self):
        if ModeIdentifier._instance !=None:
            raise Exception("Singleton class use getInstance to Create an instance.")
        else:
            print("Initializeing ModeIdentifier")
            self.config = Configuration.getInstance()
            self.mode = None
            ModeIdentifier._instance = self
        
    def identify_mode(self):
        if self.mode != None:
            return self.mode
        
        app_path = self.config.get_config_value('general','MODULE_APP_PATH')
        if os.path.exists(app_path):
            print("Switching to CMV Mode")
            self.mode = "CMV"
        else:
            print("Switching to PPV Mode")
            self.mode = "PPV"
        return self.mode
        
        
        