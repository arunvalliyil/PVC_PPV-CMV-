import time

class BootHelper():
    
    def __init__(self):
        self.DELAY = 1
        self.WAIT_TIME = 50
        pass
    
    def wait_for_host_power_off(self, itp):
        print("Waiting for the host to power off.")
        wait_time = 0
        # while boot_vars.ipc.power_status(boot_vars.DEBUGPORT_HOST) and wait_time <= boot_vars.PWRGOODWAITTIME:
        while itp.cv.targpower and wait_time <= self.WAIT_TIME:
            time.sleep(self.DELAY)
            wait_time += (self.DELAY)
        if wait_time > self.WAIT_TIME:
            print("Timed out waiting for host power off!")
            raise TimeoutError('Timed out waiting for host warm reset!')  

    def wait_for_power_on(self, itp):
        wait_time = 0
        print("Waiting for part power on.")
        while not itp.cv.targpower and wait_time <= self.WAIT_TIME:
            time.sleep(self.DELAY)
            wait_time +=  self.DELAY
        print('Waited for {} sec to host power on!!!'.format(wait_time))

        if wait_time > self.WAIT_TIME:
            print("Timed out waiting for host power!")
            raise TimeoutError('Timed out waiting for host power!')  
    
    def wait_for_itp_refresh(self, itp):
        print("Waiting for itp refresh")
        wait_time = 0
        while 'PVC_CLTAP0' not in itp.devicelist and wait_time <= self.WAIT_TIME:
            time.sleep(self.DELAY)
            itp.forcereconfig()
            wait_time +=  self.DELAY

        print('Waited for {} sec to complete Forcereconfig!!!'.format(wait_time))

        if wait_time > self.WAIT_TIME:
            print("Timed out waiting for device list to refresh")
            raise TimeoutError('Timed out waiting for device list to refresh!')
    
    def wait_for_sv_refresh(self, sv):
        print("Waiting for itp refresh")
        wait_time = 0
        while  not hasattr(sv, 'socket0'):
            time.sleep(self.DELAY)
            sv.refresh()
            wait_time +=  self.DELAY

        print('Waited for {} sec to complete sv refresh!!!'.format(wait_time))

        if wait_time > self.WAIT_TIME:
            print("Timed out waiting for device list to refresh")
            raise TimeoutError('Timed out waiting for device list to refresh!')
    
    def wait_for_reset_break(self, itp):
        wait_time = 0
        while not itp.ishalted() and wait_time <= self.WAIT_TIME:
            time.sleep(self.DELAY)
            wait_time += self.DELAY
        
        print("***halted  {}".format(itp.ishalted()))
        if wait_time > self.WAIT_TIME:
            print("Timed out waiting for reset break!")
            raise TimeoutError('Timed out waiting for reset break!') 

    def stall_bios_with_reset_break(self, itp, sv):
        sv.socket.socket0.uncore.ubox.ncdecs.biosscratchpad6_cfg[31:16] = 0xaf00
        time.sleep(self.DELAY)
        itp.breaks.reset = 0
        print("Break reset deasserted")
        time.sleep(self.DELAY)
        itp.go()
        time.sleep(self.DELAY)
    
    def wait_for_bios_breakpoint(self, sv):
        print("Waiting for host BIOS breakpoint...")                
        wait_time = 0
        while (sv.socket.socket0.uncore.ubox.ncdecs.biosnonstickyscratchpad7_cfg[31:16] != 0xaf00 and wait_time <= self.WAIT_TIME):
            time.sleep(self.DELAY)
            wait_time += self.DELAY
        if wait_time > self.WAIT_TIME:
            print("Timed out waiting for host BIOS breakpoint!")
            raise TimeoutError('Timed out waiting for bios break!')
        print("Booted up to BIOS break point")

    def wait_for_boot_halt(self, sv):
        print("Waiting for boot halt")
        wait_time = 0
        while not self.is_at_boot_halt(sv):
            time.sleep(self.DELAY)
            wait_time += self.DELAY
        if wait_time >self.WAIT_TIME:
            print("Timed out waiting for boot halt..")
            raise TimeoutError("Waiting for boot_halt")

    def wait_for_fuse_break(self, sv):
        print("Waiting for fuse_break")
        wait_time = 0
        while not self.is_at_fuse_break(sv):
            time.sleep(self.DELAY)
            wait_time += self.DELAY
        if wait_time >self.WAIT_TIME:
            print("Timed out waiting for fuse_break..")
            raise TimeoutError("Waiting for fuse break")
        print("Reached fuse break")
    
    def wait_for_fuse_override(self, sv):
        print("Waiting for fuse override")
        wait_time = 0
        while not self.is_at_fuse_override(sv):
            time.sleep(self.DELAY)
            wait_time += self.DELAY
        if wait_time >self.WAIT_TIME:
            print("Timed out waiting for fuse_override..")
            raise TimeoutError("Waiting for fuse override")
        print("Reached fuse override.")

    def is_at_fuse_override(self, sv):
        return sv.gfxcard0.tiles.fuses.fuse_controller.intel_debug_status0.ponsendone == 1 and sv.gfxcard0.tiles.fuses.fuse_controller.intel_debug_status0.senserror != 1 and sv.gfxcard0.tiles.fuses.fuse_controller.intel_debug_status0.fcbusy != 1

    def is_at_fuse_break(self, sv):
        print("DEbug exist {}".format(sv.gfxcard0.tiles.taps.pvc_agg0.status_0.early_boot_debug_exit))
        anr_status = True
        anr_status &= sv.gfxcard0.anr.tiles.taps.anr_dfxagg_pic60.status_0.early_boot_debug_exit == 1 and sv.gfxcard0.anr.tiles.taps.anr_dfxagg_pic60.tap_ctrl.resume0 == 1
        return anr_status and sv.gfxcard0.tiles.taps.pvc_agg0.status_0.early_boot_debug_exit == 1 and sv.gfxcard0.tiles.taps.pvc_agg0.tap_ctrl.resume0 == 1

    def is_at_boot_halt(self, sv):
        return sv.gfxcard0.tiles.taps.pvc_agg0.status_0.boot_halt_post_nand_sync == 1 and sv.gfxcard0.tiles.taps.pvc_agg0.status_0.early_boot_done == 0 and sv.gfxcard0.tiles.taps.pvc_agg0.status_0.early_boot_debug_exit == 0 and sv.gfxcard0.tiles.taps.pvc_agg0.tap_ctrl.resume0 == 0

    def stall_bios_without_reset_break(self, itp,sv):
        try:
            sv.socket.socket0.uncore.ubox.ncdecs.biosscratchpad6_cfg[31:16] = 0xaf00
            print("Bios stall added without reset break")
        except:
            print("Alternate")
            sv.socket0.uncore.ubox.ncdecs.biosscratchpad6_cfg[31:16] = 0xaf00
        
        #time.sleep(self.DELAY)
        #itp.go()
        #time.sleep(self.DELAY)
          