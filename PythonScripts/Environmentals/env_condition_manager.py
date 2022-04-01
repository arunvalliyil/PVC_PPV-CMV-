from .frequency_condition_manager import FrequencyConditionManager
from .voltage_condition_manager import VoltageConditionManager
from .string_env_condition_manage import StringEnvironmentCondition

class EnvironmentConditionManager():
    
    def __init__(self):
        print("Initializing environmental condition manager")
        self.condition_handlers = [VoltageConditionManager(), FrequencyConditionManager(), StringEnvironmentCondition()]
    
    def set_condition(self, condition_name, value):
        print("Setting condition {} with value {}".format(condition_name, value))
        handler = self._identify_handler(condition_name)
        handler.set_condition(condition_name, value)
    
    def read_condition_set_point(self, condition_name):
        print("Reading condition set point {}".format(condition_name))
        handler = self._identify_handler(condition_name)
        return handler.read_condition(condition_name)
     
    def read_condition_measured(self, condition_name):
        print("Reading condition measured {}".format(condition_name))
        handler = self._identify_handler(condition_name)
        return handler.read_condition(condition_name)
    
    def _identify_handler(self, condition_name):
        return_value = None
        for handler in self.condition_handlers:
            if handler.is_condition_supported(condition_name):
                return_value = handler
                break
        
        if not return_value:
            raise Exception("Could not handle condition {}".format(condition_name))
        
        return return_value
    
    