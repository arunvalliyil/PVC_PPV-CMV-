from Helpers.Configuration import Configuration
from .boot_helpers import BootHelper
from Helpers.instances import InstanceFactory
from Helpers.mid_target_identifier import MidTargetIdentifier
from Helpers.unlock_helper import UnlockHelper
from Helpers.fuse_override_generator import FuseOverrideGenerator
from Environmentals.env_condition_cache_manager import EnvironmentConditionCache 
from Environmentals.env_condition_cache_manager import EnvironmentConditionCacheManager
import time, sys

class FusedUnitHandler():

    def __init__(self):
        self.Configuration = Configuration.getInstance()
        self.BootHelper = BootHelper()
        self.instance = InstanceFactory.getInstance()
        self.identifier = MidTargetIdentifier()
        self.cache_manager = EnvironmentConditionCacheManager()
        pass

    def boot_unit(self, ispolling_bios = False):
        sv = self.instance.get_python_sv_instance()
        itp = self.instance.get_itp_instance()
        api = self.instance.get_fusion_instance()
        self.DEBUGPORT_CARD =  InstanceFactory.getInstance().identify_pvc_port()
        self.DEBUGPORT_HOST =  InstanceFactory.getInstance().identify_mid_target_port()
        print("DEBUGPORT_CARD is {}; DEBUGPORT_HOST is {}".format(self.DEBUGPORT_CARD, self.DEBUGPORT_HOST))

        if not ispolling_bios :
            if self.is_WC_mid_target():
                print("Booting a fused unit on WC platform")
                self.boot_fused_unit_WC(itp,sv, api)
            else:
                print("Booting a fused unit on AC platform")
                self.boot_fused_unit_AC(itp, sv)
        else:
            print("Implement boot sequence for polling bios")
        return api.get_processor_infos()[0].visual_id.Id
    
    def is_WC_mid_target(self):
        return self.identifier.identify_mid_target() == 'WC'

    def boot_fused_unit_AC(self, itp, sv):
        cache = self.cache_manager.read_environment_condition_cache()
        
        print("SPR reset break asserted.")
        itp.breaks.reset = 1
        print("Hold hook asserted for Debug port {}".format(self.DEBUGPORT_CARD))
        itp.holdhook(self.DEBUGPORT_CARD, 3, 1)
        print("Power Off platform waiting for 10 sec before power on")
        self.instance.get_power_control().target_power_off_control('')
        time.sleep(10)
        print("Powering on platform")
        InstanceFactory.getInstance().get_power_control().target_power_on_control()
        self.BootHelper.wait_for_power_on(itp)
        self.BootHelper.wait_for_reset_break(itp)
        itp.go()
        print("performing unlock")
        UnlockHelper().do_unlock()
        print("Propagating fuse information")
        sv.gfxcard0.tiles.taps.pvc_agg0.tap_ctrl.resume0 = 1
        sv.gfxcard0.anr.tiles.taps.anr_dfxagg_pic60.tap_ctrl.resume0 = 1
        self.override_fuse(sv)
        sv.gfxcard0.tiles.taps.pvc_agg0.tap_ctrl.resume1 = 1
        sv.gfxcard0.anr.tiles.taps.anr_dfxagg_pic60.tap_ctrl.resume1 = 1

        print("Removing holdhook to continue booting")
        itp.go()
        itp.holdhook(self.DEBUGPORT_HOST, 3, 0)
        itp.holdhook(self.DEBUGPORT_CARD, 3, 0)
        itp.breaks.reset = 0
        print("Finished AC boot sequence to EFI now wait for EFI boot.")
        return ''

    def boot_fused_unit_WC(self, itp, sv,api):
        # Power OFF Stage
        itp.breaks.reset = 1
        print("Hold hook asserted for Debug port {}".format(self.DEBUGPORT_CARD))
        itp.holdhook(self.DEBUGPORT_CARD, 3, 1)
        print("Waiting for pulse power good")
        self.instance.get_power_control().target_power_off_control('')
        self.BootHelper.wait_for_host_power_off(itp)
        self.instance.get_power_control().target_power_on_control()
        
        self.BootHelper.wait_for_power_on(itp)  
        self.BootHelper.wait_for_itp_refresh(itp)
        print("Hold hook status is {}".format(itp.hookstatus(self.DEBUGPORT_CARD, 3)))
        self.BootHelper.wait_for_reset_break(itp)
        itp.go()
        print("Waiting for second reset break")
        self.BootHelper.wait_for_reset_break(itp)
        self.BootHelper.stall_bios_with_reset_break(itp, sv)
        self.BootHelper.wait_for_bios_breakpoint(sv)
        
        for tile in sv.gfxcard0.tiles:
            tile.taps.getbypath(tile.taps.search("tap_ctrl")[0]).enable_dam_hw = 0x1
        print("performing unlock")
        UnlockHelper().do_unlock()
        sv.gfxcard0.tiles.taps.pvc_agg0.tap_ctrl.resume0 = 1
        sv.gfxcard0.anr.tiles.taps.anr_dfxagg_pic60.tap_ctrl.resume0 = 1
        self.override_fuse(sv)
        sv.gfxcard0.tiles.taps.pvc_agg0.tap_ctrl.resume1 = 1
        sv.gfxcard0.anr.tiles.taps.anr_dfxagg_pic60.tap_ctrl.resume1 = 1
        itp.holdhook(self.DEBUGPORT_CARD, 3, 0)
        itp.holdhook(self.DEBUGPORT_HOST, 3, 0)
        sv.socket.socket0.uncore.ubox.ncdecs.biosscratchpad6_cfg[31:16] = 0
        print("Finished WC boot sequence to EFI now wait for EFI boot.")
        return ''
    
    def override_fuse(self, sv):
        generator = FuseOverrideGenerator()
        fuses_to_set = generator.generate_fuse_override()
        sv.gfxcard0.tiles.fuses.load_fuse_ram()
        print("Fuse ram loaded")

        for fuse in fuses_to_set['All']:
            print(fuse)
            print("sv.gfxcard0.tiles.fuses.{}".format(fuse))
            exec("sv.gfxcard0.tiles.fuses.{}".format(fuse))
        for fuse in fuses_to_set['0']:
            exec("sv.gfxcard0.tile0.fuses.{}".format(fuse))
        for fuse in fuses_to_set['1']:
            exec("sv.gfxcard0.tile1.fuses.{}".format(fuse))
        
        sv.gfxcard0.tiles.fuses.reserved.socfusegen_reserved_lockoutid_intelhvm_row_1_bit_0=0x0

        # Flush to fuse RAM
        print("Writing to Fuse RAM...")
        sv.gfxcard0.tiles.fuses.flush_fuse_ram()
        sv.gfxcard0.tiles.fuses.reserved.socfusegen_reserved_lockoutid_intelhvm_row_1_bit_0=0xFFFFFFFF
        sv.gfxcard0.tiles.fuses.flush_fuse_ram(only_deltas=True)
        print('Reparsing Heap')
        for tile in sv.gfxcard0.tiles:
            tile.fuses.heap_reparse()
        print("All fuses updated for the boot and fuse ram flushed.")
