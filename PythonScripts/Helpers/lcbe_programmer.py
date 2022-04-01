#!/usr/bin/python
# jcswu
# 11 April 2019
# DG1
##############################

##############################
# 0.1 Copied directly from GLK version + dual LCBE program
#     Added reset LCBE command.
##############################
import os
import os.path
from pathlib import Path
import subprocess
import time
import re
import sys
from subprocess import call
from Helpers.Configuration import Configuration
from Helpers.mid_target_identifier import MidTargetIdentifier
from Helpers.instances import InstanceFactory
from Environmentals.env_condition_cache_manager import EnvironmentConditionCacheManager
from Environmentals.env_condition_cache_manager import EnvironmentConditionCache 


_ver = 0.1
_general_section = 'general'
_lcbe_config_section = 'lcbeconfigs'

print (" ** LCBE Programming script ver "+str(_ver))

target = '0' # WC
mid_target = '1' # PVC
_strPass = 'Passed'
_strFail = 'Failed'


def reset_lcbe(_LCBEselect, _lcbepath):
    """
    _LCBESelect: Lcbe to reset 0/1
    """
    print("[*] Resetting Lcbe App.")
    _lcbeSoftReset          = [_lcbepath, r"-SoftReset", str(_LCBEselect)]
    _run(_lcbeSoftReset, _disableCheck=True)

