import supported_boot_stages as stage
import process_fle, datetime
from Helpers.Configuration import Configuration
from Helpers.unit_identity_updater import UnitIdentityUpdater
from Helpers.instances import InstanceFactory
from Environmentals.env_condition_cache_manager import EnvironmentConditionCacheManager
from Environmentals.env_condition_cache_manager import EnvironmentConditionCache
from FusionBaseClass.boot_stage_controller import BootStageController
from Helpers.fuse_override_generator import FuseOverrideGenerator
from Helpers.ituff_helper import ItuffTokenHelper
from Helpers.device_id_extractor import DeviceIDExtractor
from Helpers.fused_unit_handler import FusedUnitHandler
from PVCInfo.device_manager import DeviceManager
from toolext.bootscript import boot as b
from Helpers.fused_unit_handler import FusedUnitHandler
from Helpers.Profilers.pvc_profiler import PVCProfiler
from Helpers.unlock_helper import UnlockHelper
import supported_modes as modes
import os.path
import time, csv,os
import threading

class FuseBreakController(BootStageController):
    
    Stage_Handled = stage.FuseBreak

    def __init__(self):
        self.WAIT_TIME = 30
        self.DELAY = 1
        self.DEBUGPORT_HOST = 1
        self.DEBUGPORT_CARD = 0
        self.known_aurora_skews = ['QZLK','QZ1A','QZ1G','QZ0D','QZ0F','QZND','QZNF','QZPK','QZPK','QZPM','QZ0U','QZ0W']
        self.installation_mode =  InstanceFactory.getInstance().get_installation_mode()
        self.env_manager = EnvironmentConditionCacheManager()

    def get_supported_next_stage(self):
        return [stage.EFIStage, stage.PowerOffStage]
    
    def is_in_boot_stage(self, boot_stage):
        return True
    
    def start_transition(self, from_stage, to_stage):
        if to_stage == stage.EFIStage:
            print("Transitioning to {} from {}".format(to_stage, from_stage))
            self.transition_to_efi(from_stage, to_stage)
            
            base_frequency = DeviceManager.getInstance().read_device_condition('base')
            compute = DeviceManager.getInstance().read_device_condition('compute')
            link = DeviceManager.getInstance().read_device_condition('link')
            #hbm = DeviceManager.getInstance().read_device_condition('hbm')
            #print("Unit booted to EFI with frequency base:{},compute:{}, hbm:{}, link:{}".format(base_frequency, compute,hbm,link))
            print("Unit booted to EFI with frequency base:{},compute:{}, link:{}".format(base_frequency, compute,link))

        elif to_stage == stage.PowerOffStage:
            print("Turning off target power")
            instance = InstanceFactory.getInstance()
            instance.get_power_control().target_power_off_control('')
    
    def extract_part_id(self, itp):
        tap = itp.devs.pvc_agg0
        unique_id_63_32 = tap.irdrscan(0x74,32)
        unique_id_31_0 = tap.irdrscan(0x70,32)
        unique_part_id = str(unique_id_63_32)[8:] +str(unique_id_31_0)[8:]
        return unique_part_id

    def boot_unfused_part(self, api):
        generator = FuseOverrideGenerator()
        fuses_to_set = generator.generate_fuse_override()

        tile_0_fuses = []
        tile_1_fuses = []
        if '0' in fuses_to_set:
            tile_0_fuses = fuses_to_set['0']
        if '1' in fuses_to_set:
            tile_1_fuses = fuses_to_set['1']
        
        current_mode = InstanceFactory.getInstance().get_installation_mode()
        is_boot_success = False
        visual_id = ''
        operation_code = api.lot_info.OperationCode
        qdf_value = api.lot_info.ProductID.Sspec
        recovery_opcode = Configuration.getInstance().get_config_value("DSSRecovery", "RECOVERY_OPCODE")

        if current_mode.lower() == "ppv":
            print("Calling boot script with fuse overrides for PPV")
            cache =  self.env_manager.read_environment_condition_cache()
            print("Executing regular boot script with no fuse override")
            
            if self.check_if_aurora_qdf(api):
                print("Found {} a valid aurora skew updaing dss en".format(qdf_value))
                dss_en_fuse = ['gt_gfx_gt_c0_r3.gtip_base_fuse_fuse_gt_compute_dss_en=0xffffffffffffffff']
                b.go(num_host_wr=1, hold_host_reset_break=True, fusestr = dss_en_fuse) #B1'
            else:
                b.go(num_host_wr=1, hold_host_reset_break=True, fusestr = fuse_to_set) #B1
            #b.go(num_host_wr=1, hold_host_reset_break=True, recipes=['user_custom.gt_driver_en_2t'])
            visual_id = b.boot_vars.VID
            
            screening_output= b.boot_vars.framework_vars.screenOutput
            try:
                screen_output = Configuration.getInstance().get_config_value('general','BOOTSCRIPT_OUTPUT')
                print("Caching screening output")
                with open(screen_output, 'w') as file:
                    file.write(str(screening_output))
            except Exception as e:
                print("Failed to cache screening output:- ".format())
        else:
            print("Calling boot script with fuse overrides for CMV")
            #b.go(sfo_ffr="18_00", fusestr = fuses_to_set['All'], sfo_qdf = 'QZMY')
            #b.go(sfo_ffr="18_00",sfo_qdf = 'QZMY',fusefiles=["Debug\HBM\samsung_8h_3p2.cfg"],fusestr = fuses_to_set['All'])
            #b.go(fusestr = fuses_to_set['All'])

            b.go(fusestr = fuses_to_set['All'],num_host_wr=1, hold_host_reset_break=True)
            import pontevecchio.utils.spi_access as spi
            spi.read_ifwi_version()
            visual_id = b.boot_vars.VID
            
        print( "Identified VID as {}".format(visual_id))
        UnitIdentityUpdater.getInstance().update_identifiers(visual_id)
        is_boot_success = b.boot_vars.framework_vars.marker.getPass()
        
        if not is_boot_success:
            cache = EnvironmentConditionCache()
            cache.BYPASS_ENABLED = True
            self.env_manager.update_environment_condition_cache(cache)
            print("Failed to boot part. Trying with Bypass enabled")
            raise Exception("Failed to boot the part {}".format(b.boot_vars.framework_vars.marker.getLastErrors()))
        return visual_id

    def update_meml3_info(self):
        print("Caching MEML3 information for the unit")
        cache = self.env_manager.read_environment_condition_cache()
        cache.MEML3["T0"] =  DeviceManager.getInstance().read_mem_l3(0)
        cache.MEML3["T1"] =  DeviceManager.getInstance().read_mem_l3(1)
        self.env_manager.update_environment_condition_cache(cache)
    
    def check_if_aurora_qdf(self, api):
        qdf_value = api.lot_info.ProductID.Sspec
        print("Detected QDF for current execution as {}".format(qdf_value))
        if qdf_value in self.known_aurora_skews:
            print("{} identified as a known Aurora QDF".format(qdf_value))
            return True
        return False
    
    def handle_aurora_qdf(self, api):
        if self.installation_mode == "CMV":
            return
        print("Handling aurora skew for PPV")
        if self.check_if_aurora_qdf(api):
            cache = self.env_manager.read_environment_condition_cache()
            tile_count = DeviceManager.getInstance().populated_tile_count()
            dss_to_set = {}
            for tile in range(tile_count):# enable all eus on both tiles
                dss_to_set[tile] = '0xffffffffffffffff'

            cache.DSS_OPTION = dss_to_set
            self.env_manager.update_environment_condition_cache(cache)

    def transition_to_efi(self, from_stage, to_stage):
        print("Initializing transition to {} from {}".format(from_stage, to_stage))
        sv = InstanceFactory.getInstance().get_python_sv_instance()
        itp = InstanceFactory.getInstance().get_itp_instance()
        itp.forcereconfig()
        sv.refresh()
        api = InstanceFactory.getInstance().get_fusion_instance()
        self.handle_aurora_qdf(api)
        part_id = self.extract_part_id(itp)
        print(part_id)
        visual_id = ''

        if '0000000000000000' not in part_id:
            print("Booting a fused unit")
            visual_id = FusedUnitHandler().boot_unit()
        else:
            print("Booting unfused unit")
            visual_id = self.boot_unfused_part(api)
        
        sv.gfxcard0.tiles.taps.pvc_gdtu0.gdtutapchicken.force_non_gdt_gdtu_tap_rst = 1
        sv.gfxcard0.tiles.taps.pvc_gdtu0.gdtutapchicken.fast_tap_en = 1
        
        time.sleep(5)
        PVCProfiler.getInstance().StartProfiling(False)
        print( "Identified VID as {}".format(visual_id))
        UnitIdentityUpdater.getInstance().update_identifiers(visual_id)
        
        serial_port = InstanceFactory.getInstance().get_fpd_utilities().get_marionette_serial_port()
        api.marionette.set_serial(serial_port)
        
        starttime = datetime.datetime.now()
        while not (api.marionette.get_connected_os() == "EFI"):
            time.sleep(1)
            if (datetime.datetime.now() - starttime) > datetime.timedelta(milliseconds=300000):
                raise RuntimeError("Timed out while waiting for system to go EFI marionette %s" % (to_stage))
        print("Reached EFI Stage setting all registers for runnnig EFI tests")
        DeviceIDExtractor().cache_device_id()
        #qdf_value = b.boot_vars.SFO_PKG.qdf
        base_frequency = DeviceManager.getInstance().read_device_condition('base')
        cache = self.env_manager.read_environment_condition_cache()
        cache.BOOT_FREQUENCY = base_frequency
        #cache.TESTED_QDF = qdf_value
        self.env_manager.update_environment_condition_cache(cache)

        #hgea print("Setting machinecheck 1 on ICX")
        #hgea itp.halt()
        #hgea itp.breaks.machinecheck=1
        #hgea itp.go()
        self.update_meml3_info()

        sv.gfxcard0.tiles.uncore.sgunit.pcicmd_pci.bme =1 
        sv.gfxcard0.tiles.uncore.sgunit.pcicmd_pci.mae =1
            
        sv.gfxcard0.tiles.gfx.gtgp.force_wake 
        sv.gfxcard0.tiles.gfx.gtgp.showsearch("instdone")
            
        #Blitter issue WA
        sv.gfxcard0.tiles.gfx.gtgp.bcs_ecoskpd_bcsunit_be_0=0xE100A100
            
        #Disable ATS feature for SRIOV
        sv.gfxcard0.tile0.uncore.sgunit.ats_ctrl_pci.ae=0
          
        #Check for viral
        print("Checking for Viral status registers")
        print(sv.gfxcard0.tiles.uncore.pcode_io.io_firmware_mca_command)
        
        #MC
        #print("removed MC imc0_mc_status")
        #print(sv.gfxcard0.tiles.uncore.memss.hbm0.ch0.pc0.imc0_mc_status)
    
        #Punit
        print("Punit")
        print(sv.gfxcard0.tiles.uncore.pcode_io.io_mca_err_src_log)
        print(sv.gfxcard0.tiles.uncore.pcode_io.io_firmware_mca_command)
    
        #MDFI
        print("MDFI")
        print(sv.gfxcard0.tiles.uncore.mdfi.t2t.mdfi_ctrl0.ecc_err_status_reg)
        print(sv.gfxcard0.tiles.uncore.mdfi.t2t.mdfi_ctrl0.error_status)
        print(sv.gfxcard0.tiles.uncore.mdfi.t2c.mdfi_ctrl1.ecc_err_status_reg)
        print(sv.gfxcard0.tiles.uncore.mdfi.t2c.mdfi_ctrl1.error_status)
    
        #ANR
        print("ANR")
        print(sv.gfxcard0.anr.tiles.anr_tpm0.tpm_err_sts)
        print(sv.gfxcard0.anr.tiles.anr_brg.csrs0.brg_mbe_tpmegrq_err)        
            
        #Disable ATS feature for SRIOV
        print("VCCIO voltage")
        print(sv.gfxcard0.tile0.fuses.punit.pcode_initial_wp_active_voltage_iio_domain1)
         
        #print("PCIe link training status")
        import fv.PCIe.EIPPCIeStatus as eip
        eip.iouLinkStatus()

        return True

    def print_frequency(self, delay):
        while True:
            sv = InstanceFactory.getInstance().get_python_sv_instance()
            print("GT Frequency  for tile 0 is {}Mhz".format(sv.gfxcard0.tile0.gfx.gtgp.rp_status0.current_gfx_freq*100/6))
            tile_count = DeviceManager.getInstance().populated_tile_count()
            if tile_count > 1:
                print("GT Frequency  for tile 1 is {}Mhz".format(sv.gfxcard0.tile1.gfx.gtgp.rp_status0.current_gfx_freq*100/6))
            time.sleep(delay)