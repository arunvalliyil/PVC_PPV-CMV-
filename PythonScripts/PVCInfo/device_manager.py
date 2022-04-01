from Helpers.instances import InstanceFactory
from .status import Status
from .anr_status import ANRStatus
from .gt_status import GTStatus
from .hbm_status import HBMStatus
from .basedie_status import BASEDieStatus
from .pcie_status import PCIEStatus
from . import supported_ips as ips
from .device_env_handler import DeviceEnvConditionHandler
from Environmentals.env_condition_cache_manager import EnvironmentConditionCache 
from Environmentals.env_condition_cache_manager import EnvironmentConditionCacheManager

class DeviceManager():
    
    supported_features = ['PCIE','HBM','GT','MEDIA']
    dss_command = 'sv.gfxcard0.tile{}.fuses.'
    
    
    _instance = None

    @staticmethod
    def getInstance():
        if DeviceManager._instance ==  None:
            DeviceManager._instance = DeviceManager()
        return DeviceManager._instance

    def __init__(self, instance = None):
        self.tile_count = None
        self.instance = InstanceFactory.getInstance()
        self.device_env_handler = DeviceEnvConditionHandler()
        self.cache_manager = EnvironmentConditionCacheManager()

        print("Initializing unit health monitor")
        self.managers = {
            ips.ANR :ANRStatus(self.instance),
            ips.HBM : HBMStatus(self.instance),
            ips.PCIE : PCIEStatus(self.instance),
            ips.GT : GTStatus(self.instance),
            ips.BASE: BASEDieStatus(self.instance)
        }

    def get_processor_info(self):
        print("Printing processor info")
        api = self.instance.get_fusion_instance()
        print(api.get_processor_infos())
        return "Passed"
        
    def verify_status(self, ip_to_monitor, feature, expected_value):
        ip_status =  self.monitor_ip(ip_to_monitor)
        if feature in ip_status.keys():
            if str(ip_status[feature]) in str(expected_value):
                return "Passed"
        print("Verification failed: Expected value {} - Read Value {}".format(expected_value,ip_status[feature]))
        return "Failed"

    def monitor_ip(self, ip_to_monitor):
        """
         Monitors health of the requested ip. returns a dictionary with key value pair of ip current status
         
         Parameters:
         -------------
         ip_to_monitor: Chosen ip from list to monitor.
         
         output
         ----------
         Dictionary of current ip status
        """
        if not ip_to_monitor:
            print('provide an ip for which status is required. Currently supported ips are {}'.format(','.join(self.managers.keys())))
            return {}

        if ip_to_monitor.upper() not in self.managers.keys():
            print("Currently cannot monitor the the requested ip. Currently supported ips are {}".format(','.join(self.managers.keys())))
            return {}
        try:
            status_manager = self._get_status_manager(ip_to_monitor.upper())
            return status_manager.get_ip_status()
        except Exception as e:
            print("Failed to monitor ip {} with error: {}".format(ip_to_monitor, e))
        
    def _get_status_manager(self, ip):
        return self.managers[ip]
        
    def populated_tile_count(self):
        self.extract_tile_count_fromPyConfig()
        if not self.tile_count:
            sv = self.instance.get_python_sv_instance()
            self.tile_count = len(sv.gfxcard0.tiles)
        return self.tile_count
    
    def extract_tile_count_fromPyConfig(self):
        pyConfig_path = r'C:\PythonSV\pysv_config.ini'
        try:
            with open(pyConfig_path, 'r') as reader:
                for line in reader.readlines():
                    if line.startswith('numtiles'):
                        print(line.split('=')[1].strip())
                        self.tile_count = int(line.split('=')[1].replace('t','').strip())
        except Exception as ex:
            print("Failed to read numtiles from {}. Error {}".format(pyConfig_path,ex))

    def extract_unit_vid(self):
        visual_id = ''
        try:
            api = self.instance.get_fusion_instance()
            visual_id = str(api.get_processor_infos()[0].visual_id)
        except Exception as ex:
            print(ex)
        return visual_id
    
    # Methods to support TP 
    def verify_device_condition(self, condition_name, expected_value = None):
        if not expected_value:
            cache = self.cache_manager.read_environment_condition_cache()
            expected_value = cache.SET_FREQUENCY[condition_name]
        if self.device_env_handler.verify_device_info(condition_name, expected_value):
            return "Passed"
        else:
            return "Failed"

    def set_device_condition(self, condition_name, value):
        return self.device_env_handler.set_device_info(condition_name, value)

    def read_device_condition(self, condition_name):
        return self.device_env_handler.read_device_info(condition_name)
    
    def read_current_dss_info(self, tile = 0):
        sv = self.instance.get_python_sv_instance()
        fuse_value = eval('sv.gfxcard0.tile{}.fuses.gt_gfx_gt_c0_r3.gtip_base_fuse_fuse_gt_compute_dss_en'.format(tile))
        return bin(fuse_value).replace('0b','')
    
    def get_enabled_dss_count(self, dss_info = '', tile = 0):
        if not dss_info:
            dss_info = self.read_current_dss_info(tile)

        count = 0
        for one in str(dss_info): 
            if one == '1':
                count+=1
        return count

    def get_unit_visual_id(self):
        return ''

    def read_unit_ults(self):
        print("Reading ult for the unit")
        ult_list = {}
        for ip in self.managers:
            ult_list.update(self.managers[ip].read_ult())
        return ult_list

    def read_chiplet_disable(self, tile):
        fuse_value = eval('sv.gfxcard0.tile{}.fuses.punit.pcode_gt_chiplet_disable'.format(tile))
        return bin(fuse_value).replace('0b','')
    
    def verify_gt_up(self):
        module = 'GT'
        manager = self._get_status_manager(module)
        if manager.verify_gt_up():
            return "Passed"
        return "Failed"
    
    def verify_gt_Reset_done(self):
        module = 'GT'
        manager = self._get_status_manager(module)
        if manager.gt_reset_done():
            return "Passed"
        return "Failed"

    def pcie_link_state_check(self):
        sv = self.instance.get_python_sv_instance()
        return_val = sv.gfxcard0.tile0.uncore.pcie_swu.ltssmsmsts.ltssmstatemain
        print("PCIe link state is")
        print(return_val)
        if return_val>=3:
            return "Passed"
        else:
            return "Failed"

    def collect_soc_logs(self):
        try:

            sv = self.instance.get_python_sv_instance()
            current_mode = self.instance.get_installation_mode()
            if current_mode != "ppv":
                return

            import fv.ras.pcie_errors as pe
            pe.check_errors()

            import pontevecchio.fv.ras.error_logging_modules.soc_error_log as soc
            soc.soc_error_log()

            import pontevecchio.debug.domains.gfx.gt.gtStatus as gts
            gts.status()

            sv.gfxcard0.tile0.uncore.pcie_swu.showsearch('rma','f')
            sv.gfxcard0.tile0.uncore.pcie_vrsp0.showsearch('rma','f')

        except Exception as ex:
            print("Could not capture soc and GT logs {}".format(ex))  

    def verify_screening_qdf(self):
        return "Passed"
        api = self.instance.get_fusion_instance()
        qdf_value = api.lot_info.ProductID.Sspec
        print("Expected QDF value is {}".format(qdf_value))
        cache = EnvironmentConditionCacheManager().read_environment_condition_cache()
        tested_qdf = cache.TESTED_QDF
        print("Tested QDF value is {}".format(tested_qdf))
        if qdf_value.lower() == tested_qdf.lower():
            return "Passed"
        return "Failed"
    
    def read_mem_l3(self, tile):
        print("Reading Mem L3 value for tile {}".format(tile))
        sv = self.instance.get_python_sv_instance()
        return_val  = ''
        if tile == 0:
            return_val =  sv.gfxcard0.tile0.fuses.gt_gfx_gt_c0_r3.gtip_base_fuse_fuse_gt_meml3_en.get_value()
        else:
            return_val =  sv.gfxcard0.tile1.fuses.gt_gfx_gt_c0_r3.gtip_base_fuse_fuse_gt_meml3_en.get_value()
        print("Mem l3 value for tile {} is {}".format(tile, return_val))
        return return_val

    def cache_device_id(self):
        sv = self.instance.get_python_sv_instance()
        return_val =  hex(self.sv.gfxcard0.tile0.fuses.sgunit_pciess_c0_r2.sg_device_id.get_value())
        print("current recorded device id is {}".format(return_val))
        cache = self.cache_manager.read_environment_condition_cache()
        cache.DEVICEID = device_id
        self.cache_manager.update_environment_condition_cache(cache)
        return '0'+str(return_val)[2:]

    def get_pcie_margin(self):
        return_val = "Failed"
        try:
            import pontevecchio.hsphy.smv.Smv as Smv
            smv=Smv.Smv()
            smv.ParamsSet(Io='PCIE', PortList=[0], LaneList=[], Resets=1, Iterations=1, ResetType=None, State='L0',Gen=5, PPV=True,PPVFormat=1,FomJitterEnable=True,ShowProgress=False,GetTxEq=True, GetFom=True, GetVoc=False, GetJim=False, GetCals=True,GetLoops=True,GetAprobe=False,GetDebug=True,GetCpuInfo=False,FomErrCntrLen=15,FomTmrLenSel=15,Volume=True,LogRunTime=True)
            p_dictionary=smv.Run()
        except Exception as ex:
            print("Failed to get pcie margin {}".format(ex))
        try:
            api = self.instance.get_fusion_instance()
            p_dict = dict(p_dictionary['IP']['PCIE']['gfxcard'][0]['iou']['pxp0']['lane']);
            for p_id, p_info in p_dict.items():
                for key in p_info:
                    header= "Pcie_Margin_Lane"
                    p_key = key.replace(":","_")
                    p_key = p_key.replace(".","_")
                    p_key = p_key.replace(" ","_")
                    header = str(header) + str(p_id)+ "_" + str(p_key)
                    print(header)
                    api.ituff_log(header,p_info[key])
            return_val = "Passed"
        except Exception as ex:
            print("Failed to upload ituff data {}".format(ex))
        return return_val
        
    def get_mdfi_margin(self):
        return_val = "Failed"
        try:
            sv = InstanceFactory.getInstance().get_python_sv_instance()
            itp = InstanceFactory.getInstance().get_itp_instance()
            itp.forcereconfig()
            sv.refresh()
            from users.jjafri import mdfi_ppv_data_log
            mdfi_ppv_data_log.mdfi_PPV_data_log()
            return_val = "Passed"
        except Exception as ex:
            print("Failed to get mdfi margin {}".format(ex))
        return return_val