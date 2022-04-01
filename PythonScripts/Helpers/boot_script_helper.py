import pysvtools.bootscript.BootVars as boot_vars

class BootScriptHelper():

    def __init__(self):
        pass

    def run_pcie_screen(self):
        print("Running PCIE test")
        from toolext.bootscript import boot as b
        if b.boot_vars.screening.pcie_screen() == boot_vars.SUCCESS:
            return "Passed"
        else:
            return "Failed"
        
    def run_mdfi_screen(self):
        print("Running MDFI test")
        from toolext.bootscript import boot as b
        if b.boot_vars.screening.mdfi_screen() == boot_vars.SUCCESS:
            return "Passed"
        else:
            return "Failed"

    def run_gt_screen(self):
        print("Running GT test")
        from toolext.bootscript import boot as b
        if b.boot_vars.screening.gt_screen() == boot_vars.SUCCESS:
            return "Passed"
        else:
            return "Failed"
    
    def run_hbm_screen(self):
        print("Running GT test")
        from toolext.bootscript import boot as b
        if b.boot_vars.screening.hbm_screen() == boot_vars.SUCCESS:
            return "Passed"
        else:
            return "Failed"
    
    def run_anr_screen(self):
        print("Running GT test")
        from toolext.bootscript import boot as b
        if b.boot_vars.screening.anr_screen() == boot_vars.SUCCESS:
            return "Passed"
        else:
            return "Failed"