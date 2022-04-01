from Helpers.Configuration import Configuration
import sys,os,time,csv
from datetime import datetime
import threading
from Helpers.instances import InstanceFactory
from Environmentals.env_condition_cache_manager import EnvironmentConditionCacheManager
from Environmentals.env_condition_cache_manager import EnvironmentConditionCache
sys.path.append(r'C:\PythonSV\pontevecchio\users\tcase')

stop_threads = False

class ThermalProfiler():

    _instance = None

    def __init__(self):
        self.config = Configuration.getInstance()
        self.api = InstanceFactory.getInstance().get_fusion_instance()
        self.itp = InstanceFactory.getInstance().get_itp_instance()
        enable_profiling = self.config.get_config_value('general','EnableThermalProfilingMarker')
        self.enable_profiling = False
        if enable_profiling.lower() == "true":
            self.enable_profiling = True

        self.profiling_log = self.config.get_config_value('general','EnableThermalProfilingLOGLocation')
        self.now = datetime.now()
        self.thermals = None
        self.stop = False
        self.t1 = None
        self.dts_names = []
        self.header = []
    
    @staticmethod
    def getInstance():
        if ThermalProfiler._instance ==  None:
            ThermalProfiler._instance = ThermalProfiler()
        return ThermalProfiler._instance

    def create_thermal_headers(self):
        if os.path.exists(self.profiling_log):
            return

        dt_string = self.now.strftime("%Y-%m-%d %H:%M:%S.")
        self.profiling_log = self.profiling_log.split('.')[0] + '_'+ dt_string.replace(' ','_').replace('-','_').replace(':','').strip() + self.profiling_log.split('.')[1]
        print("Thermal Profile Creating profile data to {}".format(self.profiling_log))
        self._get_thermals()
        self.dts_names = list(self.thermals.get_all_dts_temps().keys())
        
        try:
            with open(self.profiling_log,'w',newline='') as csvfile:
                writer = csv.writer(csvfile)
                self.header = list(filter(lambda header: not header.startswith('_'), dir(temp_data)))
                writer.writerow(self.header)
        except Exception as ex:
            print("failed {}".format(ex))
            return False
        return True

    def is_lot_set_up(self):
        try:
            print(self.api.log_directory)
            return True
        except:
            print("waiting for lot set up")
            return False

    def read_feedback_temp(self):
        try:
            return round(self.api.intec.get_feedback_temperature(),3)
        except:
            return ""

    def log_device_temp(self):
        self.create_thermal_headers()
        cacheManager = EnvironmentConditionCacheManager()
        cache = cacheManager.read_environment_condition_cache()
        temp = self.read_feedback_temp()
        set_temp = ""
        sensors = None
        try:
            set_temp = self.api.intec.get_set_point_temperature()
            sensors = self.api.intec.get_enabled_sensors()
        except Exception as ex:
            print("Exception :- {}".format(ex.message))

        if sensors:
            tdiode_temp = round(self.api.intec.get_sensor_temperature(sensors[0]),3)

        frequency = ''
        for freq in cache.SET_FREQUENCY:
            frequency = cache.SET_FREQUENCY[freq]

        try:
            data = temp_data()
            data.set_temp = set_temp
            data.diode_temp = tdiode_temp
            data.case_temp = temp
            data.adate_tm = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            data.id = self.api.get_processor_infos()[0].visual_id.Id
            test_name = ''
            if frequency:
                data.frequency = frequency
            else:
                data.frequency = 'Not Set'
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
                print("api access failed")
            if self.itp.power_status():
                try:
                    all_temp = self.thermals.get_all_dts_temps()
                    print(test_name+','+str(all_temp))
                    for temp in all_temp:
                        setattr(data,temp,all_temp[temp])
                except Exception as ex:
                    print(ex)
                    print(" Thermal Profile Exception thrown while trying to reading DTS temp")
            else:
                print(" Thermal Profile Unit not powered on")
                
            with open(self.profiling_log,'a',newline='') as csvfile:
                writer = csv.writer(csvfile)
                row_to_write = []
                for header in self.header:
                    row_to_write.append(getattr(data, header))
                writer.writerow(row_to_write)
        except Exception as ex:
            print(" Thermal Profile profiling to file failed: {}".format(ex))

    def start_continous_profiling(self):
        while True:
            global stop_threads
            print("Reading device temperature details")
            self.log_device_temp()
            time.sleep(5)
            if stop_threads:
                break
    
    def StopProfiling(self):
        print("stopping device temp measurement")
        global stop_threads
        stop_threads = True
        return "Passed"

    def StartProfiling(self, istpinitiated = True ):
        if self.t1:
            print("Thermal profiling thread is alive.")
            return "Passed"
        print("Starting Thermal profiling")
        global stop_threads
        stop_threads = False
        if not istpinitiated and not self.enable_profiling:
            return "Passed"
        
        print("Initiating Thermal profiling")
        self.t1 = threading.Thread(target = self.start_continous_profiling)
        self.t1.start()
        return "Passed"
    
    def _get_thermals(self):
        if not self.thermals:
            import thermals
            self.thermals = thermals

