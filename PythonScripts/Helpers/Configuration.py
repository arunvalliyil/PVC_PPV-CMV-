import configparser
import enum
import os
from pathlib import Path

class Configuration(object):

    _instance = None
    
    @staticmethod
    def getInstance():
        if Configuration._instance ==  None:
            Configuration._instance = Configuration()
        return Configuration._instance
    
    def __init__(self):
        if Configuration._instance !=None:
            raise Exception("Singleton class use getInstance to Create an instance.")
        else:
            print("Initializeing Configuration")
            self.reload_configuration()
            Configuration._instance = self
        

    def reload_configuration(self, config_file_path = None):
        self.config = configparser.ConfigParser()
        if not config_file_path:
            current_path = Path(os.path.realpath(__file__))
            config_file_path = os.path.join(current_path.parent,'Configuration.ini')

        self.config.read(config_file_path)
        print("loaded configuration from {}".format(config_file_path))

    def get_config_value(self,section, config_key):
        return self.config[section][config_key]
