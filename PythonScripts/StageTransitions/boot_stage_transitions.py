'''
How to use:
    Assume we want to implement the boot stage transition from PowerOffStage to EfiStage
    1.- Create a pair of functions (start and wait) that perform any necessary steps for the transition to take place. In example:
            def start_transition_power_off_to_efi(from_boot_stage, to_boot_stage):
                #insert custom code here
            def wait_for_transition_power_off_to_efi(from_boot_stage, to_boot_stage):
                #insert custom code here
    2.- Register the new function into the _boot_stage_transitions dictionary. In example:
            _boot_stage_transitions = {
                "PowerOffStage-EfiStage": {
                    "start_transition": start_transition_power_off_to_efi,
                    "wait_for_transition": wait_for_transition_power_off_to_efi
                }...
'''
import datetime
import time, inspect, sys
from Helpers.instances import InstanceFactory
import supported_boot_stages as stage


def is_abstract(cls):
    return bool(getattr(cls, "__abstractmethods__", False))

def wait_for_transition_to_boot_stage(from_boot_stage, to_boot_stage, timeout):
    '''
    Waits for the boot stage transition to complete.

    Parameters
    ----------
    from_boot_stage: str
        Name of the boot stage the target is currently at. (i.e. PowerOff, Fivrbreak, EFI)

    to_boot_stage: str
        Name of the boot stage the method will transition to. (i.e. PowerOff, Fivrbreak, EFI)

    timeout: int
        Max time in milliseconds this transition should take.
    '''
    starttime = datetime.datetime.now()
    _TimeExpired = True
    print("Booting to {} waiting for {}".format(to_boot_stage,str(timeout)))
    while (datetime.datetime.now() - starttime) < datetime.timedelta(milliseconds=int(timeout)):
       if is_in_boot_stage(to_boot_stage):
           _TimeExpired = False
           break
       else:
            time.sleep(1)
        
    print("Total Time : %d seconds" % (datetime.datetime.now() - starttime) .total_seconds())
            
    if _TimeExpired:
        raise RuntimeError("Timed out while waiting for %s" % (to_boot_stage))
    else:
        print("Successfully booted to %s! \n" % to_boot_stage)

def start_transition_not_implemented(from_boot_stage, to_boot_stage):
    raise NotImplementedError("Start transition is not implemented from '{0}' to '{1}'".format(from_boot_stage, to_boot_stage))

def wait_for_transition_not_implemented(from_boot_stage, to_boot_stage,timeout):
    raise NotImplementedError("Wait for transition is not implemented from '{0}' to '{1}'".format(from_boot_stage, to_boot_stage))

def get_all_boot_stages():
    all_controllers = []
    from FusionBaseClass.boot_stage_controller import BootStageController
    from  StageTransitions import StageControllers
    for name,obj in inspect.getmembers(sys.modules['StageTransitions.StageControllers']):
        if inspect.isclass(obj) and issubclass(obj,BootStageController) and not is_abstract(obj):
            if obj not in all_controllers:
                all_controllers.append(obj)
    return all_controllers

def get_boot_stage_controller(boot_stage):
    from FusionBaseClass.boot_stage_controller import BootStageController
    from  StageTransitions import StageControllers
    for name,obj in inspect.getmembers(sys.modules['StageTransitions.StageControllers']):
        if inspect.isclass(obj) and issubclass(obj,BootStageController):
            if obj.Stage_Handled == boot_stage:
                return obj()
    

def prepare_available_transitions():
    available_transitions = {}
    for boot_stage in get_all_boot_stages():
        for to_stage in boot_stage().get_supported_next_stage():
            key = "{}-{}".format(boot_stage.Stage_Handled,to_stage)
            available_transitions[key] = {
                    "start_transition": get_boot_stage_controller(boot_stage.Stage_Handled).start_transition_method,
                    "wait_for_transition": wait_for_transition_to_boot_stage
                }
    return available_transitions

print("loading all boot stage transitioners")

_boot_stage_transitions = prepare_available_transitions()


def is_in_boot_stage(boot_stage):
    '''
    Checks if the target is in the boot stage provided.
        
    Parameters
    ----------
    boot_stage: str
        Name of the boot stage. (i.e. PowerOff, Fivrbreak, EFI)

    Returns
    -------
    bool
        True if target is in the boot stage.
    '''
    instance = InstanceFactory.getInstance()
    return instance.get_boot_stage_controller(boot_stage).is_in_boot_stage(boot_stage)

def get_transition_value(from_boot_stage, to_boot_stage, subkey, default_value):
    '''
    Returns the value for the specified subkey of the "_boot_stage_transitions" dictionary or returns the
    provided default value if there is no key for the combination of "from_boot_stage-to_boot_stage" or if
    the specified subkey does not exist.
    
    Parameters
    ----------
    from_boot_stage: str
        Name of the boot stage Fusion thinks the target is currently at. (i.e. PowerOff, Fivrbreak, EFI)

    to_boot_stage: str
        Name of the boot stage we will try to transition to. (i.e. PowerOff, Fivrbreak, EFI)

    subkey: str
        Subkey we should try to retrieve the value from. (i.e. start_transition)

    default_value: function
        Function to return if the key or subkey does not exist.
    
    Returns
    -------
    Function
        Function found under the specified key->subkey or the default value if no function was found.
    '''
    transition_key = "{0}-{1}".format(from_boot_stage, to_boot_stage)
    print(transition_key)
    transition_object = _boot_stage_transitions.get(transition_key)
    if transition_object == None:
        print(_boot_stage_transitions.keys)
        return default_value
    transition_subvalue = transition_object.get(subkey, default_value)
    return transition_subvalue

def can_transition_to_boot_stage(from_boot_stage, to_boot_stage):
    '''
    Determines if target is in the correct state to start the boot stage transition.

    Parameters
    ----------
    from_boot_stage: str
        Name of the boot stage Fusion thinks the target is currently at. (i.e. PowerOff, Fivrbreak, EFI)

    to_boot_stage: str
        Name of the boot stage we will try to transition to. (i.e. PowerOff, Fivrbreak, EFI)

    Returns
    -------
    str
        If the transition can be performed this method should return None or "True". If the transition cannot
        be performed then this method should return the reason this transition is being denied. For example,
        if the from_boot_stage said Earbreak, but the system was not in Earbreak, then the denial reason could
        be: Not in Earbreak.
    '''
    transition = get_transition_value(from_boot_stage, to_boot_stage, "start_transition", start_transition_not_implemented)
    return transition != start_transition_not_implemented

def start_transition_to_boot_stage(from_boot_stage, to_boot_stage, timeout):
    '''
    Starts the boot stage transition to the destination boot stage.

    Parameters
    ----------
    from_boot_stage: str
        Name of the boot stage the target is currently at. (i.e. PowerOff, Fivrbreak, EFI)

    to_boot_stage: str
        Name of the boot stage the method will transition to. (i.e. PowerOff, Fivrbreak, EFI)

    timeout: int
        Max time in milliseconds this transition should take.
    '''
    transition = get_transition_value(from_boot_stage, to_boot_stage, "start_transition", start_transition_not_implemented)
    transition(from_boot_stage, to_boot_stage)

