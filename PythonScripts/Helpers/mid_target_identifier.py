import sys,os
from Helpers.Configuration import Configuration

class MidTargetIdentifier():
    
    _instance = None

    @staticmethod
    def getInstance():
        if not MidTargetIdentifier._instance:
            MidTargetIdentifier._instance = MidTargetIdentifier()
        
        return MidTargetIdentifier._instance

    def __init__(self):
        self.config = Configuration.getInstance()
        self.mid_target_configured = self.config.get_config_value('general','MID_TARGET')
        self.identified_mid_target= ''
        pass

    def identify_mid_target(self):
        if self.mid_target_configured.upper() in 'AUTO':
            print("Auto detecting mid target")
            mid_target = 'WC'
            with open(r'C:\PythonSV\pysv_config.ini', 'r') as reader:
                lines = reader.readlines()
                for line in lines:
                    if 'sapphirerapids' in line:
                        mid_target = 'AC'
            print("Identified Mid taraget to be {}".format(mid_target))
            return mid_target
            #if not self.identified_mid_target:
            #    print("looking for icx/spr python SV")
            #    if os.path.isdir(r'C:\PythonSV\icelakex'):
            #        self.identified_mid_target = "WC"
            #    elif os.path.isdir(r'C:\PythonSV\sapphirerapids'):
            #        self.identified_mid_target= "AC"
        else:
            self.identified_mid_target = self.mid_target_configured
        
        return self.identified_mid_target

        