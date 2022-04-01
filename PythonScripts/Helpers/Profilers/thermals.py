###############################################################################
# INTEL CONFIDENTIAL
# Copyright Intel Corporation All Rights Reserved.
#
# The source code contained or described herein and all documents related to
# the source code ("Material") are owned by Intel Corporation or its suppliers
# or licensors. Title to the Material remains with Intel Corporation or its
# suppliers and licensors. The Material may contain trade secrets and propri-
# etary and confidential information of Intel Corporation and its suppliers and
# licensors, and is protected by worldwide copyright and trade secret laws and
# treaty provisions. No part of the Material may be used, copied, reproduced,
# modified, published, uploaded, posted, transmitted, distributed, or disclosed
# in any way without Intel's prior express written permission.
#
# No license under any patent, copyright, trade secret or other intellectual
# property right is granted to or conferred upon you by disclosure or delivery
# of the Materials, either expressly, by implication, inducement, estoppel or
# otherwise. Any license under such intellectual property rights must be ex-
# press and approved by Intel in writing.
###############################################################################
"""
    INTEL CONFIDENTIAL - DO NOT RE-DISTRIBUTE
    Copyright Intel Corporation All Rights Reserved

    Author(s): travis.case@intel.com

    This file contains scripts to interact with DTS sensors
"""
from svtools.logging.toolbox import getLogger
#from namednodes import sv
import namednodes
import os
import math

class Domain:
    def __init__(self, name):
        pass

class IntelDTS:
    def __init__(self, name, namednode,sv):
        self.name = name
        self.namednode = sv.get_by_path(namednode)
    
    def __repr__(self):
        return "{} - {}".format(self.name, self.namednode.path)
    
    def _get_active_sensors(self):
        ret_val = []
        try:
            active_diode_mask = self.namednode.dtscfgfuse.dtscfg_cri_active_diode_mask
        #Handling case for PVC named nodes collateral having the wrong path...
        except AttributeError:
            active_diode_mask = self.namednode.dtsfusecfg.dtscfg_cri_active_diode_mask
        for index in range(0,6):
            if active_diode_mask[index]==1:
                ret_val.append(index)
        return ret_val
    
    def _get_sensor_temp(self, index):
        try:
            dtscfgfuse = self.namednode.dtscfgfuse
        #Handling case for PVC named nodes collateral having the wrong path...
        except AttributeError:
            dtscfgfuse = self.namednode.dtsfusecfg
        rawcode = dtscfgfuse.getfieldobject("dtscfg_cri_dtstemperature_{}".format(index))
        if dtscfgfuse.dtscfg_cri_dtsrawcodeen == 0x0:
            #PVC DTS is doing the calculation automatically it looks like...
            #return rawcode*0.5
            return (rawcode*0.5)-64.0
        else:
            return rawcode*1.0
    
    def _get_all_sensor_temps(self, active_only=True):
        ret_val = []
        if active_only:
            sensor_list = self._get_active_sensors()
        else:
            sensor_list = range(0,6)
        for index in sensor_list:
            ret_val.append(self._get_sensor_temp(index))    
        return ret_val

