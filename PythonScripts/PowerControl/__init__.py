"""
Power control python package 

"""
__version__ = "1.0"

from pkgutil import iter_modules
from pathlib import Path
import inspect
from importlib import import_module
from Helpers.instances import InstanceFactory
from Helpers.mode_identifier import ModeIdentifier
from FusionBaseClass.target_power_control import TargetPowerControl

mode = ModeIdentifier.getInstance().identify_mode()
mid_target = InstanceFactory.getInstance().identify_mid_target()
print("Identified {} as mid target".format(mid_target))

package_dir = Path(__file__).resolve().parent # get the folder from which the files need to be loaded (in my case parent dir)
for (_, module_name, _) in iter_modules([package_dir]):# iterate through all modules in the folder
    module = import_module(f"{__name__}.{module_name}") # locally import module
    for name, obj in inspect.getmembers(module): #get all module details
        if inspect.isclass(obj) and issubclass(obj,TargetPowerControl) and obj is not TargetPowerControl and mid_target in obj.supported_platform() and mode in obj.supported_mode(): # MY filter condition on how to choose the modules.(in my case all classes derived from a base class and not the base class itself which has the mid target set to a pre configured value)
            print("Imported target power control {}".format(name))
            globals()[name] = obj # add the loaded object to globals
