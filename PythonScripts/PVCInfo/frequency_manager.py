import sys, os
import ipccli
import svtools.common.smartprompt
import svtools.common.baseaccess as baseaccess
from svtools import ipip
from Helpers.instances import InstanceFactory
import time

class FrequencyManager():

    def __init__(self):
        self.supported_conditions = ['base','chipet_ifc','compute','media','systolic','link','hbm']
        
    
    def verify_device_info(self, condition_name, expected_value):
        return self.read_device_condition(condition_name) == expected_value

    def read_device_condition(self, condition_name, tile = None):
        if condition_name not in self.supported_conditions:
            raise Exception("Reading condition {} not supported".format(condition_name))
        
        sv = InstanceFactory.getInstance().get_python_sv_instance()
        return_val = 0
        if 'hbm' in condition_name.lower():
            hbm0_pll_ratio = sv.gfxcard0.tile0.uncore.adpll.adpll2.clockgen_cr.clki_dword0.pll_ratio
            hbm_freq = str(2*100 * int(hbm0_pll_ratio))
            print("Read HBM Frequency {}".format(hbm_freq))
            return hbm_freq

        if "base" in condition_name:
           return self.read_base_pll_ratio(sv)
        
        if 'link' in condition_name:
            GTLink_pll_ratio = (sv.gfxcard0.tile0.uncore.iosfpll.iosfpll_1.clockgen_cr.clki_dword0.pll_ratio)
            GTLink_pll_freq = str(50 * int(GTLink_pll_ratio))
            print("\nGTLINK PLL is locked at "+GTLink_pll_freq+" MHz\n")
            return GTLink_pll_freq

        if 'compute' in condition_name:
            clock_mode =  self.identify_pll_mode()
            if clock_mode == 0:
                return self.read_base_pll_ratio(sv)
            if clock_mode == 1:
                GTBaseCompute_pll_freq = 100 * (float(sv.gfxcard0.tile0.uncore.iosfpll.iosfpll_2.clockgen_cr.clki_dword0.pll_ratio))
                print("Clock Mode is Mode{} and running at frequency".format(clock_mode, GTBaseCompute_pll_freq))
                return GTBaseCompute_pll_freq
            if clock_mode == 2:
                GTComputeDie_pll_ratio = (sv.gfxcard0.tile0.uncore.iosfpll.iosfpll_2.clockgen_cr.clki_dword0.pll_ratio)
                GTComputeDie_pll_freq = str(100 * int(GTComputeDie_pll_ratio))
                print("Clock Mode is Mode{} and running at frequency".format(clock_mode, GTComputeDie_pll_freq))
                return GTComputeDie_pll_freq
            if clock_mode == 3:
                return self.chiplet_freq(1)
        
        raise Exception("Python script is not equipped to read frequency for {}".format(condition_name))

    def set_device_condition(self,condition_name, frequency, tile = None):
        print("Set Frequency condition {} to {}handled by fuse overrides during boot".format(condition_name, frequency))

    def read_base_pll_ratio(self, sv):
        GTBase_pll_ratio = (sv.gfxcard0.tile0.uncore.iosfpll.iosfpll_0.clockgen_cr.clki_dword0.pll_ratio)
        GTBase_pll_freq = 100 * (float(GTBase_pll_ratio)/2)
        print("Current Base frequency read to be {}".format(GTBase_pll_freq))
        return GTBase_pll_freq
        
    def identify_pll_mode(self):
        sv = InstanceFactory.getInstance().get_python_sv_instance()
        link_pll = sv.gfxcard0.tile0.gfx.gtgp.pll_sel.link_pll_sel
        compute_pll = sv.gfxcard0.tile0.gfx.gtgp.pll_sel.ct_pll_sel
        if link_pll == 0:
            return 0
        return compute_pll + 1

    def chiplet_freq(self, chiplet_id):
        offset = 8
        sv = InstanceFactory.getInstance().get_python_sv_instance()
        soc = sv.gfxcard0.tile0
        soc.taps.pvc_gdtu0.gdtutapchicken=0x9
        div1 = eval("soc.taps.pvc_cdt_compute_"+str(chiplet_id)+"0.cdt_rtdr_irdec_pll_gcdpll_crashlog2.pll_postdiv1")
        div2 = eval("soc.taps.pvc_cdt_compute_"+str(chiplet_id)+"0.cdt_rtdr_irdec_pll_gcdpll_crashlog2.pll_postdiv2")
        chiplet_ratio = eval("soc.taps.pvc_cdt_compute_"+str(chiplet_id)+"0.cdt_rtdr_irdec_pll_gcdpll_crashlog1.pll_ini_ratio")
        if (div1 == 7) and (div2 == 3):
            chiplet_frequency = int(16.67 * (int(chiplet_ratio) >> (offset + 4)))
        elif (div1 == 7) and (div2 == 1):
            chiplet_frequency = int(16.67 * int(chiplet_ratio >> (offset + 3)))
        elif (div1 == 7) and (div2 == 0):
            chiplet_frequency = int(16.67 * int(chiplet_ratio >> (offset + 2)))
        elif (div1 == 3) and (div2 == 0):
            chiplet_frequency = int(16.67 * int(chiplet_ratio >> (offset + 1)))
        elif (div1 == 1) and (div2 == 0):
            chiplet_frequency = int(16.67 * int(chiplet_ratio >> offset))
        else: chiplet_frequency = 0
        return chiplet_frequency
