import json

class execution_data:

    def __init__(self):
        self.testflows =[]

class TestFlow:
    
    def __init__(self,testflowname, testflowguid, algorithm):
        self.testflowname = testflowname
        self.testflowguid = testflowguid
        self.algorithm = algorithm
        self.testgroup =[]
    

class TestGroup:

    def __init__(self, testgroupname,boot_stage):
        self.testgroupname = testgroupname
        self.boot_stage = boot_stage
        #self.env_conditions = [] // revisit if needed to populate environment conditions
        self.tests = []


class Test():

    def __init__(self,name,path,testtype, timeout):
        self.testname  = name
        self.testpath = path
        self.testType = testtype
        self.timeout = timeout
