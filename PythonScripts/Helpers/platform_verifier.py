import sys
import os
from Helpers.Configuration import Configuration

class PlatformVerifier:

    def __init__(self):
        print("Loading Platform verifier")
        self.config = Configuration.getInstance()
    
    def verify_sata_version(self):
        expected_sata_version = self.config.get_config_value('general','SATA_VERSION')
        serial_log_loc = self.config.get_config_value('general','SERIAL_LOG_PATH')
        print("Expected Sata version to be {}".format(expected_sata_version))
        return self.check_serial_log(serial_log_loc,expected_sata_version)
        
    
    def verify_linux_version(self):
        expected_linux_version = self.config.get_config_value('general','LINUX_VERSION')
        serial_log_loc = self.config.get_config_value('general','SERIAL_LOG_PATH')
        print("Expected linux kernal version to be {}".format(expected_linux_version))
        print(self.check_serial_log(serial_log_loc,expected_linux_version))
        return "Passed"

    def verify_fcc_version(self):
        expected_fcc_version = self.config.get_config_value('general','FCC_VERSION')
        version_lookup = self.config.get_config_value('general','FCC_VERSION_LOOKUP')
        print("Verifying FCC Version to be {}".format(expected_fcc_version))
        return self.check_serial_log(version_lookup,expected_fcc_version)

    def verify_pvc_device(self):
        #expected_pvc_device = self.config.get_config_value('general','PVC_DID')
        expected_pvc_device = self.config.get_config_value('general','PCI_DID')
        serial_log_loc = self.config.get_config_value('general','SERIAL_LOG_PATH')
        print("PVC device ID should be {}".format(expected_pvc_device))
        return self.check_serial_log(serial_log_loc,expected_pvc_device)    

    def check_serial_log(self, log_path, string_to_check):
        lines = None
        with open(log_path, 'r') as reader:
            lines = reader.readlines()
            lines.reverse()
        for line in lines:
            if str(string_to_check).strip() in str(line).strip():
                return "Passed"
        return "Failed"

