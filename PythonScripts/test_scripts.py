import json
from Helpers.Configuration import Configuration
from Environmentals.env_condition_cache_manager import EnvironmentConditionCacheManager

class ExecuteTestRun():

    def __init__(self):
        print("Instantiating tester scripts")
        self.config = Configuration.getInstance()
        self.cache = EnvironmentConditionCacheManager()


    def runshmoo(self):
        print("Running shmoo test")
        cache_data = self.cache.read_environment_condition_cache()
        current_voltage = cache_data['VOLTAGE_OVERRIDE']
        limit_voltage = self.read_limit()
        if int(limit_voltage['VCCEU']) >0:
            if current_voltage['VCCEU']< limit_voltage['VCCEU']:
                return "Failed"
            else:
                return "Passed"
        
        if int(limit_voltage['VCCBASE']) >0:
            if current_voltage['VCCBASE']< limit_voltage['VCCBASE']:
                return "Failed"
            else:
                return "Passed"
        


    
    def read_limit(self):
        if os.path.isfile(self.cache_path):
            with open("vmin_failurepoint_flag.txt", 'r') as reader:
                return_val = json.loads(reader.read())
        else:
            return EnvironmentConditionCache()

