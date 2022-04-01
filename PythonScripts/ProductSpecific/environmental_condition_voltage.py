'''
How to use:
    Modify the "import" statement to have access to the voltage control system you're using (Sinai is here just for reference)
    Modify the "__init__" method to instantiate the voltage control object you're using
    Modify the "set_condition" & "read_condition" methods to call the methods on the voltage control object you're using
'''



class VoltageEnvironmentalCondition:

    
    def __init__(self, fusion_api):
        self._api = fusion_api
        

    def set_condition(self, voltage_name, set_value):
        self.voltage_object.set_svid_voltage(voltage_name, set_value)

    def read_condition(self, voltage_name):
        voltage_object.read_svid_voltage(voltage_name)