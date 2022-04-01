
from . import supported_ips as ip
from .status import Status

class HBMStatus(Status):
    
    handled_ip = ip.HBM
    supported_HBMS = {
        "Tile0":
        {
            "U8":"HBM0",
            "U7":"HBM1",
            "U6":"HBM2",
            "U5":"HBM3" 
        },
        "Tile1":
        {
            "U9":"HBM4",
            "U10":"HBM5",
            "U11":"HBM6",
            "U12":"HBM7" 
        }
    }

    def __init__(self, instance):
        self.instance = instance

    def get_ip_status(self):
        print("Collecting HBM status")
        return_val = {}
        try:
            import pontevecchio.ev.hbmio.hbm.hbm_pll as pll
            import pontevecchio.fv.mem.pvcMcUtils as mcu
            import pontevecchio.fv.mem.check_hbm_training as c
            from namednodes import sv
            return_val['Manufacturer'] = mcu.get_hbm_manufacturer(0,0)
            return_val['HBM_Speed'] = self.get_hbm_speed()
            return_val['StackHeight'] = mcu.get_hbm_height()

            hbm_trained = c.main(check_ieee1500=False, silent=True)
            for tile in range(len(sv.gfxcard0.tiles)):
                for hbm in range(len(eval('sv.gfxcard0.tile{}.uncore.memss.hbms'.format(tile)))):
                    trained_speed = str(pll.hbm_pllratio(gfxcard=0, tile=tile, hbm=hbm))
                    hbm_instance = f"T{tile}H{hbm}"
                    if hbm_trained[hbm_instance] == "PASS":
                        return_val[hbm_instance] = trained_speed
        except Exception as e:
            print("Exception during HBM Screen: {}".format(e))

        return return_val

    def get_hbm_speed(self):
        print("Collecting HBM training speed")
        return_val = 0
        try:
            import pontevecchio.ev.hbmio.hbm.hbm_pll as pll
            return_val = str(pll.hbm_pllratio())
        except Exception as ex:
            print("Faile to read hbm speed {}".format(ex))
        return return_val

    def get_hbm_count(self, tile):
        print("Collecting enable HBM count")
        return_val = 0
        try:
            import pontevecchio.fv.mem.check_hbm_training as c
            hbm_trained = c.main(check_ieee1500=False, silent=True)
            return_val = list(hbm_trained.values()).count('PASS')   
        except Exception as ex:
            print("Failed to read hbm count {}".format(ex))
        return return_val
    
    def read_ult(self, identifier_list = None):
        print("Reading HBM ULT info")
        return_val = {}
        return return_val         

