import sys
from . import instances

class ParametricReader():

    def __init__(self):
        print("Initiating unit Parametric reader")
        self.factory = instances.InstanceFactory.getInstance()

    def read_dss_from_dff(self):
        api = self.factory.get_fusion_instance()
        return 50,32


