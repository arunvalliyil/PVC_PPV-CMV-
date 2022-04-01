
from . import supported_ips as ip
from .status import Status
import sys
sys.path.append(r'C:\PythonSV\pontevecchio')

class BASEDieStatus(Status):
    
    handled_ip = ip.BASE

    tile0_identifier = 'U1.U1'
    tile1_identifier = 'U2.U1'

    def __init__(self, instance):
        self.instance = instance
    
    def get_ip_status(self):
        return_val={}
        return return_val

    def read_ult(self, identifier_list = None):
        print("Reading Base Die ULT info")
        from pontevecchio.debug.domains.fuse import fuse_utils
        return_val = {}
        sv = self.instance.get_python_sv_instance()
        if not identifier_list:
            identifier = []
            identifier.append(BASEDieStatus.tile0_identifier)
            if len(sv.gfxcard0.tiles)>1:
                identifier.append(BASEDieStatus.tile1_identifier)
        try:
            print("loading fuse ram to refresh the sv fuse info")
            sv.gfxcards.tiles.fuses.load_fuse_ram()
            print("loaded fuse ram to refresh ")
            if BASEDieStatus.tile0_identifier in identifier:
                return_val[BASEDieStatus.tile0_identifier] = fuse_utils.decodeult(sv.gfxcard0.tile0.fuses.dfxagg.ult_fuse)
                print(return_val[BASEDieStatus.tile0_identifier])
            
            if BASEDieStatus.tile1_identifier in identifier:
                return_val[BASEDieStatus.tile1_identifier]  = fuse_utils.decodeult(sv.gfxcard0.tile1.fuses.dfxagg.ult_fuse)
                print(return_val[BASEDieStatus.tile1_identifier])
        except Exception as e:
            print('Failed to read Base Die ULT {}'.format(e))
        
        return return_val
        