#Need to put binfile path or _fromConfigFile = True and need to choose LCBE chip _LCBEselect
def emulate_bios(_LCBEselect):
    """

    :param image: BIOS BIN file.
    :return: Passed / Failed
    """
    current_dir = os.getcwd()
    print("Emulating Bios on LCBE {}".format(_LCBEselect))
    _LCBEselect = str(_LCBEselect)
    config = Configuration.getInstance()
    config.reload_configuration()
    mid_target = MidTargetIdentifier.getInstance().identify_mid_target()
    instance = InstanceFactory.getInstance()
    zero_qdf = ['QZBX','QZCN','QZBX','QZEF','QZCP','QZCR','QZDE','QZDA','QZDU','QXDP',]
    qdf = instance.get_fusion_instance().lot_info.ProductID.Sspec
    cache_manager = EnvironmentConditionCacheManager()
    cache = cache_manager.read_environment_condition_cache()
    target_os = cache.TARGETOS
    print("Current boot target determined to be {}".format(target_os))
    
    _lcbepath = config.get_config_value(_lcbe_config_section, "LCBE_EXE_PATH")
    _logpath =  config.get_config_value(_lcbe_config_section, "LOG_PATH")
    _main_path = config.get_config_value(_lcbe_config_section, "MAIN_PATH")
    _bios_path = ''
    if _LCBEselect == '1':
        if target_os.lower() == 'efi':
            _bios_path = config.get_config_value(_lcbe_config_section, "LCBE{}_BIOS_PATH_{}_{}".format(_LCBEselect, mid_target,target_os))
        else:
            _bios_path = config.get_config_value(_lcbe_config_section, "LCBE{}_BIOS_PATH_{}".format(_LCBEselect, mid_target))
    elif qdf in zero_qdf:
        _bios_path = config.get_config_value(_lcbe_config_section, "LCBE{}_BIOS_PATH_0DSS".format(_LCBEselect))
    else:
        _bios_path = config.get_config_value(_lcbe_config_section, "LCBE{}_BIOS_PATH".format(_LCBEselect))

    _chip = config.get_config_value(_lcbe_config_section, "CHIP{}".format(_LCBEselect))
    _fpga_version =config.get_config_value(_lcbe_config_section, "LCBE{}_FPGA_VERSION".format(_LCBEselect))
    _fw_version =config.get_config_value(_lcbe_config_section, "LCBE{}_FW_VERSION".format(_LCBEselect))
    _voltage = config.get_config_value(_lcbe_config_section, "VOLTAGE{}".format(_LCBEselect))

    lcbe_path = Path(_lcbepath).parent
    os.chdir(lcbe_path) # work around for emulation failing if the lcbeapp is executed from a different location

    _lcbeSoftReset          = [_lcbepath, r"-SoftReset", _LCBEselect]
    _lcbeVerCheckCommand    = [_lcbepath, r"-ver", _LCBEselect]
    _lcbeReadVolt           = [_lcbepath, r"-vadjread", _LCBEselect]

    if '1.8' in _voltage:
        _lcbeSetVolt            = [_lcbepath, r"-vadjset1p8v", _LCBEselect]
    elif '3.3' in _voltage:
        _lcbeSetVolt            = [_lcbepath, r"-vadjset3p3v", _LCBEselect]

    _fail_pattern   = 'EMULATION_CONFIG_FAIL'
    _pass_pattern   = 'EMULATION_CONFIG_PASS'
    _verify_pattern = 'EMULATION_VERIFY_PASS'

    # check existence of lcbe
    if not os.path.isfile(_lcbepath.strip()):
        print (" ** LCBEApp.exe Not Found!! Please make sure %s exists!\n " % _lcbepath )
        print (" ** ERROR_BIOS_EMULATION: Abort Emulation..\n")
        return _strFail
    
    # clean up previous logs
    if os.path.isfile(_logpath):
        os.remove(_logpath)

    _bios = os.path.join(_main_path, _bios_path)
    
    if not os.path.isfile(_bios):
        print (" ** %s does not exist!" % _bios)
        print (" ** ERROR_BIOS_EMULATION: Abort Emulation..\n")
        return _strFail

    _lcbeEmulateCommand     = [_lcbepath, r"-emulate", _chip, _bios, _LCBEselect]
    _lcbeVerifyCommand      = [_lcbepath, r"-emulateverify", _bios, _LCBEselect]
    
    try:
        reset_lcbe(_LCBEselect, _lcbepath)

        time.sleep(3)

        print("[*] Checking the LCBE FPGA & FW Version.")

        if not _run(_lcbeVerCheckCommand, _fpga_version):
            print("[!] Wrong LCBE FPGA Version!\n[!] Please program the LCBE FPGA through APSE Update GUI! expected {}".format(_fpga_version))
            return _strFail

        if not _run(_lcbeVerCheckCommand, _fw_version):
            print("[!] Wrong LCBE FW Version!\n[!] Please program the LCBE FW through APSE Update GUI!. Expected {}".format(_fw_version))
            return  _strFail

        print("[*] Reading LCBE Voltage.")
        if not _run(_lcbeReadVolt, _voltage):
            print("[!] LCBE Voltage is not correct!.Expected {}".format(_voltage))
            print("[!] Trying to set LCBE voltage.")
            _run(_lcbeSetVolt, _disableCheck=True)
            time.sleep(3)
            print("[!] Reading back LCBE voltage.")
            _run(_lcbeSoftReset, _disableCheck=True)
            time.sleep(3)
            if not _run(_lcbeReadVolt, _voltage):
                print("[!] Cant set the LCBE Voltage. Please set manually!")
                return _strFail

        print("[*] Emulating BIOS through LCBE.")
        if not _run(_lcbeEmulateCommand, _pass_pattern):
            print("[!] Failed to emulate BIOS!")
            return _strFail

        print("[*] Verifying BIOS through LCBE.")
        if not _run(_lcbeVerifyCommand, _verify_pattern):
            print("[!] Failed to verify BIOS!")
            return _strFail
    except Exception as ex:
        print(ex)
        print (" ** Exception : %s" % sys.exc_info()[0])
        print (" ** ERROR_BIOS_EMULATION: Abort Emulation..\n")
        return _strFail
    os.chdir(current_dir)
    return  _strPass


def _run(_command, _string='', _disableCheck = None):
    """

    :param _command: insert the command needed to execute through subprocess
    :param _string: insert the string as regex format. Eg. "^Find_something"
    :param _disableCheck: to disable string check
    :return: process output (0) if success run program / True if _disableCheck is not disabled
    """
    print("Executing command {}".format(" ".join(_command)))
    process = subprocess.Popen(_command, stdin=subprocess.PIPE, stderr=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
    process.wait()
    _output = str(process.stdout.read(), 'utf-8')
    process.terminate()
    #_output = subprocess.check_output(" ".join(_command), universal_newlines=True)
    print("LCBE process es exited with output {}".format(_output))
    if not _disableCheck:
        return_val = _string in _output
        if not return_val:
            print("Failed to emulat bios output is {}".format(_output))
        return return_val


def Setup():
    results="Passed"
    return results

def Cleanup():
    results="Passed"
    return results
