
from frequency_manager import FrequencyManager
from voltage_manager import VoltageManager

class DeviceEnvConditionHandler():

    def __init__(self):
        self.handlers = [FrequencyManager(), VoltageManager()]
    

    def read_device_info(self, condition_name):
        handler = self.identify_handler(condition_name)
        if handler:
            return handler.read_device_condition(condition_name)
    
    def set_device_info(self, condition_name, value):
        handler = self.identify_handler(condition_name)
        if handler:
            return handler.set_device_condition(condition_name, value)
    
    def verify_device_info(self, condition_name, expected_value):
        print("Verifying if device condition {} is with expected value {}".format(condition_name, expected_value))
        handler = self.identify_handler(condition_name)
        if handler:
            return handler.verify_device_info(condition_name, expected_value)
        return False
    
    def identify_handler(self, condition_name):
        for handler in self.handlers:
            if condition_name in handler.supported_conditions:
                return handler
        return