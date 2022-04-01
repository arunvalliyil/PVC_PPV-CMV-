from Helpers.Configuration import Configuration
import sys,os,time,csv
from datetime import datetime
from Profilers.base_profiler import BaseProfiler
from .thermals import Thermals
from Helpers.instances import InstanceFactory
import pontevecchio.fv.pm.pmutils.convert as c

class ThermalProfiler():

    def __init__(self):
        self.thermals = None
        self.sv = None
        self.api = InstanceFactory.getInstance().get_fusion_instance()
        pass
    
    def setup_thermals(self):
        if not self.sv:
            self.sv = InstanceFactory.getInstance().get_python_sv_instance()
        if not self.thermals:
            self.thermals = Thermals()
            self.thermals.init_from_config(self.sv)
            self.set_temp = self.read_set_temp()

    def get_data_to_log(self):
        return_val = temp_data()
        try:
            self.setup_thermals()
            all_temp = self.thermals.get_all_dts_temps()

            return_val.t0_eu_0 = round(c.convert.bin2float(self.sv.gfxcard0.tile0.pcudata.global_slice_max_temp_4,"U8.8") - 64,2)
            return_val.t0_eu_1 = round(c.convert.bin2float(self.sv.gfxcard0.tile0.pcudata.global_slice_max_temp_6,"U8.8") - 64,2)
            return_val.t0_eu_2 = round(c.convert.bin2float(self.sv.gfxcard0.tile0.pcudata.global_slice_max_temp_8,"U8.8") - 64,2)
            return_val.t0_eu_3 = round(c.convert.bin2float(self.sv.gfxcard0.tile0.pcudata.global_slice_max_temp_10,"U8.8") - 64,2)
            return_val.t0_eu_4 = round(c.convert.bin2float(self.sv.gfxcard0.tile0.pcudata.global_slice_max_temp_12,"U8.8") - 64,2)
            return_val.t0_eu_5 = round(c.convert.bin2float(self.sv.gfxcard0.tile0.pcudata.global_slice_max_temp_14,"U8.8") - 64,2)
            return_val.t0_eu_6 = round(c.convert.bin2float(self.sv.gfxcard0.tile0.pcudata.global_slice_max_temp_16,"U8.8") - 64,2)
            return_val.t0_eu_7 = round(c.convert.bin2float(self.sv.gfxcard0.tile0.pcudata.global_slice_max_temp_18,"U8.8") - 64,2)
            
            return_val.t1_eu_0 =  round(c.convert.bin2float(self.sv.gfxcard0.tile1.pcudata.global_slice_max_temp_4,"U8.8") - 64,2)
            return_val.t1_eu_1 =  round(c.convert.bin2float(self.sv.gfxcard0.tile1.pcudata.global_slice_max_temp_6,"U8.8") - 64,2)
            return_val.t1_eu_2 =  round(c.convert.bin2float(self.sv.gfxcard0.tile1.pcudata.global_slice_max_temp_8,"U8.8") - 64,2)
            return_val.t1_eu_3 =  round(c.convert.bin2float(self.sv.gfxcard0.tile1.pcudata.global_slice_max_temp_10,"U8.8") - 64,2)
            return_val.t1_eu_4 =  round(c.convert.bin2float(self.sv.gfxcard0.tile1.pcudata.global_slice_max_temp_12,"U8.8") - 64,2)
            return_val.t1_eu_5 =  round(c.convert.bin2float(self.sv.gfxcard0.tile1.pcudata.global_slice_max_temp_14,"U8.8") - 64,2)
            return_val.t1_eu_6 =  round(c.convert.bin2float(self.sv.gfxcard0.tile1.pcudata.global_slice_max_temp_16,"U8.8") - 64,2)
            return_val.t1_eu_7 =  round(c.convert.bin2float(self.sv.gfxcard0.tile1.pcudata.global_slice_max_temp_18,"U8.8") - 64,2)

            for temp in all_temp:
                if hasattr(return_val,temp):
                    setattr(return_val,temp,all_temp[temp])
            return_val.set_temp = self.set_temp
            return_val.diode_temp = self.read_tdiode_temp()
        except Exception as ex:
            print("Failed to collect thermal information {}".format(ex))
        return return_val
    
    def read_set_temp(self):
        return_val = 'Empty' 
        try:
            return_val = self.api.intec.get_set_point_temperature()
        except:
            print("")
        return return_val
    
    def read_tdiode_temp(self):
        return_val = 'Empty' 
        try:
            return_val = round(self.api.intec.get_sensor_temperature(1),2)
        except:
            print("")
        return return_val



