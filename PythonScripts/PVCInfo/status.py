from abc import ABC, abstractmethod

class Status(ABC):
    
    handled_ip =''

    def __init__(self, instance):
        self.instance = instance
    
    @abstractmethod
    def get_ip_status(self):
        pass

    @abstractmethod
    def read_ult(self,identifier_list = None):
        pass