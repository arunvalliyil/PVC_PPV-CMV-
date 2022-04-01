
from FusionBaseClass.boot_stage_controller import BootStageController
from Helpers.instances import InstanceFactory

class MarrionetteBootStageController(BootStageController):
 
    def is_in_boot_stage(self, boot_stage):
        _api = InstanceFactory.getInstance().get_fusion_instance()
        print("Checking if target is in {}".format(boot_stage.replace('Stage','').lower()))
        return str.lower(_api.marionette.get_connected_os()) in str.lower(boot_stage)
    