class temp_data:
    t0_dts_0_0 ='Empty'
    t1_dts_0_0='Empty'
    t0_eu_0 ='Empty'
    t0_eu_1 ='Empty'
    t0_eu_2 ='Empty'
    t0_eu_3 ='Empty'
    t0_eu_4 ='Empty'
    t0_eu_5 ='Empty'
    t0_eu_6 ='Empty'
    t0_eu_7 ='Empty'
    t1_eu_0 ='Empty'
    t1_eu_1 ='Empty'
    t1_eu_2 ='Empty'
    t1_eu_3 ='Empty'
    t1_eu_4 ='Empty'
    t1_eu_5 ='Empty'
    t1_eu_6 ='Empty'
    t1_eu_7 ='Empty'
    t0_hbm_0_0='Empty'
    t0_hbm_0_1='Empty'
    t1_hbm_0_0='Empty'
    t1_hbm_0_1='Empty'
    t0_hbm_1_0='Empty'
    t0_hbm_1_1='Empty'
    t0_hbm_1_2='Empty'
    t0_hbm_1_3='Empty'
    t0_hbm_1_4='Empty'
    t1_hbm_1_0='Empty'
    t1_hbm_1_1='Empty'
    t1_hbm_1_2='Empty'
    t1_hbm_1_3='Empty'
    t1_hbm_1_4='Empty'
    t0_hbm_2_0='Empty'
    t0_hbm_2_1='Empty'
    t0_hbm_2_2='Empty'
    t0_hbm_2_3='Empty'
    t1_hbm_2_0='Empty'
    t1_hbm_2_1='Empty'
    t1_hbm_2_2='Empty'
    t1_hbm_2_3='Empty'
    t0_hbm_3_0='Empty'
    t0_hbm_3_1='Empty'
    t1_hbm_3_0='Empty'
    t1_hbm_3_1='Empty'
    t0_slice_0_0='Empty'
    t0_slice_0_1='Empty'
    t0_slice_0_2='Empty'
    t1_slice_0_0='Empty'
    t1_slice_0_1='Empty'
    t1_slice_0_2='Empty'
    t0_slice_1_0='Empty'
    t0_slice_1_1='Empty'
    t0_slice_1_2='Empty'
    t1_slice_1_0='Empty'
    t1_slice_1_1='Empty'
    t1_slice_1_2='Empty'
    t0_slice_2_0='Empty'
    t0_slice_2_1='Empty'
    t0_slice_2_2='Empty'
    t1_slice_2_0='Empty'
    t1_slice_2_1='Empty'
    t1_slice_2_2='Empty'
    t0_slice_3_0='Empty'
    t0_slice_3_1='Empty'
    t0_slice_3_2='Empty'
    t1_slice_3_0='Empty'
    t1_slice_3_1='Empty'
    t1_slice_3_2='Empty'
    t0_mdfi_ew_0='Empty'
    t0_mdfi_ew_1='Empty'
    t0_mdfi_ew_2='Empty'
    t0_mdfi_ew_3='Empty'
    t0_mdfi_ew_4='Empty'
    t0_mdfi_ew_5='Empty'
    t1_mdfi_ew_0='Empty'
    t1_mdfi_ew_1='Empty'
    t1_mdfi_ew_2='Empty'
    t1_mdfi_ew_3='Empty'
    t1_mdfi_ew_4='Empty'
    t1_mdfi_ew_5='Empty'
    t0_mdfi_ns_0='Empty'
    t0_mdfi_ns_1='Empty'
    t0_mdfi_ns_2='Empty'
    t1_mdfi_ns_0='Empty'
    t1_mdfi_ns_1='Empty'
    t1_mdfi_ns_2='Empty'
    set_temp = 'Empty'
    diode_temp = 'Empty'