import sys
if r'C:\PythonSV\pontevecchio\fivr\scripts' not in sys.path: sys.path.append(r'C:\PythonSV\pontevecchio\fivr\scripts')
from os.path import exists
import BasicTools as bt
from Configuration import Configuration
import fusion
import time


class DroopMeasureHelper():

    def __init__(self, sv = None):
        self.sv = sv
        self.rail_cdt = None
        self.tilesv = None
        self.acm_data_format = "0x807F{}00"
        self.config = Configuration.getInstance()
        self.droop_section = "DroopConfig" 
        self.api = fusion.api_access()
        pass
    
    def set_voltage(self, voltage, tile, rail):
        print("Setting voltage {} for rail {} on tile {}".format(voltage, rail, tile))
        #rails = ['FIVR_EU0','FIVR_EU2','FIVR_EU4','FIVR_EU6','FIVR_EU8','FIVR_EU10','FIVR_EU12','FIVR_EU14']
        #for rail1 in rails:
        tool = bt.BasicTools(rail, tile)
        tool.Enable_protection = False
        tool.Enable_logger = False
        try:
            tool.VoltageSet(voltage) 
        except Exception as ex:
            print("Failed to set voltage: Trying again "+ ex)

    def dc_calibration(self, voltage, tile, rail, max_threshold = 0xFF):
        print("Measuring DC calibration at voltage {}".format(voltage))
        print("Setting comparator")
        self.set_voltage(voltage, tile, rail)
        self.setup_comparator_code(tile, rail)
        threshold_max = max_threshold
        threshold = 0x0
        self.set_threshold_aggressive_override(threshold)    
        print("Calibration code is {}".format(self.read_calibration_code()))

        while True:
            print("Checking for threshold {}".format(threshold))
            if threshold > threshold_max:
                break

            self.set_threshold_aggressive_override(threshold)    
            if self.read_calibration_code() > 0:
                break
            else:
                threshold = threshold + 1
        return threshold

    def droop_measurement(self, voltage, tile, rail):
        threshold = self.dc_calibration(voltage, tile, rail)
        dc_calibration = threshold
        command_to_execute = self.config.get_config_value(self.droop_section, 'COMMAND')
        print("DC calibration finished , threshold hit during calibration is {}".format(dc_calibration))
        if self.execute_test():
            print("Successfully executed test and now trying to read droop for executed content")
        else:
            print("Failed to execute test.Droop calculation failed for content")
        
        self.setup_comparator_code(tile, rail)
        threshold = 0xff

        self.set_threshold_aggressive_override(threshold)
        self.read_droop_status()

        #while threshold > 0x0:
        #    self.set_threshold_aggressive_override(threshold)
        #    if self.read_droop_status() == 0:
        #        break
        #    threshold = threshold -1
        print("DC Cablibration :{} Content Threshold: {}".format(dc_calibration, threshold))
        measured_droop = (dc_calibration - threshold)*2.5
        return measured_droop
    
    def execute_test(self):
        try:
            command = self.config.get_config_value('InlineShmoo','COMMAND')
            self.api.marionette.set_ethernet_rcf()
            print("Executing test with command {} ".format(command))
            test_Status = self.api.marionette.execute_command(command)
            print("Test Status:-  {}".format(test_Status))
            if 'ocelot main: result=success' in test_Status.lower():
                return True
        except: 
            return False
        return False
    
    def set_threshold_aggressive_override(self, threshold):
        print("Setting threshold to {}".format(threshold))
        if threshold <0x10:
            threshold_str = str(hex(threshold))[2:].ljust(2,'0')[::-1]
        else:
            threshold_str = str(hex(threshold))[2:].ljust(2,'0')
        print("Threshold string is  {}".format(threshold_str))
        acm_data = self.acm_data_format.format(threshold_str)
        print("Programming acm_data {}".format(acm_data))
        self.execute_tap2acm(0x0, 0x9C,int(acm_data,16))

    def read_droop_status(self):
        self.execute_tap2acm(0x1,0x40, 0x0)
        return self.read_acm2tap()

    def read_calibration_code(self):
        self.execute_tap2acm(0x1,0xC0, 0x0)
        acm_tap = self.read_acm2tap()
        agg_comparator_output = str(bin(acm_tap))[2:][2] # covert the acm_tap data(hex) to binary and take out 0b and take 29th bit, 3nd from left (31-0,30-1, 29-2)
        print("comparator output :- {}".format(agg_comparator_output))
        return int(agg_comparator_output)
    
    def setup_for_rail(self, tile, rail):
        print("Setting up rail for tile {} and rail {}".format(tile, rail))
        import time
        time.sleep(5)
        if not self.tilesv:
            self.setup_for_tile(tile)

        if '10' in rail:
            self.rail_cdt = self.tilesv.taps.pvc_cdt_compute_50
        elif '12' in rail:
            self.rail_cdt = self.tilesv.taps.pvc_cdt_compute_60
        elif '14' in rail:
            self.rail_cdt = self.tilesv.taps.pvc_cdt_compute_70
        elif '0' in rail:
            self.rail_cdt = self.tilesv.taps.pvc_cdt_compute_00
        elif '2' in rail:
            self.rail_cdt = self.tilesv.taps.pvc_cdt_compute_10
        elif '4' in rail:
            self.rail_cdt = self.tilesv.taps.pvc_cdt_compute_20
        elif '6' in rail:
            self.rail_cdt = self.tilesv.taps.pvc_cdt_compute_30
        elif '8' in rail:
            self.rail_cdt = self.tilesv.taps.pvc_cdt_compute_40
       

    def setup_for_tile(self, tile):
        if tile == 1:
            self.tilesv = self.sv.gfxcard0.tile1
        else:
            self.tilesv = self.sv.gfxcard0.tile0

    def setup_comparator_code(self, tile, rail):
        if not self.sv:
            from Helper.instances import InstanceFactory
            self.sv = InstanceFactory.getInstance().get_python_sv_instance()
        if not self.rail_cdt:
            self.setup_for_rail(tile, rail)

        self.rail_cdt.cdt_tapchicken = 0x00002001
        print("TAP chicken :{}".format(self.rail_cdt.cdt_tapchicken))
        self.rail_cdt.cdt_tap2acm = 0x00000000178
        print("TAP 2 ACM :{}".format(self.rail_cdt.cdt_tap2acm))
        self.rail_cdt.cdt_tap2acm = 0x040FA040040
        print("TAP 2 ACM :{}".format(self.rail_cdt.cdt_tap2acm))
        
    def execute_tap2acm(self, command, address, acm_data):
        command_str_to_set =  '0b'+str(bin(acm_data)[2:])+str(bin(address)[2:])+str(bin(command)[2:])
        command_to_set =  int(command_str_to_set,2)
        print("Command to set is {}".format(hex(command_to_set)))
        self.rail_cdt.cdt_tap2acm = command_to_set
        
    
    def read_acm2tap(self):
        return self.rail_cdt.cdt_acm2tap       
