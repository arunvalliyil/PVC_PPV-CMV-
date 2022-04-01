
from Helpers.instances import InstanceFactory
import subprocess,os,time
from Helpers.Configuration import Configuration

class PhoronixExecuter():

    def __init__(self):
        self.mobaxterm_path = r'C:\STHI\MobaXterm\MobaXterm_Portable_v20.6\MobaXterm_Personal_20.6.exe'
        self.instance = InstanceFactory.getInstance()
        self.mobaxterm_exe = "MobaXterm_Personal_20.6"

    def Execute(self):
        print("Start Executing Phoronix")
        api = self.instance.get_fusion_instance()
        command = "cd /home/gfx-test/ppv/collaterals/tap_3.6_Linux/apps/Phoronix;sudo ./smallptGPUCaustic.sh"
        #command = "export OverrideDrmRegion=0;export CFESingleSliceDispatchCCSMode=0;export DISPLAY=192.168.0.1:0.0;export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/lib64:/usr/local/lib64;cd /home/gfx-test/ppv/collaterals/tap_3.6_Linux/apps/Phoronix;sudo ./smallptGPUCaustic.sh"
        try:
            api.marionette.execute_command(command, 360,'','Ethernet')
        except Exception as e:
            print("Phoronix test Timed out {}".format(e))
            return "Failed"
        
        #api.marionette.execute_command(command,120,'','Serial', 7)
        print("Execution completed;Time to verify execution")
        command_verify = "cat /home/gfx-test/ppv/collaterals/tap_3.6_Linux/apps/Phoronix/smallptGPU/smallptGPU.out"
        result = None
        try:
            result = api.marionette.execute_command(command_verify, 120,'','Ethernet')
        except Exception as e:
            print("Timed out {}".format(e))

        #result = api.marionette.execute_command(command_verify,120,'','Serial', 7)
        print("Executed Phoronix with result {}".format(result))
        if result and "[FINAL]" in result and self.read_instdone():
            return "Passed"
        return "Failed"
    
    def read_instdone(self):
        instdone = []
        sv = self.instance.get_python_sv_instance()
        instdone.extend(sv.gfxcard0.tiles.gfx.gtgp.instdone_ccs0)
        instdone.extend(sv.gfxcard0.tiles.gfx.gtgp.instdone_ccs1)
        instdone.extend(sv.gfxcard0.tiles.gfx.gtgp.instdone_ccs2)
        instdone.extend(sv.gfxcard0.tiles.gfx.gtgp.instdone_ccs3)
        for status in instdone:
            if '0xfffffffe' not in str(status):
                return False
        return True


    def Setup(self):
        api = self.instance.get_fusion_instance()
        print("Opening Mobaxterm")
        if not os.path.exists(self.mobaxterm_path):
            print("Missing Mobaxterm")
            return "Failed"
        if self.get_pid() ==0:
            os.startfile(r'C:\STHI\MobaXterm\MobaXterm_Portable_v20.6\launch.bat.lnk')
            print("Mobaxterm started")
        else:
             print("MobaXterm already running.")
        
        time.sleep(5)
        print("Cleaning old output file")
        try:
            api.marionette.set_ethernet_rcf()
            command_remove_output = 'rm /home/gfx-test/ppv/collaterals/tap_3.6_Linux/apps/Phoronix/smallptGPU/smallptGPU.out'
            result = api.marionette.execute_command(command_remove_output,120,'','Ethernet')
            print("Cleaned previous output file {}".format(result))
        except Exception as ex:
            print("Failed with error {}".format(ex))

        print("Executed all pre commands for phoronix")
        return "Passed"
    
    def Cleanup(self):
        #self.kill_program()
        return "Passed"
    

    def get_pid(self):
        import psutil,signal,os
        process_name= self.mobaxterm_exe
        for proc in psutil.process_iter():
            if process_name in proc.name():
                print("process {} with pid {}".format(process_name, proc.pid))
                return proc.pid
        return 0

    def kill_program(self):
        try:
            process_name= self.mobaxterm_exe
            import psutil,signal,os
            for proc in psutil.process_iter():
                if process_name in proc.name():
                    print("Killing process {} with pid {}".format(process_name, proc.pid))
                    pid = proc.pid
                    os.kill(pid, signal.SIGTERM)
                    print("Killed process {} with pid {}".format(process_name, proc.pid))
            return "Passed"
        except Exception as ex:
            print("Failed to kill {} with exception {}".format(process_name, ex))
            return "Failed"