import sys
from pkgutil import iter_modules
from pathlib import Path
import inspect
from importlib import import_module
from FusionBaseClass.boot_stage_controller import BootStageController

package_dir = Path(__file__).resolve().parent
loaded_modules =[]
for (_, module_name, _) in iter_modules([package_dir]):
    module = import_module(f"{__name__}.{module_name}")
    for name, obj in inspect.getmembers(module):
        if inspect.isclass(obj) and issubclass(obj,BootStageController) and obj is not BootStageController and name not in loaded_modules and  not bool(getattr(obj, "__abstractmethods__", True)):
            print("Importing Boot stage controller {}".format(name))
            globals()[name] = obj
            loaded_modules.append(name)