class IntelPVC_XT_A0:
    def __init__(self, name, namednode, slope_offset_fuse):
        self.name = name
        self.namednode = sv.get_by_path(namednode)
        self.slope_offset_fuse = slope_offset_fuse
    
    def __repr__(self):
        return "{} - {}".format(self.name, self.namednode.path)
    
    def _get_active_sensors(self):
        ret_val = []
        active_diode_mask = self.namednode.dtsfusecfg.dtscfg_cri_active_diode_mask
        for index in range(0,6):
            if active_diode_mask[index]==1:
                ret_val.append(index)
        return ret_val
    
    def _get_sensor_temp(self, index, do_conversion=True):
        dtscfgfuse = self.namednode.dtsfusecfg
        
        rawcode = dtscfgfuse.getfieldobject("dtscfg_cri_dtstemperature_{}_{}".format(math.floor(index/2), index%2))
        if do_conversion:
            #HSD: https://hsdes.intel.com/appstore/article/#/16013180594
            (slope, offset) = self._get_slope_and_offset()
            return round(((rawcode / 512) * slope) - offset, 1)
        else:
            return rawcode*1.0
    
    def _get_all_sensor_temps(self, active_only=True):
        ret_val = []
        if active_only:
            sensor_list = self._get_active_sensors()
        else:
            sensor_list = range(0,6)
        for index in sensor_list:
            ret_val.append(self._get_sensor_temp(index))    
        return ret_val
       
    def _get_slope_and_offset(self):
        fuse_value = self.namednode.parent.parent.fuses.punit.get_by_path(self.slope_offset_fuse)
        slope = fuse_value[15:0] / (2**6)
        offset = fuse_value[31:16] / (2**6)
        return (slope, offset)

class IntelPVC_XT_B0:
    def __init__(self, name, namednode, sv):
        self.name = name
        self.namednode = sv.get_by_path(namednode)
    
    def __repr__(self):
        return "{} - {}".format(self.name, self.namednode.path)
    
    def _get_active_sensors(self):
        ret_val = []
        active_diode_mask = self.namednode.dtscfgfuse.dtscfg_cri_active_diode_mask
        for index in range(0,6):
            if active_diode_mask[index]==1:
                ret_val.append(index)
        return ret_val
    
    def _get_sensor_temp(self, index, do_conversion=True):
        dtscfgfuse = self.namednode.dtscfgfuse
        
        rawcode = dtscfgfuse.getfieldobject("dtsstatus_cri_dtstemperature_{}_{}".format(math.floor(index/2), index%2))
        if dtscfgfuse.dtscfg_cri_rawcode_en == 0x0:
            #PVC XT B0 DTS is doing the calculation automatically it looks like...
            #return rawcode*0.5
            return (rawcode*0.5)-64.0
        else:
            return rawcode*1.0
    
    def _get_all_sensor_temps(self, active_only=True):
        ret_val = []
        if active_only:
            sensor_list = self._get_active_sensors()
        else:
            sensor_list = range(0,6)
        for index in sensor_list:
            ret_val.append(self._get_sensor_temp(index))    
        return ret_val
       
    def _get_slope_and_offset(self, index):
        dtscfgfuse = self.namednode.dtscfgfuse
        slope = dtscfgfuse.getfieldobject("dtscfg_cri_slope_{}".format(index)) / (2**6)
        offset = dtscfgfuse.getfieldobject("dtscfg_cri_offset_{}".format(index)) / (2**6)
        return (slope, offset)

