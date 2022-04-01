import os,sys,csv
import json
from Helpers.instances import InstanceFactory
from Helpers.Configuration import Configuration
from PVCInfo.device_manager import DeviceManager

class UnitIdentityUpdater():
    
    _instance = None
    @staticmethod
    def getInstance():
        if not UnitIdentityUpdater._instance :
            UnitIdentityUpdater._instance = UnitIdentityUpdater()
        return UnitIdentityUpdater._instance
    
    def calculate_vid_from_ult(self, ult):
        vid_lookup = Configuration.getInstance().get_config_value('general','VID_LOOKUP')
        print("Looking for vid look up file at {}".format(vid_lookup))
        return_val = ''
        try:
            if os.path.exists(vid_lookup):
                filtered = None
                with open(vid_lookup, encoding='utf-8-sig') as f:
                    reader = csv.DictReader(f) 
                    filtered = list(filter(lambda row: ult == row["TPPV"], reader))
                    if filtered:
                        return_val = filtered[0]["Vid"]
                    else:
                        print("Look up table does not have a VID assigned to requested ult {}".format(ult))
                        return return_val
            else:
                print("Missing VID look up file at {}".format(vid_lookup))
        except Exception as e:
            print("Failed to extract vid from look up table:- {}".format(e))
        return return_val

    def update_identifiers(self,vid):
        try:
            api = InstanceFactory.getInstance().get_fusion_instance()
            device = DeviceManager.getInstance()
            ult_list = device.read_unit_ults()
            for identifier in ult_list:
                print("Updating ult for identifier {} with ult {}".format(identifier, ult_list[identifier]))
                api.update_ult(ult_list[identifier], identifier)
            print("Updated fusion with ult for the device")

            ult = ult_list["U1.U1"]
            if not vid:
                vid = self.calculate_vid_from_ult(ult)
            if vid:
                api.update_vid(vid)
                print("Updated VisualID for the unit with {}".format(vid))
                self.update_all_ult_info(vid)
                print("Updated all available ult information for the unit{}".format(vid))
        except Exception as ex:
            print("Failed to update ult information {}".format(ex))

    def update_all_ult_info(self, visualid):
        vid_lookup = Configuration.getInstance().get_config_value('general','VID_LOOKUP')
        api = InstanceFactory.getInstance().get_fusion_instance()
        print("Looking for ult list look up file at {}".format(vid_lookup))
        return_val = ''
        try:
            if os.path.exists(vid_lookup):
                filtered = None
                with open(vid_lookup, encoding='utf-8-sig') as f:
                    reader = csv.DictReader(f) 
                    filtered = list(filter(lambda row: visualid == row["VID"], reader))
                    for ip in filtered:
                        api.update_ult(ip['TPPV'], ip['MDPOSITION'])
                        
            else:
                print("Missing VID look up file at {}".format(vid_lookup))
        except Exception as e:
            print("Failed to extract vid from look up table:- {}".format(e))
        return return_val