class temp_data:
    adate_tm ='Empty'
    diode_temp  ='Empty'
    executing_test ='Empty'
    frequency = 'Empty'
    id ='Empty'
    case_temp = 'Empty'
    set_temp ='Empty'
    stage ='Empty'
    t0_dts_0_0 ='Empty'
    t1_dts_0_0='Empty'
    t0_compute_00_0='Empty'
    t0_compute_00_1='Empty'
    t0_compute_00_2='Empty'
    t0_compute_00_3='Empty'
    t0_compute_00_4='Empty'
    t0_compute_00_5='Empty'
    t1_compute_00_0='Empty'
    t1_compute_00_1='Empty'
    t1_compute_00_2='Empty'
    t1_compute_00_3='Empty'
    t1_compute_00_4='Empty'
    t1_compute_00_5='Empty'
    t0_compute_10_0='Empty'
    t0_compute_10_1='Empty'
    t0_compute_10_2='Empty'
    t0_compute_10_3='Empty'
    t0_compute_10_4='Empty'
    t0_compute_10_5='Empty'
    t1_compute_10_0='Empty'
    t1_compute_10_1='Empty'
    t1_compute_10_2='Empty'
    t1_compute_10_3='Empty'
    t1_compute_10_4='Empty'
    t1_compute_10_5='Empty'
    t0_compute_20_0='Empty'
    t0_compute_20_1='Empty'
    t0_compute_20_2='Empty'
    t0_compute_20_3='Empty'
    t0_compute_20_4='Empty'
    t0_compute_20_5='Empty'
    t1_compute_20_0='Empty'
    t1_compute_20_1='Empty'
    t1_compute_20_2='Empty'
    t1_compute_20_3='Empty'
    t1_compute_20_4='Empty'
    t1_compute_20_5='Empty'
    t0_compute_30_0='Empty'
    t0_compute_30_1='Empty'
    t0_compute_30_2='Empty'
    t0_compute_30_3='Empty'
    t0_compute_30_4='Empty'
    t0_compute_30_5='Empty'
    t1_compute_30_0='Empty'
    t1_compute_30_1='Empty'
    t1_compute_30_2='Empty'
    t1_compute_30_3='Empty'
    t1_compute_30_4='Empty'
    t1_compute_30_5='Empty'
    t0_compute_40_0='Empty'
    t0_compute_40_1='Empty'
    t0_compute_40_2='Empty'
    t0_compute_40_3='Empty'
    t0_compute_40_4='Empty'
    t0_compute_40_5='Empty'
    t1_compute_40_0='Empty'
    t1_compute_40_1='Empty'
    t1_compute_40_2='Empty'
    t1_compute_40_3='Empty'
    t1_compute_40_4='Empty'
    t1_compute_40_5='Empty'
    t0_compute_50_0='Empty'
    t0_compute_50_1='Empty'
    t0_compute_50_2='Empty'
    t0_compute_50_3='Empty'
    t0_compute_50_4='Empty'
    t0_compute_50_5='Empty'
    t1_compute_50_0='Empty'
    t1_compute_50_1='Empty'
    t1_compute_50_2='Empty'
    t1_compute_50_3='Empty'
    t1_compute_50_4='Empty'
    t1_compute_50_5='Empty'
    t0_compute_60_0='Empty'
    t0_compute_60_1='Empty'
    t0_compute_60_2='Empty'
    t0_compute_60_3='Empty'
    t0_compute_60_4='Empty'
    t0_compute_60_5='Empty'
    t1_compute_60_0='Empty'
    t1_compute_60_1='Empty'
    t1_compute_60_2='Empty'
    t1_compute_60_3='Empty'
    t1_compute_60_4='Empty'
    t1_compute_60_5='Empty'
    t0_compute_70_0='Empty'
    t0_compute_70_1='Empty'
    t0_compute_70_2='Empty'
    t0_compute_70_3='Empty'
    t0_compute_70_4='Empty'
    t0_compute_70_5='Empty'
    t1_compute_70_0='Empty'
    t1_compute_70_1='Empty'
    t1_compute_70_2='Empty'
    t1_compute_70_3='Empty'
    t1_compute_70_4='Empty'
    t1_compute_70_5='Empty'
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