class MoortecDTS:
    _IP_DATA = 0x3
    _A_datasheet = 65.4
    _B_datasheet = 254.6
    _G = 56.9
    _H = 249.6
    _cal5 = 4096
    _cal7 = 1
    _cal8 = 1.8

    def __init__(self, name, namednode, sv):
        self.name = name
        self.namednode = sv.get_by_path(namednode)
    
    def __repr__(self):
        return "{} - {}".format(self.name, self.namednode.path)

    def _test_pvtc(self):
        pvt_comp_id_num_reg = self.namednode.get_by_path(self.namednode.search("pvt_comp_id_num")[0])
        id_read = pvt_comp_id_num_reg
        if(id_read == 0x9b487063):
            print("ID_NUM register matches expectations")
        else:
            print("ERROR: ID_NUM register fail - read:{} expected:0x9b487063".format(id_read))
        
        scratch_test_value = 0xaaaa
        pvt_tm_scratch_reg = self.namednode.get_by_path(self.namednode.search("pvt_tm_scratch")[0])
        pvt_tm_scratch_reg = scratch_test_value
        scratch_read = pvt_tm_scratch_reg
        if(scratch_read == scratch_test_value):
            print("SCRATCH register written and read values match")
        else:
            print("ERROR: SCRATCH register fail - read:{} expected:{}".format(scratch_read, scratch_test_value))

    def _init_pvtc(self, calibrated = False):
        #WRITE TS_SDIF_DISABLE - enable all sensors by writing all 0s
        self.namednode.ts_ts_sdif_disable = 0x0
        #print(gfxcard.pvt.get_by_path(pvtc).ts_sdif_disable)
        
        #Write TS_CLK_SYNTH
        self.namednode.ts_ts_clk_synth = 0x1010201
        #print(gfxcard.pvt.get_by_path(pvtc).ts_clk_synth)
        
        if (calibrated == True):
            #WRITE SDIF Register - ip_cfg - set MODE 1 so cal is expected
            mode = 0x0
        else:
            #WRITE SDIF Register - ip_cfg - set MODE 2 so no cal is needed
            mode = 0x1
        self._write_sdif_reg(0x1, mode)
        #print(self._read_sdif_reg(0x1, 0x0)) #should be 0x1
        
        #WRITE Clear power down bit - Set reset bit - set single sample - set load config - in SDIF Register - ip_ctrl
        #_write_sdif_reg(controller_index,0x0,0x1A) #Manual
        self._write_sdif_reg(0x0,0x108) #Auto
        #print(self._read_sdif_reg(0x0, 0x0)) #should be 0x2

    def _read_sdif_reg(self, ip_addr, instance_index):
        ip_addr = ip_addr << 24
        write_val = 0x80000000 + ip_addr
        #ts_sdif name difference from dg2 to pvc ts_sdif
        sdif_reg = self.namednode.get_by_path(self.namednode.search("ts_sdif$")[0])
        sdif_reg.write(write_val)
        sdif_rdata_reg = self.namednode.getbypath(self.namednode.search(f'ts_{instance_index:02}_sdif_rdata')[0])
        return sdif_rdata_reg
    
    def _write_sdif_reg(self, ip_addr, write_val):
        ip_addr = ip_addr << 24
        write_val = 0x88000000 + ip_addr + write_val
        sdif_reg = self.namednode.get_by_path(self.namednode.search("ts_sdif$")[0])
        sdif_reg.write(write_val)
    
    def _dump_ip_registers(self, ip_num):
        for offset in range(6):
            print("{:02X}: {:02X}".format(offset, self._read_sdif_reg(offset, ip_num)))
    
    def _dump_pvtc_registers(self):
        sv.get_by_path(self.namednode).show()

    def _twos_comp(self, number, num_bits):
        bin_str = bin(number).split("b")[1][-1*num_bits:]
        if len(bin_str) == num_bits and bin_str[0] is "1":
            if bin(number+1)[-1*num_bits] is "1":
                sign = -1
            else:
                sign = 1
            return int(bin(number + 1)[-1*num_bits+1:].split("b")[-1],2) * sign
        else:
            return int(bin(number)[-1*num_bits:].split("b")[-1],2)
    
    def _decode_temp(self, code):
        e = code/self._cal5 - 0.5
        temp = self._G + self._H * e
        return temp
    
    def _get_sensor_temp(self, index):
        read_val = self._read_sdif_reg(self._IP_DATA, index)
        code = 0xffff & read_val
        return self._decode_temp(code)
    
    def _get_all_sensor_temps(self):
        ret_val = []
        reg = self.namednode.get_by_path(self.namednode.search("pvt_ip_config")[0])
        for index in range(0,reg.ts_num):
            ret_val.append(self._get_sensor_temp(index))    
        return ret_val
    
    def _get_active_sensors(self):
        return range(0,self.namednode.get_by_path(self.namednode.search("pvt_ip_config")[0]).ts_num)
    

class MR74137_v2r3(MoortecDTS):
    _IP_DATA = 0x3
    _A_datasheet = 82.6
    _B_datasheet = 262.6
    _G = 81.1
    _H = 255.2
    _cal5 = 4096
    _cal7 = 1
    _cal8 = 1.8  


        

