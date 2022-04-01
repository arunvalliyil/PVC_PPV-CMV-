import sys
import os
from Helpers.Profilers.pvc_profiler import PVCProfiler

from contextlib import contextmanager

class BasePowerControl:
    """
    Provides basic Power Control operations for TTK and PowerSplitter Command Line
    """
    def __init__(self, ttk_path = r'C:\\SVShare\\user_apps\\TTK2', ttk_python_path = r'C:\\SVShare\\user_apps\\TTK2\\API\\Python', power_splitter_cli_path = r'c:\\SVSHARE\\User_Apps\\PowerSplitter\\PowerSplitterCL.exe'):
        """
        Initializes Power Control Operations for TTK and Power Splitter Command Line

        Parameters
        ----------
        ttk_path : str, Optional
            Path to the install location of TTK2. Defaults to C:\\SVShare\\user_apps\\TTK2
        ttk_python_path : str, Optional
            Path to Python API package of TTK2. Defaults to C:\\SVShare\\user_apps\\TTK2\\API\\Python
        power_splitter_cli_path: str, Optional
            Path to the Power Splitter Command Line Application. Defaults to c:\\SVSHARE\\User_Apps\\PowerSplitter\\PowerSplitterCL.exe
        """
        self.ttk_path = ttk_path
        self.ttk_python_path = ttk_python_path
        self.power_splitter_cli_path = power_splitter_cli_path

    def turn_on_power_splitter(self, port_number):
        """
        Turns on the power splitter using the provided port number

        Parameters
        ----------
        port_number : int
            The port number that needs to be turned on
        """
        print("Turning on power using power control port %d" % port_number)
        with self.power_splitter_interface() as p_interface:
            p_interface.PortOn(port_number)

    def turn_off_power_splitter(self, port_number):
        """
        Turns off the power splitter using the provided port number

        Parameters
        ----------
        port_number : int
            The port number that needs to be turned off
        """
        try:
            with self.power_splitter_interface() as p_interface:
                p_interface.PortOff(port_number)
            PVCProfiler().StopProfiling()
        except:
            print("Failed to turn off power splitter port {}".format(port_number))

    def is_port_on(self, port_number):
        """
        Checks if the provided port number is turned on

        Parameters
        ----------
        port_number : int
            The port number that needs to be checked
        
        Returns
        -------
        bool
            True is the port is turned on
        """
        with self.power_splitter_interface() as p_interface:
            bool_port_state = p_interface.GetPortState(port_number)
        return bool_port_state

    def turn_on_power_splitter_cli(self, port_number, power_splitter_cli_path = None):
        """
        Turns on the power splitter using the provided port number using the executable CLI

        Parameters
        ----------
        port_number : int
            The port number that needs to be turned on

        power_splitter_cli_path: str, None
            The install location of the power splitter CLI path. Will default to 
            c:\\SVSHARE\\User_Apps\\PowerSplitter\\PowerSplitterCL.exe
        """
        print("Turning on the power splitter to turn on the target.") 
        if power_splitter_cli_path is None:
            power_splitter_cli_path = self.power_splitter_cli_path
        os.system("%s portpower %d True" % (power_splitter_cli_path, port_number))

    def turn_off_power_splitter_cli(self, port_number, power_splitter_cli_path = None):
        """
        Turns off the power splitter using the provided port number using the executable CLI

        Parameters
        ----------
        port_number : int
            The port number that needs to be turned off

        power_splitter_cli_path: str, None
            The install location of the power splitter CLI path. Will default to 
            c:\\SVSHARE\\User_Apps\\PowerSplitter\\PowerSplitterCL.exe
        """
        print("Turning off the power splitter to turn on the target.")
        if power_splitter_cli_path is None:
            power_splitter_cli_path = self.power_splitter_cli_path
        os.system("%s portpower %d False" % (power_splitter_cli_path, port_number))

    @contextmanager
    def power_splitter_interface(self):
        """
        Creates and manages a new instance of the Power Control object that can 
        be used in a with statement
        """
        if self.ttk_path not in sys.path:
            sys.path.append(self.ttk_path)
        if self.ttk_python_path not in sys.path:
            sys.path.append(self.ttk_python_path)
        from TTK2_PowerControl import Power_Control

        p_interface = Power_Control()
        try:
            p_interface.OpenPowerSplitter()
            yield p_interface
        finally:
            p_interface.Close()
