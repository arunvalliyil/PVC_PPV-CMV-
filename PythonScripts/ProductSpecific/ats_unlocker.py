from Configuration import Configuration

class ATSUnlocker():
    
    
    def __init__(self):
        self.config = Configuration.getInstance()
        
    
    def unlock(self):
        self.config = Configuration.getInstance()
        unlock_method = config.get_config_value('unlock','UNLOCK_METHOD')
        if unlock_method == 'ferum':
            self.ferum_unlocker()
        elif unlock_method == 'metalkey':
            self.metal_key_unlocker()
        elif unlock_method == 'iseed':
            self.iseed_unlocker()
          
        print('Finished unlocking , Check if {} is unlocked'.format(target))
        if itp.isunlocked(unlock_chk_tap):
            print ("{} is unlocked".format(product))
            return True
        else:
            return False
        
    def ferum_unlocker(self):
        try:
            product = self.config.get_config_value('general','PRODUCT')
            unlock_chk_tap =self.config.get_config_value('unlock','UNLOCK_CHECK_TAP')
            print("Using ferum to unlock part")
            from users.jlim9 import ferum
            ferum.open()
        except Exception as ex:
            print('Failed to unlock part using ferum {}'.format(ex.message))
    
    def metal_key_unlocker(self):
        print("Metal key unlock not implemented")
        
    def iseed_unlocker(self):
        print("iseed unlock not implemented")
                