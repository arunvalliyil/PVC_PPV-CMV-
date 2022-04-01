import os,sys,json
from pathlib import Path
from Helpers.mode_identifier import ModeIdentifier
dir_path = os.path.dirname(os.path.realpath(__file__))
parent = Path(dir_path).parent
sys.path.append(os.path.join(parent, 'Environmentals'))
from env_condition_cache_manager import EnvironmentConditionCacheManager
from PVCInfo.device_manager import DeviceManager

class FuseOverrideGenerator():
    
    max_itd_temp = 125
    
    def __init__(self):
        print("init")
        self.device_manager = DeviceManager.getInstance()
        self.mode = ModeIdentifier.getInstance()
        self.cache_manager = EnvironmentConditionCacheManager()
        
    def generate_fuse_override(self, isaurora = False):
        print('generating fuse files for set condition')
        return_val = {}
        return_val['All'] = []
        return_val['1'] = []
        return_val['0'] = []
        
        set_frequency = 0 # set to a default value. Skip fuse override for frequency when 0

        cache = self.cache_manager.read_environment_condition_cache()
        set_fuse_overrides = []
        set_tile0_fuse = []
        set_tile1_fuse = []
        # this code is to add clock compensation fuses until they are integrated with fuse release
     
        if cache.TARGETOS.upper() == "EFI":
            print("Deteced boot to EFI adding specific fuses for EFI test execution")
            #set_fuse_overrides.append('gt_gfx_gt_c0_r3.gtip_base_fuse_fuse_gt_auth_bypass = 0x1')
            #set_fuse_overrides.append('gt_gfx_gt_c0_r3.gtip_base_fuse_fuse_gt_huc_auth_bypass = 0x1')
            #set_fuse_overrides.append('gt_gfx_gt_c0_r3.gtip_base_fuse_fuse_gt_guc_privilige = 0x1')
        elif cache.TARGETOS.upper() =='LINUX':
            print("Adding Linux specific fuses that are needed for PVC")

        dss_fuse = self.calculate_dss_fuses(cache)
        if '1' in dss_fuse:
            set_tile1_fuse.append(dss_fuse['1'])
        if '0' in dss_fuse:
            set_tile0_fuse.append(dss_fuse['0'])
        
        print("Extracting fuse strings for setting ratio")
        for domain in cache.SET_FREQUENCY:
            set_frequency = int(cache.SET_FREQUENCY[domain])
            print("Setting ratio for domain {} with frequency {}".format(domain, set_frequency))
            freq_to_set = int(set_frequency/50)
            if 'COMPUTE' in domain.upper() or 'BASE' in domain.upper():
                set_fuse_overrides.append('punit.pcode_gt_p0_ratio_systolic={}'.format(freq_to_set))
                set_fuse_overrides.append('punit.pcode_gt_p0_ratio_compute={}'.format(freq_to_set))

                set_fuse_overrides.append('punit.pcode_gt_p1_ratio_systolic={}'.format(freq_to_set))
                set_fuse_overrides.append('punit.pcode_gt_p1_ratio_compute={}'.format(freq_to_set))

                set_fuse_overrides.append('punit.pcode_gt_pn_ratio={}'.format(freq_to_set))
                set_fuse_overrides.append('punit.pcode_gt_min_ratio={}'.format(freq_to_set))
                set_fuse_overrides.append('punit.pcode_gt_p0_ratio_chiplet_ifc={}'.format(freq_to_set))
            
                set_fuse_overrides.append('punit.pcode_gt_p0_ratio={}'.format(freq_to_set))
                set_fuse_overrides.append('punit.pcode_gt_p1_ratio={}'.format(freq_to_set))
                set_fuse_overrides.append('punit.pcode_gt_p0_ratio_chiplet_ifc={}'.format(freq_to_set))
            elif 'LINK' in domain.upper():
                set_fuse_overrides.append('punit.pcode_gt_p0_ratio_chiplet_ifc={}'.format(freq_to_set))
                set_fuse_overrides.append('punit.pcode_gt_max_chiplet_ifc_multiplier= 0xA0')
            elif 'HBM' in domain.upper():
                set_fuse_overrides = set_fuse_overrides + self.generate_hbm_fuses(set_frequency)
        
        if self.mode.identify_mode() == "CMV":
            print("Setting itd voltage boot GB to 0")
            set_fuse_overrides.append('punit.pcode_sa_itd_voltage_boot_guardband = {}'.format(0))
            print("Disable media freq restriction to run at half")
            set_fuse_overrides.append('gt_gfx_gt_c0_r3.gtip_base_fuse_fuse_hvm_mediahalffreq_sel = {}'.format(1))
            
            print("Disabling Aging threshold")
            set_fuse_overrides.append('gt_gfx_gt_c0_r3.gtip_base_fuse_fuse_gt_aging_volt_threshold = {}'.format(0xFFF))

            #set_fuse_overrides.append('gt_fuse.gt_fuse_gt_sleep_transistor_volt_threshold = {}'.format(0xFFF))

            print("Set tj_max to {}".format(str(0x100)))
            set_fuse_overrides.append('punit.pcode_tj_max={}'.format(hex(self.max_itd_temp)))

            print("Creating fuses to set itd slope to 0")
            for fuse in self.fuses_to_set_itd_slope(0):
                set_fuse_overrides.append(fuse)

            print("Extracting fuse strings for setting dts slope to 0")
            for fuse in self.fuses_to_set_dts(0):
                set_fuse_overrides.append(fuse)

            print("Disabling thermtrip")
            for fuse in self.fuses_to_disable_thermtrip():
                set_fuse_overrides.append(fuse)                
            
            print("Setting all domain to highest voltage setting to ensure proper boot")
            #for fuse in self.fuses_to_set_voltage_points(str(0xc)): # Set the PO voltage to 1V for all rails
            #    set_fuse_overrides.append(fuse)
        
        return_val['All'] = set_fuse_overrides
        return_val['1'] = set_tile1_fuse
        return_val['0'] = set_tile0_fuse
        return return_val 

    def generate_hbm_fuses(self, frequency):
        set_frequency = str(frequency)
        print("Generating fuses to set hbm frequency to {}".format(set_frequency))

        import pontevecchio.fv.mem.pvcMcUtils as mcu
        manufacturer = "samsung"#mcu.get_hbm_manufacturer(0,0).lower()
        if manufacturer == 'samsung' and set_frequency == "2800":
            import samsung_8h_2p8
            return samsung_8h_2p8.FUSELIST
        elif manufacturer == 'samsung' and set_frequency == "3200":
            import samsung_8h_3p2
            return samsung_8h_3p2.FUSELIST
        elif manufacturer == 'skhynix' and set_frequency == "2800":
            import skhynix_8h_2p8
            return skhynix_8h_2p8.FUSELIST
        elif manufacturer == 'skhynix' and set_frequency == "3200":
            import skhynix_8h_3p2
            return skhynix_8h_3p2.FUSELIST
        print("Could not find fuses for the HBM manufacturer {} to set frequency to {}".format(set_frequency))


    def fuses_to_disable_thermtrip(self):

        return_val = []

        return_val.append('gt_gfx_gt_c0_r3.gtip_base_dts0_cattripdis=1')
        return_val.append('gt_gfx_gt_c0_r3.gtip_base_dts1_cattripdis=1')
        return_val.append('gt_gfx_gt_c0_r3.gtip_base_dts2_cattripdis=1')
        return_val.append('gt_gfx_gt_c0_r3.gtip_base_dts3_cattripdis=1')
        # only for A0
        #return_val.append('gt_gfx_gt_c0_r3.gtip_ct0_dts_cattripdis=1')
        #return_val.append('gt_gfx_gt_c0_r3.gtip_ct1_dts_cattripdis=1')
        #return_val.append('gt_gfx_gt_c0_r3.gtip_ct2_dts_cattripdis=1')
        #return_val.append('gt_gfx_gt_c0_r3.gtip_ct3_dts_cattripdis=1')
        #return_val.append('gt_gfx_gt_c0_r3.gtip_ct4_dts_cattripdis=1')
        #return_val.append('gt_gfx_gt_c0_r3.gtip_ct5_dts_cattripdis=1')
        #return_val.append('gt_gfx_gt_c0_r3.gtip_ct6_dts_cattripdis=1')
        #return_val.append('gt_gfx_gt_c0_r3.gtip_ct7_dts_cattripdis=1')
        #return_val.append('pciess_sapmas_pciess_c0_r2.dts_fuses_cattripdis=1')
        return_val.append('mdfiss_sapmas_mdfiss_ns_t2c_c0_r3.mdfiss_dts_cattripdis=1')
        return_val.append('mdfiss_sapmas_mdfiss_ew_c2_r3.mdfiss_dts_cattripdis=1')
        return_val.append('upmas0_ats_hbmss_ns0_c1_r0.dts0_cattripdis=1')
        return_val.append('upmas0_ats_hbmss_ns1_c1_r2.dts0_cattripdis=1')
        return_val.append('pma_dtsearly.dts_fuse_cattripdis=1')
        return_val.append('upmas0_ats_hbmss_ns2_c1_r3.dts0_cattripdis=1')
        return_val.append('upmas0_ats_hbmss_ns3_c1_r4.dts0_cattripdis=1')
        return return_val

    def fuses_to_set_voltage_points(self,voltage):
        '''
        Adds all fuses needed to set curve voltage. 
        Parameters:
        ----------------
        voltage:- hex voltage value that needs to be set.
        '''
        return_val = []
        for point in range(6):
            #return_val.append('punit.pcode_gt_r03d_vf_voltage_curve0_voltage_index0_voltage_point{}= {}'.format(point,voltage))
            #return_val.append('punit.pcode_gt_r03d_vf_ratio_voltage_index0_ratio_point{}= {}'.format(point,voltage))
            for index in range(2):
                return_val.append('punit.pcode_gt_dsseu_vf_ratio_voltage_index{}_ratio_point{}={}'.format(index, point, voltage))
                for curve in range(8):    
                    return_val.append('punit.pcode_gt_dsseu_vf_voltage_curve{}_voltage_index{}_voltage_point{}= {}'.format(curve, index, point,voltage))
        
        return return_val




    def fuses_to_set_itd_slope(self,itd_slope):
        itd_slope_fuse =[]
        print("Set ITD Slopes")

        itd_slope_fuse.append('punit.pcode_vccmdfi_lv_itd_slope={}'.format(itd_slope))
        itd_slope_fuse.append('punit.pcode_vccmdfi_lv_itd_slope_2={}'.format(itd_slope))
        itd_slope_fuse.append('punit.pcode_cfc0_itd_slope={}'.format(itd_slope))
        itd_slope_fuse.append('punit.pcode_cfc0_itd_slope_2={}'.format(itd_slope))
        itd_slope_fuse.append('punit.pcode_l2_itd_slope={}'.format(itd_slope))
        itd_slope_fuse.append('punit.pcode_ia_itd_slope={}'.format(itd_slope))
        itd_slope_fuse.append('punit.pcode_ia_itd_slope_2={}'.format(itd_slope))
        itd_slope_fuse.append('punit.pcode_sa_itd_slope={}'.format(itd_slope))
        itd_slope_fuse.append('punit.pcode_sa_vr_itd_slope={}'.format(itd_slope))
        itd_slope_fuse.append('punit.pcode_vcceu_itd_slope={}'.format(itd_slope))
        itd_slope_fuse.append('punit.pcode_vcceu_itd_slope_2={}'.format(itd_slope))
        itd_slope_fuse.append('punit.pcode_vccmedia_itd_slope={}'.format(itd_slope))
        itd_slope_fuse.append('punit.pcode_vccmedia_itd_slope_2={}'.format(itd_slope))
        itd_slope_fuse.append('punit.pcode_vccmdfia_itd_slope={}'.format(itd_slope))
        itd_slope_fuse.append('punit.pcode_vccmdfia_itd_slope_2={}'.format(itd_slope))
        itd_slope_fuse.append('punit.pcode_vccrogt_itd_slope={}'.format(itd_slope))
        itd_slope_fuse.append('punit.pcode_vccrogt_itd_slope_2={}'.format(itd_slope))
        itd_slope_fuse.append('punit.pcode_vcccombo_itd_slope={}'.format(itd_slope))
        itd_slope_fuse.append('punit.pcode_vcccombo_itd_slope_2={}'.format(itd_slope))
        return itd_slope_fuse

    def fuses_to_set_dts(self,slope_value):
        slope_fuses =[]
        for quadrant in range(0,3):
            for param in range(0,5):
                slope_fuses.append('gt_gfx_gt_c0_r3.gtip_base_dts{}_dtsslope_{}={}'.format(quadrant, param, hex(slope_value)))
                slope_fuses.append('gt_gfx_gt_c0_r3.gtip_base_dts{}_dtsoffsett0_{}={}'.format(quadrant, param, hex(slope_value)))
        
        for quadrant in range(0,7):
            for param in range(0,5):
                slope_fuses.append('gt_gfx_gt_c0_r3.gtip_ct{}_dts_slope_{}={}'.format(quadrant, param, hex(slope_value)))
                slope_fuses.append('gt_gfx_gt_c0_r3.gtip_ct{}_dts_offset_{}={}'.format(quadrant, param, hex(slope_value)))
                # for A0
                #slope_fuses.append('gt_gfx_gt_c0_r3.gtip_ct{}_dts_offsett0_{}={}'.format(quadrant, param, hex(slope_value)))
                
        return slope_fuses

    def calculate_dss_fuses(self, cache):
        dss_fuses = {}

        print("Calculating dss fuses to be set for current boot") 
        for tile in range(self.device_manager.populated_tile_count()):
            if str(tile) in cache.DSS_OPTION:
                if cache.DSS_OPTION[str(tile)]:
                    hex_value = hex(int(cache.DSS_OPTION[str(tile)],16))
                    print("Setting DSS to binary{} hex {} for tile {}".format(cache.DSS_OPTION[str(tile)],hex_value,tile))
                    dss_fuses[str(tile)] = 'gt_gfx_gt_c0_r3.gtip_base_fuse_fuse_gt_compute_dss_en={}'.format(hex_value)
                else:
                    print("No DSS fuse override set for current boot for tile {}".format(tile))
            else:
                print("No DSS fuse override set for current boot for tile")
        print("DSS Fuses to set :- {}".format(dss_fuses))
        return dss_fuses
