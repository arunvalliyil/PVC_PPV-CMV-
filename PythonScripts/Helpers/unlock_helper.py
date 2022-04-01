import sys
from Helpers.instances import InstanceFactory


class UnlockHelper():
    
    def __init__(self):
        self.api = InstanceFactory.getInstance().get_fusion_instance()
        pass

    def do_unlock(self):
        itp = InstanceFactory.getInstance().get_itp_instance()
        part_id = self.extract_part_id(itp)
        if '0000000000000000' not in part_id:
            print("Performing iSeed Unlock!!!")
            iseed_hex = self.api.get_iseed_key('PVC',"0x{}".format(part_id),'PVC_RED_PROD',"U1.U1")
            iseed_key = iseed_hex[2:]
            if not self.do_iseed_unlock(iseed_key, itp):
                raise ("Failed to unlock the part.")
        else:
            do_metal_unlock()

    def do_metal_unlock(self):
        print("Executing Metal Unlock")
        sys.path.append(r'C:\STHI\Fusion\ptm')
        import pontem as m
        m.unlock()
        itp = InstanceFactory.getInstance().get_itp_instance()
        print("Part is unlocked ? {}".format(itp.isunlocked('PVC_CLTAP0')))
        if not itp.isunlocked('PVC_CLTAP0'):
            raise("Failed Metal unlock.")
        pass
    
    def do_iseed_unlock(self, iseed_key, itp):
        print("Executing Iseed unlock")
        sv = InstanceFactory.getInstance().get_python_sv_instance()
        tap = itp.devs.pvc_agg0
        tap.irdrscan(0x30,32)

        ##Shift in the passcode to the Payload registers.
        tap.irdrscan(0x50,32,int("0x{}".format(iseed_key[24:32]),16))
        tap.irdrscan(0x54,32,int("0x{}".format(iseed_key[16:24]),16))
        tap.irdrscan(0x58,32,int("0x{}".format(iseed_key[8:16]),16))
        tap.irdrscan(0x5C,32,int("0x{}".format(iseed_key[0:8]),16))

        personality = 0
 
        ##Set tap_ctrl to perform the unlock.
        tap.irdrscan(0x40, 32, personality);##Write the pc_pers_select=tap_ctrl[6:4]
        tap.irdrscan(0x40, 32, 0x8)
 
        ##Check if the status_0 reflects it.
        tap.irdrscan(0x30,32)##Check policy_output=status_0[23:20]==0x4(Intel Unlocked)
        print("Policy output is :{}".format(sv.gfxcard0.tile0.taps.pvc_agg0.status_0.policy_output))
        return sv.gfxcard0.tile0.taps.pvc_agg0.status_0.policy_output == 0x4
    
    def extract_part_id(self, itp):
        tap = itp.devs.pvc_agg0
        unique_id_63_32 = tap.irdrscan(0x74,32)
        unique_id_31_0 = tap.irdrscan(0x70,32)
        unique_part_id = str(unique_id_63_32)[8:] + str(unique_id_31_0)[8:]
        return unique_part_id