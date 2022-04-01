
from . import supported_ips as ip
from .status import Status

class GTStatus(Status):
    
    handled_ip = ip.GT

    def __init__(self, instance):
        self.instance = instance
    
    def target_tile(self, tileid =0):
        global _soc
        global _gt
        if (tileid == 0):
            _soc= gfxcard0.tile0
            _gt = _soc.gfx.gtgp
        
        elif(tileid == 1):
            _soc= gfxcard0.tile1
            _gt = _soc.gfx.gtgp
        

    def get_ip_status(self):
        return_val={}
        sv = self.instance.get_python_sv_instance()
        return_val['Tile_Count'] = self.get_tile_count(sv)
        for tile in range(0, return_val['Tile_Count']):
            return_val['GT_tile{}_Status'.format(tile)] = self.get_gt_status(tile, sv)
            return_val['Enabled_tile{}_EU'.format(tile)] = self.get_enabled_eu(tile, sv)
            return_val['Enabled_tile{}_DSS'.format(tile)] = self.get_enabled_dss(tile, sv)
            return_val['Enabled__tile{}_VDBox'.format(tile)] = self.get_enabled_vdbox(tile, sv)
        return return_val
    
    
    def get_tile_count(self, sv):
        print("Getting tile count")
        global tile_count
        tile_count = len(sv.gfxcard0.tiles)
        return tile_count
    
    def get_gt_status(self, tile, sv):
        print("Getting GT status for tile {}".format(tile))
        core_state = sv.gfxcard0.tiles.uncore.punit.ptpcfsms_gpsb.gt0_core_status.core_state
        if core_state[tile] != 0X0:
            return "GT not up"
        else:
            return "GT up"
        
        return return_val
    
    def get_enabled_eu(self, tile, sv):
        eu_enabled = sv.gfxcard0.tiles.gfx.gtgp.mirror_eu_enable.eu_enable
        return eu_enabled[tile]

    def get_enabled_dss(self, tile, sv):
        dss_enabled = sv.gfxcard0.tiles.gfx.gtgp.mirror_gt_compute_dss_enable.gt_compute_dss_enable
        return dss_enabled[tile]

    def get_enabled_vdbox(self, tile, sv):
        enabled_vd_box = sv.gfxcard0.tiles.gfx.gtgp.mirror_gt_vebox_vdbox_en.gt_vdbox_enable
        return enabled_vd_box[tile]
	
    def read_ult(self, identifier_list = None):
        print("Reading ULT info")
        return_val = {}
        return return_val     
    
    def verify_gt_up(self):
        sv = self.instance.get_python_sv_instance()
        for tile in range(0, self.get_tile_count(sv)):
            if self.get_gt_status(tile, sv) == 'GT not up':
                return False
        return True

    def gt_reset_done(self):
        return_val = True
        sv = self.instance.get_python_sv_instance()
        tile_count = self.get_tile_count(sv)
        for info in sv.gfxcard0.tiles.gfx.gtgp.instdone_1:
            if info != 0xfffffffe:
                return False
        return True