class Thermals:

    _dts_list = []

    def init_from_config(self, sv):
        import tomlkit
    
        global _dts_list
        _dts_list = []
    
        folder_path = os.path.dirname(os.path.realpath(__file__))
        with open(os.path.join(folder_path,r"dts_config.toml"), "r") as reader: 
            config = reader.read()
        config_dict = tomlkit.parse(config)
    
        for dts in config_dict["dts_list"]:
            #print("{}-{}".format(dts["name"], dts["type"]))
            #if more than 1 tile/gfxcard split into a different object for each one
            if isinstance(sv.get_by_path(dts["named_node"]), namednodes.comp.ComponentGroup):
                for access_path in sv.get_by_path(dts["named_node"]):
                    #todo: find a better way to dynamically handle tiles
                    #todo: improve mooretec vs intec
                    if "tile0" in access_path.path:
                        name = "t0_"+dts["name"]
                    else:
                        name = "t1_"+dts["name"]
                    if dts["type"] == "intel":
                        _dts_list.append(IntelDTS(name,access_path.path, sv))
                    elif dts["type"] == "moortec":
                        _dts_list.append(MoortecDTS(name,access_path.path, sv))
                    elif dts["type"] == "MR74137_v2r3":
                        _dts_list.append(MR74137_v2r3(name,access_path.path,sv))
                    elif dts["type"] == "intelpvc_xt_a0":
                        _dts_list.append(IntelPVC_XT_A0(name,access_path.path,dts["slope_offset_fuse"]))
                    elif dts["type"] == "intelpvc_xt_b0":
                        _dts_list.append(IntelPVC_XT_B0(name,access_path.path, sv))
                    else:
                        raise Exception("Unexpected type '{}' found in config".format(dts["type"]))

            else:
                if dts["type"] == "intel":
                    _dts_list.append(IntelDTS(dts["name"],dts["named_node"]))
                elif dts["type"] == "moortec":
                    _dts_list.append(MoortecDTS(dts["name"],dts["named_node"]))
                elif dts["type"] == "intelpvc_xt_a0":
                    _dts_list.append(IntelPVC_XT_A0(dts["name"],dts["named_node"],dts["slope_offset_fuse"]))
                elif dts["type"] == "intelpvc_xt_b0":
                    _dts_list.append(IntelPVC_XT_B0(dts["name"],dts["named_node"]))
                else:
                    raise Exception("Unexpected type '{}' found in config".format(dts["type"]))

    def get_all_dts_temps(self):
        global _dts_list
        ret_val = {}
        for dts in _dts_list:
            for index, sensor_temp in enumerate(dts._get_all_sensor_temps()):
                ret_val[dts.name+"_"+str(index)] = sensor_temp
        return ret_val

    def get_dts_temp(self, dts_id, source = "dts"):
        #this is the case where a user gets all sensors assigned to a given dts
        dts = self._get_dts_by_id(dts_id)
        if (dts is not None):
            return dts._get_all_sensor_temps()
        #this is the case where a user specifies the name then the index
        (split_dts_id,index) = dts_id.rsplit("_",1)
        dts = self._get_dts_by_id(split_dts_id)
        if (dts is not None):
            return dts._get_sensor_temp(index)
    
        raise Exception("dts_id '{}' is not found".format(dts_id))


    def get_dts_names(self):
        global _dts_list
        ret_val = []
        for dts in _dts_list:
            for index in dts._get_active_sensors():
                ret_val.append("{}_{}".format(dts.name,index))
        return ret_val

    def _get_dts_by_id(self, dts_id):
        global _dts_list
        for dts in _dts_list:
            if (dts.name == dts_id):
                return dts
        return None

    def _set_rawcode_en(value):
        for dts in _dts_list:
            try:
                dts.namednode.dtscfgfuse.dtscfg_cri_dtsrawcodeen = value
            except AttributeError:
                pass

    def _init_pvtc(calibrated = False):
        for dts in _dts_list:
            try:
                dts._init_pvtc(calibrated)
            except AttributeError:
                pass

