class fpdutility():
    
    def __init__(self, fusion_api):
        self.api = fusion_api
    
    def get_defined_boot_stages(self):
        boot_stages = []
        for boot_stage in self.api.product_definition.BootStages:
            boot_stages.append(boot_stage.StageName.replace('Stage',''))
        return boot_stage
    
    def get_marionette_serial_port(self):
        for boot_stage in self.api.product_definition.BootStages:
            if hasattr(boot_stage,'MarionetteTransport'):
                if hasattr(boot_stage.MarionetteTransport,'ComPortNumber'):
                    print("Found serial marionette transport configured to Com Port {}".format(boot_stage.MarionetteTransport.ComPortNumber))
                    return boot_stage.MarionetteTransport.ComPortNumber
        print("Could not find a serial port configured boot stage")
        return 0
    
    def get_environment_limits(self, condition_name):
        print("Extracting limits for environment condition {}".format(condition_name))
        for environment in self.api.product_definition.EnvironmentalConditionDescriptors:
            if environment.name in condition_name and hasattr(environment,'Max'):
                return {"Max":environment.Max, "Min":environment.Min,"Step": environment.Step}
            elif environment.name in condition_name and hasattr(environment,'DiscreteValues'):
                return {"DiscreteValues": environment.DiscreteValues}
        
                
            
                
                
                
                