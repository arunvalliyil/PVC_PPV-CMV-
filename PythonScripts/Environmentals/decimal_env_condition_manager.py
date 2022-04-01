
import sys
from abc import ABC, abstractmethod

class DecimalEnvironmentCondition(ABC):
    
    def __init__(self):
        self.fpd_ranges = {}
        return
    
    @abstractmethod
    def get_supported_conditions(self):
        pass
    
    @abstractmethod
    def execute_read_condition(self):
        pass
    
    @abstractmethod
    def execute_set_condition(self):
        pass
    
    def read_condition(self, name):
        if self.is_condition_supported(name):
            return self.execute_read_condition(name)
        return False
    
    def set_condition(self, name, value):
        if self.is_condition_supported(name):
            return self.execute_set_condition(name, value)
        return False
    
    def is_condition_supported(self, condition_name):
        return condition_name in self.get_supported_conditions()