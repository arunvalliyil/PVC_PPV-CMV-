
from . import supported_ips as ip
from .status import Status


class ANRStatus(Status):
    
    handled_ip = ip.ANR

    tile0_identifier = 'U3'
    tile1_identifier = 'U4'
    
    def __init__(self, instance):
        self.instance = instance

    def get_ip_status(self):
        return_val={}
        sv = self.instance.get_python_sv_instance()
        return_val["anrpresent"] = self.check_all_anrs_present(sv)
        for tile in range(len(sv.gfxcard0.tiles)):
            return_val['ANR_Count_Tile{}'.format(tile)] = self.find_anrs(tile,sv)
            return_val['ANR_TrainStatus_Tile{}'.format(tile)] = self.verify_training_status(tile, sv)
        return return_val
        
    def find_anrs(self, tile, sv):
        return len(sv.gfxcard0.anr.tiles)
    
    def verify_training_status(self, tile, sv):
        ###ANR should be at 0xd
        if tile == 0:
            if ANRStatus.grayToDec(sv.gfxcard0.anr.tile0.taps.anr_cltap0.dinit.gray_enc_cs) == 0xd:
                return "Trained"
        elif tile == 1:
            if ANRStatus.grayToDec(sv.gfxcard0.anr.tile1.taps.anr_cltap0.dinit.gray_enc_cs) == 0xd:
                return "Trained"
        return "Not Trained"
    
    def check_all_anrs_present(self, sv):
        anr_present = []
        tile_count = len(sv.gfxcards.tiles)
        anr_present = sv.gfxcard0.tiles.uncore.punit.ptpcioregs.gt0_punit_mmio_cr_poc_straps_obs.cd_present
        available_anr_count = list(filter(lambda x: (x == 1), anr_present))  
        tile_count = tile_count - len(available_anr_count)
        return tile_count == 0
        
    def grayToDec(num):
        mask = num
        while mask:
            mask >>= 1
            num ^= mask
        return num



    def read_ult(self, identifier_list = None):
        print("Reading ANR Die ULT info")
        import toolext.bootscript.toolbox.fuse_utils as fuse_utils
        return_val = {}
        sv = self.instance.get_python_sv_instance()
        sv.gfxcards.anr.tiles.fuses.load_fuse_ram()
        if not identifier_list:
            identifier = []
            identifier.append(ANRStatus.tile0_identifier)
            if len(sv.gfxcard0.tiles)>1:
                identifier.append(ANRStatus.tile1_identifier)
        try:
            if ANRStatus.tile0_identifier in identifier:
                fuse = fuse_utils.decodeult_tsmc(sv.gfxcard0.anr.tile0.fuses.dfxagg.ult_fuse)
                # work around until fusion fixes the ult length issue
                if len(fuse.split('_')[0])>8:
                    fuse = fuse.replace(fuse.split('_')[0],fuse.split('_')[0][:-2])

                return_val[ANRStatus.tile0_identifier] = fuse
            
            if ANRStatus.tile1_identifier in identifier:
                fuse = fuse_utils.decodeult_tsmc(sv.gfxcard0.anr.tile1.fuses.dfxagg.ult_fuse)
                if len(fuse.split('_')[0])>8:
                    fuse = fuse.replace(fuse.split('_')[0],fuse.split('_')[0][:-2])
                return_val[ANRStatus.tile1_identifier]  = fuse
        except Exception as e:
            print('Failed to read ANR Die ULT {}'.format(e))
        
        return return_val
        

