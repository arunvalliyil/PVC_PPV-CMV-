import inspect
import json, os, sys,time
from Helpers.Configuration import Configuration
from Helpers import unit_parametric_reader
from Helpers.mode_identifier import ModeIdentifier
from Helpers.fusionfpdutility import fpdutility
from Helpers.mid_target_identifier import MidTargetIdentifier

class InstanceFactory:

    _instance = None

    '''
    This class creates instances for common items that will be 
    used throughout a session
    '''
    def __init__(self, dal_path = r'C:\Intel\DAL'):
        '''
        Initializes the DAL path and sets up constants for lazy initialize instances

        Paramaters
        ----------
        dal_path: str, Optional
            The path to the dal install, defaults to C:\Intel\DAL
        '''
        self.config = Configuration.getInstance()
       
        self.dal_path = dal_path
        self.itp = None
        self.api = None
        self.sv = None
        self.fpd_utility = None
        self.pvc_instanceid = None
        self.mid_target_instanceid = None


    @staticmethod
    def getInstance():
        if InstanceFactory._instance ==  None:
            InstanceFactory._instance = InstanceFactory()
        return InstanceFactory._instance

    def get_itp_instance(self):
        '''
        Lazily initializes and returns the ITP/IPC instance that was set up for the session

        Returns
        -------
        itp or ipc baseacess instance
        '''
        try:
            import ipccli
            self.itp = ipccli.baseaccess()
        except Exception as ex:
            print("Failed to get itp instance {}".format(ex))
         
        return self.itp

    def get_fusion_instance(self):
        '''
        Lazily initialized and returns the Fusion CellAgent API instance

        Returns
        -------
        Fusion CellAgent API instance
        '''
        if self.api is None:
            import fusion
            self.api = fusion.api_access()
        return self.api
  
    def get_power_control(self):
        '''
        Lazily initialize and return the relevent target power control
        Returns
        ---------
        TargetPowerControl instance
        '''
        from FusionBaseClass.target_power_control import TargetPowerControl
        import PowerControl
        for name,obj in inspect.getmembers(sys.modules['PowerControl']):
            if inspect.isclass(obj) and issubclass(obj,TargetPowerControl)and obj is not TargetPowerControl:
                return obj()

    def get_installation_mode(self):
        identifier = ModeIdentifier.getInstance()
        return identifier.identify_mode()

    def get_boot_stage_controller(self, boot_stage):
        from FusionBaseClass.boot_stage_controller import BootStageController
        from  StageTransitions import StageControllers
        for name,obj in inspect.getmembers(sys.modules['StageTransitions.StageControllers']):
            if inspect.isclass(obj) and issubclass(obj,BootStageController):
                if obj.Stage_Handled == boot_stage:
                    return obj()
    
    def get_all_boot_stages(self):
        all_controllers = []
        from FusionBaseClass.boot_stage_controller import BootStageController
        from  StageTransitions import StageControllers
        for name,obj in inspect.getmembers(sys.modules['StageTransitions.StageControllers']):
            if inspect.isclass(obj) and issubclass(obj,BootStageController) and not self.is_abstract(obj):
                if obj not in all_controllers:
                    all_controllers.append(obj)
        return all_controllers
    
    def get_python_sv_instance(self):
        itp = self.get_itp_instance()
        if not self.sv:
            from namednodes import sv
            sv.refresh()
            import __main__
            __main__.sv = sv
            self.sv = sv
        return self.sv 
    
    def get_parametric_reader_instance(self):
        return unit_parametric_reader.ParametricReader()

    def is_abstract(self,cls):
        return bool(getattr(cls, "__abstractmethods__", False))

    def get_all_sub_device_identifiers(self, tile_count):
        with open(os.path.join(sys.path[0],'subdevice_identifier.json')) as f:
            data = json.load(f)
        return data[str(tile_count)]
    
    def get_fpd_utilities(self):
        if self.fpd_utility is None:
            self.fpd_utility = fpdutility(self.get_fusion_instance())
        return self.fpd_utility

    def identify_mid_target(self):
        return MidTargetIdentifier.getInstance().identify_mid_target()

    def identify_pvc_port(self):
        if self.pvc_instanceid:
            return self.pvc_instanceid

        itp = self.getInstance().get_itp_instance()
        port_tap_names = [x.children[0].children[0].name for x in itp.debugports]
        DEBUGPORT_CARD = port_tap_names.index('PVC_CLTAP0')
        self.pvc_instanceid = DEBUGPORT_CARD
        print("DEBUGPORT_CARD identified as {}".format(self.pvc_instanceid))
        return DEBUGPORT_CARD
    
    def identify_mid_target_port(self):
        if self.mid_target_instanceid:
            return self.mid_target_instanceid
        
        DEBUGPORT_HOST = -1
        itp = self.getInstance().get_itp_instance()
        port_tap_names = [x.children[0].children[0].name for x in itp.debugports]
        if 'ICX0_CLTAP0' in port_tap_names:
            DEBUGPORT_HOST = port_tap_names.index('ICX0_CLTAP0')
        elif 'SPR0_CLTAP0' in port_tap_names:
            DEBUGPORT_HOST = port_tap_names.index('SPR0_CLTAP0')
        
        self.mid_target_instanceid = DEBUGPORT_HOST
        if DEBUGPORT_HOST == -1:
            print("XDP not connected to mid target")
        else:
            print("DEBUGPORT_HOST identified as {}".format(self.mid_target_instanceid))
        return DEBUGPORT_HOST
