
from . import supported_ips as ip
from .status import Status

class PCIEStatus(Status):
    
    handled_ip = ip.PCIE

    def __init__(self, instance):
        self.instance = instance
    
    def get_ip_status(self):
        return_val = {}
        return_val['LinkSpeed'] = self.get_link_train_speed()
        return_val['TrainError'] = self.get_training_error_details()
        return_val['LinkWidth'] = self.get_link_width()
        return_val['LinkState'] = self.get_link_state()

        return return_val
        
    def get_training_error_details(self):
        return ""
    
    def get_link_width(self):
        sv = self.instance.get_python_sv_instance()
        return sv.gfxcard0.tile0.uncore.pcie_swu.linksts.nlw
    
    def get_link_train_speed(self):
        sv = self.instance.get_python_sv_instance()
        return sv.gfxcard0.tile0.uncore.pcie_swu.linksts.cls 
    
    def read_ult(self, identifier_list = None):
        print("NO ULT read for PCIE")
        return_val = {}
        return return_val

    def get_link_state(self):
        sv = self.instance.get_python_sv_instance()
        return sv.gfxcard0.tile0.uncore.pcie_swu.ltssmsmsts.ltssmstatemain