import os,signal,psutil,subprocess
print ("Initializing python console for product pvc")
import sys
import os.path
import time
import traceback
import glob

if r'C:\PythonSV' not in sys.path: sys.path.append(r'C:\PythonSV')
if r'C:\PythonSV\pontevecchio' not in sys.path: sys.path.append(r'C:\PythonSV\pontevecchio')
if r'C:\STHI\Fusion\PythonScripts' not in sys.path: sys.path.append(r'C:\STHI\Fusion\PythonScripts')
if r'C:\STHI\Fusion\PythonScripts\PVCInfo' not in sys.path: sys.path.append(r'C:\STHI\Fusion\PythonScripts\PVCInfo')
if r'C:\STHI\Fusion\PythonScripts\DSSRecovery' not in sys.path: sys.path.append(r'C:\STHI\Fusion\PythonScripts\DSSRecovery')
if r'C:\STHI\Fusion\PythonScripts\Helpers' not in sys.path: sys.path.append(r'C:\STHI\Fusion\PythonScripts\Helpers')
if r'C:\STHI\Fusion\PythonScripts\Environmentals' not in sys.path: sys.path.append(r'C:\STHI\Fusion\PythonScripts\Environmentals')


def cleanup_cache():
    try:
        print("Cleaning up cache")
        import glob,os
        filelist = glob.glob(os.path.join("C:\STHI\Fusion\PythonScripts\Cache", "*.json"))
        print(filelist)
        for f in filelist:
            print("removing file {}".format(str(f)))
            os.remove(f)
    except Exception as ex:
        print("Failed to clean up cache exception {}".format(ex))

cleanup_cache()



def kill_serial_port_hoggers(process_name):
    try:
        import psutil,signal,os
        for proc in psutil.process_iter():
            if process_name in proc.name():
                print("Killing process {} with pid {}".format(process_name, proc.pid))
                pid = proc.pid
                os.kill(pid,signal.SIGTERM)
                print("Killed process {} with pid {}".format(process_name, proc.pid))
    except Exception as ex:
        print("Failed to kill {} with exception {}".format(process_name, ex))

kill_serial_port_hoggers('ttermpro')
kill_serial_port_hoggers('putty')
kill_serial_port_hoggers('OpenIPC_x64.exe')


from Helpers.instances import InstanceFactory
from PVCInfo import device_manager
from Helpers.Configuration import Configuration
from Helpers import lcbe_programmer
from Helpers.testlist_manager import TestListManager
from Helpers import ituff_helper
from Helpers import mode_identifier
from Helpers.platform_verifier import PlatformVerifier
from Helpers import boot_script_helper
from Environmentals.env_condition_manager import EnvironmentConditionManager
from Environmentals.env_condition_cache_manager import EnvironmentConditionCacheManager
from mce_check import MCECheck
from DSSRecovery.recovery_manager import RecoveryManager
from DSSRecovery.dss_manager import DSSManager
from StageTransitions  import boot_stage_transitions
from Helpers.PhoronixExecuter import PhoronixExecuter
from Helpers.command_appender import CommandAppender
from Environmentals.vmin_voltage_setter import VminSetter
import test_scripts

identifier = mode_identifier.ModeIdentifier.getInstance()
mode = identifier.identify_mode()
instance = InstanceFactory.getInstance()

BootStageTransitions = boot_stage_transitions
Emulator = lcbe_programmer
MachineCheckExceptions = MCECheck()
CacheManager = EnvironmentConditionCacheManager()
DecimalEnvironmentalConditionControl = EnvironmentConditionManager()
StringEnvironmentalConditionControl = EnvironmentConditionManager()
TargetPowerControl = instance.get_power_control()
CellPowerControl = instance.get_power_control()
DeviceManager = device_manager.DeviceManager(instance)
config = Configuration.getInstance()
RecoveryManager = RecoveryManager(instance,DeviceManager,config, BootStageTransitions)
DSSManager = DSSManager(DeviceManager)
Tester = test_scripts.ExecuteTestRun()
BootScript = boot_script_helper.BootScriptHelper()
ITUFFManager = ituff_helper.ItuffTokenHelper()
TestListManager = TestListManager()
PlatFormVerifier = PlatformVerifier()
PhoronixExecuter = PhoronixExecuter()
CommandAppender = CommandAppender()
VminSetter = VminSetter()

def do_startup(startup_script):
    try:
        import os
        if not os.path.exists(startup_script):
            print ("Fatal Error: start up script not found at {}".format(startup_script))
            return
        
        print("Initiating the start up script at {0}".format(startup_script))
        import runpy
        d = runpy.run_path(startup_script, run_name='__main__')
        globals().update(d)
        
        from svtools.common.pysv_config import CFG
        from pontevecchio import startpvc
        startpvc.add_to_main(CFG)
    except Exception as inst:
        print ("Exception caught: %s" % inst) 
        traceback.print_exc()
        print ('Warning: pythonsv for pvc not started with: "%s" ' % startup_script)
        
def toggle_SATA_workaround(instance):
    try:
        api = instance.get_fusion_instance()
        api.sata.select_sata_drive_host(api.sata.SATA_DRIVEB,api.sata.SATA_HOST_CELLHOST)
        print("Toggled sata to cell host")
        time.sleep(10)
        api.sata.select_sata_drive_host(api.sata.SATA_DRIVEB,api.sata.SATA_HOST_TARGET)
        print("Toggled sata back to target")
    except Exception as ex:
        print("Toggling sata connection failed {}".format(ex))

do_startup(r'C:\PythonSV\pontevecchio\startpvc_auto.py')
toggle_SATA_workaround(instance)



def prepare_hbm_fuse_updates():
    return
    hbm_fuse_files = ['skhynix_8h_2p8.py','skhynix_8h_3p2.py','samsung_8h_3p2.py','samsung_8h_2p8.py']
    try:
        for fuse_file in hbm_fuse_files:
            print("Processing file {}".format(fuse_file))
            output_path = r'C:\sthi\fusion\pythonscripts\{}'.format(fuse_file)
            fuse_file_path = r'C:\PythonSV\pontevecchio\toolext\bootscript\recipes\user_custom\{}'.format(fuse_file)
            if exists(fuse_file_path):
                with open(fuse_file_path,'r') as reader:
                    lines = reader.readlines()
                    lines = lines[4:-1]
                with open(output_path, 'w') as writer:
                    writer.write("FUSELIST = [")
                    writer.writelines(lines)
                    writer.write("]")
    except: 
        print("Failed to create HBM modified fuse files.")
