'''
How to use:
    Add "elif" blocks for any environmental condition you want to support
    Create a Python script for any environmental condition you want to support (or modify the existing "environmental_condition_temperature.py" & "environmental_condition_voltage.py" to fit your needs)
'''
from ProductSpecific.environmental_condition_voltage import VoltageEnvironmentalCondition
import ProductSpecific.supported_voltages

class EnvironmentalConditions:
    def __init__(self, fusion_api):
        self.voltage_object = VoltageEnvironmentalCondition()

    def set_condition(self, condition_name, set_value):
        if condition_name in SUPPORTED_VOLTAGES:
            self.voltage_object.set_voltage(condition_name, set_value)
        else:
            raise NotImplementedError("Environmental condition not supported for set operation '{0}'".format(condition_name))

    def read_condition_set_point(self, condition_name):
        if condition_name in SUPPORTED_VOLTAGES:
            self.voltage_object.read_voltage(condition_name)
        else:
            raise NotImplementedError("Environmental condition not supported for read operation '{0}'".format(condition_name))