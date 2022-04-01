
from Helpers.instances import InstanceFactory
from Helpers.Configuration import Configuration
import threading, time , datetime
from os.path import exists
from Environmentals.env_condition_cache_manager import EnvironmentConditionCacheManager
from Environmentals.env_condition_cache_manager import EnvironmentConditionCache

class PVCProfiler():
    _instance = None

    
    @staticmethod
    def getInstance():
        if PVCProfiler._instance ==  None:
            PVCProfiler._instance = PVCProfiler()
        return PVCProfiler._instance

    def __init__(self):
        print("Initializing PVC Profiler for current run")
        self.config = Configuration.getInstance()
        self.api = InstanceFactory.getInstance().get_fusion_instance()
        self.itp = InstanceFactory.getInstance().get_itp_instance()
        self.stop = False
        self.t1 = None
        self.profiler_list =[]
        enable_profiling = self.config.get_config_value('general','EnableThermalProfilingMarker')
        self.profile_location = self.config.get_config_value('general','EnableThermalProfilingLOGLocation')
        self.enable_profiling = False
        self.visual_id = ''
        self.set_point = 'Empty'
        self.cache_manager = EnvironmentConditionCacheManager()
        if enable_profiling.lower() == "true":
            self.enable_profiling = True
        pass
    
    def ProfilePVC(self):
        data = profile_data()
        data =  self.update_execution_info(data)
        data.date_tm = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        for profiler in self.profiler_list:
            datalog = profiler.get_data_to_log()
            data = self.merge_data_lot(data, datalog)
            data.visual_id = self.visual_id
        if data.FIVR_EU0_T0 == "Empty":
            return data
        with open(self.profile_location, 'a') as writer:
            to_write = []
            for prop in dir(data):
                if '__' not in prop:
                    to_write.append(str(getattr(data, prop)))
            writer.write(','.join(to_write)+ "\n")
        return data

    def merge_data_lot(self, data, datalog):
        if not datalog:
            return data
        for prop in dir(datalog):
            if '__' not in prop:
                setattr(data,prop,getattr(datalog, prop))
        return data

    
    def start_continous_profiling(self):
        while True:
            global stop_threads
            print("Reading device PVC details")
            self.ProfilePVC()
            time.sleep(10)
            if stop_threads:
                break
    
    def StopProfiling(self):
        try:
            print("stopping device temp measurement")
            global stop_threads
            stop_threads = True
            self.t1 = None
        except:
            print("Failed to stop profiling")
        return "Passed"

    def create_log_file(self):
        if exists(self.profile_location):
            return
        dt_time = self.api.lot_info.StartTime.strftime("%Y_%m_%d-%I_%M_%S_%p")
        
        if self.api.get_processor_infos():
            self.visual_id = self.api.get_processor_infos()[0].visual_id.Id
        if self.set_point == 'Empty':
            self.set_point = self.api.intec.get_set_point_temperature()
        test_flow = self.api.test_flow_name.replace(' ', '_')
        cache_data = self.cache_manager.read_environment_condition_cache()
        freq = 'NotSet'
        if 'compute' in cache_data.SET_FREQUENCY:
            freq = cache_data.SET_FREQUENCY['compute']
        elif 'base' in cache_data.SET_FREQUENCY:
            freq = cache_data.SET_FREQUENCY['base']
        self.profile_location = "{}_{}_{}_{}_{}_{}.{}".format(self.profile_location.split('.')[0] , self.visual_id ,freq, self.set_point,test_flow, dt_time, self.profile_location.split('.')[1] )
        print("Profile output written to {}".format(self.profile_location))
        with open(self.profile_location, 'w') as writer:
            header= []
            for prop in dir(profile_data):
                if '__' not in prop:
                    header.append(prop)
            writer.write(','.join(header)+"\n")

    def StartProfiling(self, istpinitiated = True ):
        try:
            if not istpinitiated and not self.enable_profiling:
                print("Thermal profiling disabled.")
                return "Passed"

            self.create_log_file()
            if self.t1:
                print("profiling thread is alive.")
                return "Passed"
            from .frequency_profiler import FrequencyProfiler
            from .voltage_profiler import VoltageProfiler
            from .thermal_profiler import ThermalProfiler
        
            self.profiler_list = [FrequencyProfiler(),VoltageProfiler(),ThermalProfiler() ]
            print("Starting PVC profiling")
            global stop_threads
            stop_threads = False

            self.t1 = threading.Thread(target = self.start_continous_profiling)
            self.t1.start()
        except Exception as ex:
            print("Failed to start profiling {}".format(ex))
        return "Passed"
    
    def update_execution_info(self, data):
        try:
            if self.api.test_iteration and self.itp.power_status():
                test_name = self.api.test_iteration.Test.Name
                if test_name:
                    data.executing_test = test_name
                boot_Stage = self.api.test_iteration.BootStage.StageName
                if boot_Stage:
                    data.stage = boot_Stage
                else:
                    data.stage = "PowerOff"
        except:
            print("Failed to access fusion api")
        return data


class profile_data:
    date_tm ='Empty'
    visual_id = 'Empty'
    stage ='Empty'
    executing_test ='Empty'
    compute_freq = 'Empty'
    base_freq = 'Empty'
    link_freq = 'Empty'
    hbm_freq = 'Empty'
    FIVR_EU0_T0 = 'Empty'
    FIVR_EU2_T0 = 'Empty'
    FIVR_EU4_T0 = 'Empty'
    FIVR_EU6_T0 = 'Empty'
    FIVR_EU8_T0 = 'Empty'
    FIVR_EU10_T0 = 'Empty'
    FIVR_EU12_T0 = 'Empty'
    FIVR_EU14_T0 = 'Empty'
    FIVR_BASE2_T0 = 'Empty'
    FIVR_EU0_T1 = 'Empty'
    FIVR_EU2_T1 = 'Empty'
    FIVR_EU4_T1 = 'Empty'
    FIVR_EU6_T1 = 'Empty'
    FIVR_EU8_T1 = 'Empty'
    FIVR_EU10_T1 = 'Empty'
    FIVR_EU12_T1 = 'Empty'
    FIVR_EU14_T1 = 'Empty'
    FIVR_BASE2_T1 = 'Empty'
    diode_temp = 'Empty'
    set_temp ='Empty'
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