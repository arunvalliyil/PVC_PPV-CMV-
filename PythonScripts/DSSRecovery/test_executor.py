import sys,os,errno,pickle
import os.path

from os import listdir
from os.path import isfile, join
from pathlib import Path


class TestExecutor():

    Passed = "Passed"
    Failed = "Failed"
    Hung = "Hung"

    def __init__(self, config, instance):
        self.config = config
        self.api = instance.get_fusion_instance()
        self.fpd_utility = instance.get_fpd_utilities()
    
    def execute_test(self, tile, test_flow, test_group):
        serial_port = self.fpd_utility.get_marionette_serial_port()
        self.api.marionette.set_serial(serial_port)

        test_look_up_file = self.config.get_config_value('DSSRecovery','TEST_LIST_PATH')
        print("Checking the master file {}".format(test_look_up_file))
        command_to_send = ''
        ed1 = pickle.load(open(test_look_up_file,"rb"))
        if os.path.isfile(test_look_up_file):
            print("Master list exist")
            if not ed1:
                print("Failed to read pickle")

        if ed1:
            flow_to_execute = next(filter(lambda x:x.testflowname == test_flow ,ed1.testflows), None)
            if flow_to_execute:
                test_group_to_execute = next(filter(lambda x:x.testgroupname in test_group, flow_to_execute.testgroup), None)
                print('Found test group to execute {}'.format(test_group_to_execute.testgroupname))
                if test_group_to_execute:
                    for test in test_group_to_execute.tests:
                        test_result = ''
                        try:
                            print("Executing an efi test {} of test type {}".format(test.testname,test.testType))
                            if test.testType == 'Grits EFI':
                                print("Executing an efi test {}".format(test.testname))
                                test_result = self.send_marionette_command(test, serial_port)
                            else:
                                print("Executing an python test {} with command {}".format(test.testname, command_to_send))
                                return exec(command_to_send)
                        except Exception as e:
                            print("Failed to execute test {}".format(e))

                        if test_result != "Passed":
                            return test_result
                        print("Test {} executed successfully continuing test execution".format(test.testname))
                else:
                    print("Fatal Error: Could not find the test group {} to execute".format(test_group_to_execute.testgroupname))
                    raise NameError("Could not find test group {}  under test_flow {} in master list at {}".format(test_group_to_execute.testgroupname, test_flow_to_execute.testflowname,test_look_up_file))

            else:
                print("Fatal Error: Could not find the test flow {} to execute".format(test_flow))
                raise NameError("Could not find test_flow {} in master list at {}".format(test_flow,test_look_up_file))

            return "Passed"
        else:
            print("Missing master file at {}".format(test_look_up_file))
            raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), test_look_up_file)
 

    def send_marionette_command(self, test, serial_port):
        command_to_send = "{} {}".format(test.testpath, self.calculate_additional_params(test.testname))
        print("Executing command {}".format(command_to_send))
        return self.api.marionette.execute_command(command_to_send,test.timeout,'serial',serial_port)

    
    def calculate_additional_params(self, testname):
        return "-did 201"



