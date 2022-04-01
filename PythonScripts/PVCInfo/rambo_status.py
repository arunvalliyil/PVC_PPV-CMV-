
from . import supported_ips as ip
from .status import Status
from debug.domains.fuse import fuse_utils

class RamboStatus(Status):
    
    handled_ip = ip.RAMBO

    supported_Rambos = {
        "Tile0":
        {
            "U1.U12":"RAMBO0_0",
            "U1.U15":"RAMBO0_1",
            "U1.U18":"RAMBO0_2",
            "U1.U21":"RAMBO0_3" 
        },
        "Tile1":
        {
            "U2.U12":"RAMBO1_0",
            "U2.U15":"RAMBO1_1",
            "U2.U18":"RAMBO1_2",
            "U2.U21":"RAMBO1_3" 
        }
    }
    
    def __init__(self, instance):
        self.instance = instance

    def get_ip_status(self):
        return_val={}
        return return_val
        
    def find_rambos(self):
        # write code to get all active RAMBOS here
        return [1,2]
    
    def read_ult(self, identifier_list = None):
        print("NO ULT read for Rambo")
        return_val = {}
        return return_val
        

