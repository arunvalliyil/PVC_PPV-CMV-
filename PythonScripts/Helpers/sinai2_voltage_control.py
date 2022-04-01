import sys, time, math

class Sinai2VoltageControl:    
    def __init__(self):
        '''
        This class defines voltage control using Sinai2

        Usage
        -----
        from fusion_Helpers.sinai2_voltage_control import Sinai2VoltageControl
        sinai_obj = Sinai2VoltageControl()
        '''
        if u'C:\\VFT64\\Python Scripts' not in sys.path: sys.path.append(u'C:\\VFT64\\Python Scripts')
        from VFTWrapperClass import VFTWrapper
        PASS_THROUGH_MODE = 0
        SEMI_TRANSPARENT_MODE = 1
        INTERVENTION_MODE = 2
        self.vft_wrapper = VFTWrapper()
        self.vft_wrapper.Init("C:\\VFT64\\OsirisHal.ini")

    def _check_error_code(self, error_code):
        if error_code != 0:
            res, last_error = self.vft_wrapper.GetSinai2LastError()
            raise RuntimeError("SINAI2 ERROR: {0}".format(last_error))

    def get_svid_names(self):
        '''
        Gets all the available SVID Names

        Returns
        -------
        List of string
            List of all SVID Names
        
        Raises
        ------
        RuntimeError
            If the SINAI2 raises an error when attempting call the API
        '''
        svid_names = []
        error_code , svid_name , valid = self.vft_wrapper.GetFirstSvidVRName()
        self._check_error_code(error_code)
        while (svid_name != ""):
            svid_names.append(svid_name)
            error_code , svid_name , valid = self.vft_wrapper.GetNextSvidVRName()
            self._check_error_code(error_code)
        return svid_names

    def read_all_svid_voltages(self):
        '''
        Reads all the available SVIDs

        Returns
        -------
        Dicitionary of string and voltages
            Float Voltage mapped to the corresponding string name
        
        Raises
        ------
        RuntimeError
            If the SINAI2 raises an error when attempting call the API
        '''
        print("Reading SVID voltages")
        svid_names = self.get_svid_names()
        svid_values = {}
        for svid_name in svid_names:
            time.sleep(0.3)
            svid_values[svid_name] = self.read_svid_voltage(svid_name)
        return svid_values

    def read_svid_voltage(self, svid_name):
        '''
        Reads the SVID voltage for the provided name

        Parameters
        ----------
        svid_name: string
            SVID Voltage name to be read

        Returns
        -------
        float
            SVID Voltage value

        Raises
        ------
        RuntimeError
            If the SINAI2 raises an error when attempting call the API
        '''
        print("Reading SVID voltage {0}".format(svid_name))
        error_code , voltage = self.vft_wrapper.GetSvidVRVoltage(svid_name)
        self._check_error_code(error_code)
        print("{0}: {1}".format(svid_name, voltage))
        return voltage

    def set_svid_voltage(self, svid_name, voltage):
        '''
        Sets the SVID voltage for the provided name

        Parameters
        ----------
        svid_name: string
            SVID Voltage name to be read
        voltage: float
            SVID Voltage to be set
            
        Raises
        ------
        RuntimeError
            If the SINAI2 raises an error when attempting call the API
        '''
        print("Setting SVID voltage {0} to {1}".format(svid_name, voltage))

        if self.get_svid_operation_mode() is not INTERVENTION_MODE:
            print("Setting SVID Mode to INTERVENTION so we can control voltages.")
            self.set_semi_transparent_mode()
            time.sleep(0.3)
            self.set_intervention_mode()
        error_code = self.vft_wrapper.SetSvidVRVoltage(svid_name, voltage)
        self._check_error_code(error_code)

    def _get_svid_operation_mode_name(self, operation_mode):
        if operation_mode == PASS_THROUGH_MODE:
            return "PASS THROUGH MODE"
        elif operation_mode == SEMI_TRANSPARENT_MODE:
            return "SEMI TRANSPARENT MODE"
        elif operation_mode == INTERVENTION_MODE:
            return "INTERVENTION MODE"
        else:
            return "UNDEFINED"

    def get_svid_operation_mode(self):
        '''
        Gets the operation mode of the SVID

        Returns
        -------
        int : {0, 1, 2}
            Integer value corresponding to the operation mode

        Raises
        ------
        RuntimeError
            If the SINAI2 raises an error when attempting call the API
        '''
        error_code, svid_operation_mode = self.vft_wrapper.GetSvidOperationMode()
        self._check_error_code(error_code)
        return svid_operation_mode

    def get_svid_operation_mode_name(self):
        '''
        Gets the SVID operation mode string NameError

        Returns
        -------
        string : {"PASS THROUGH MODE", "SEMI TRANSPARENT MODE", "INTERVENTION MODE", "UNDEFINED" }

        Raises
        ------
        RuntimeError
            If the SINAI2 raises an error when attempting call the API
        '''
        return self._get_svid_operation_mode_name(self.get_svid_operation_mode())

    def set_svid_operation_mode(self, operation_mode):
        '''
        Sets the SVID operation mode to the provided integer ValueError

        Parameters
        ----------
        int : { 0, 1, 2 }
            Integer qualified operation mode

        Raises
        ------
        ValueError
            If the provided operation mode is not 0, 1 or 2
        RuntimeError
            If the SINAI2 raises an error when attempting call the API
        '''
        if operation_mode not in range(0, 3):
            raise ValueError("Only operation modes of up to 2 are supported")
        print("Setting SVID operation mode to {0}".format(self._get_svid_operation_mode_name(operation_mode)))
        error_code = self.vft_wrapper.SetSvidOperationMode(operation_mode)
        self._check_error_code(error_code)

    def set_semi_transparent_mode(self):
        '''
        Sets the SVID to semi transparent mode
        '''
        self.set_svid_operation_mode(SEMI_TRANSPARENT_MODE)

    def set_pass_through_mode(self):
        '''
        Sets the SVID to pass through mode
        '''
        self.set_svid_operation_mode(PASS_THROUGH_MODE)

    def set_intervention_mode(self):
        '''
        Sets the SVID to intervention mode
        '''
        self.set_svid_operation_mode(INTERVENTION_MODE)

    def select_voltage_monitor_channels_by_name(self, channels):
        '''
        Selects the channels that need to be monitored for voltage

        Parameters
        ---------
        channels: list of string
            List of channel names

        Raises
        ------
        RuntimeError
            If the SINAI2 raises an error when attempting call the API
        '''
        error_code = self.vft_wrapper.SelectVoltMonMonitorChannelsByName(channels)
        self._check_error_code(error_code)

    def get_voltage_monitor_active_channel_names(self):
        '''
        Gets the list of active channels on which voltages are being monitored

        Returns
        -------
        list of string
            List of channel names which are being monitored
        
        Raises
        ------
        RuntimeError
            If the SINAI2 raises an error when attempting call the API
        '''
        error_code, id, name, type = self.vft_wrapper.GetFirstActiveVmonChannel()
        self._check_error_code(error_code)
        channel_names = []
        while (id != 255):
            channel_names.append(name)
            error_code, id, name, type = self.vft_wrapper.GetNextActiveVmonChannel()
            self._check_error_code(error_code)
        return channel_names

    def clear_voltage_monitor_min_max_by_names(self, channels):
        '''
        Clears the min and max voltages for the specified channels

        Parameters
        ----------
        channels: list of string
            List of channel names whose Min and Max Voltages have to be cleared
        
        Raises
        ------
        RuntimeError
            If the SINAI2 raises an error when attempting call the API
        '''
        error_code = self.vft_wrapper.ClearVoltMonMinMaxByName(channels)
        self._check_error_code(error_code)
    
    def get_voltage_monitor_max_by_names(self, channels):
        '''
        Gets the Max monitored voltages in the specified channel names

        Parameters
        ----------
        channels: list of string
            List of channel names whose Max Voltages are requested
        
        Returns
        -------
        list of float
            Ordered list of float for the voltage monitor names

        Raises
        ------
        RuntimeError
            If the SINAI2 raises an error when attempting call the API
        '''
        #The min and max apis are switched. We have to ask for  the min to get the max value.
        error_code, max_values = self.vft_wrapper.GetVoltMonVoltMinByName(list(channels))
        self._check_error_code(error_code)
        return max_values

    def get_voltage_monitor_min_by_names(self, channels):
        '''
        Gets the Min monitored voltages in the specified channel names

        Parameters
        ----------
        channels: list of string
            List of channel names whose Min Voltages are requested
        
        Returns
        -------
        list of float
            Ordered list of float for the voltage monitor names
            
        Raises
        ------
        RuntimeError
            If the SINAI2 raises an error when attempting call the API
        '''
        #The min and max apis are switched. We have to ask for  the min to get the max value.
        error_code, min_values = self.vft_wrapper.GetVoltMonVoltMaxByName(list(channels))
        self._check_error_code(error_code)
        return min_values

    def get_voltage_monitor_avg_by_names(self, channels):
        '''
        Gets the Average of monitored voltages in the specified channel names

        Parameters
        ----------
        channels: list of string
            List of channel names whose Average Voltages are requested
        
        Returns
        -------
        list of float
            Ordered list of float for the voltage monitor names
            
        Raises
        ------
        RuntimeError
            If the SINAI2 raises an error when attempting call the API
        '''
        error_code, avg_values = self.vft_wrapper.GetVoltMonVoltAvgByName(list(channels))
        self._check_error_code(error_code)
        return avg_values

    def profile_voltage_for_fixed_time(self, hold_time, channels):
        '''
        Profiles select channels for a specified amount of time

        Parameters
        ----------
        hold_time: int
            The time to profile the channel in seconds
        channels: list of string
            List of channel names to be profiled

        Returns
        -------
        List of StatisticalData object
            One object for each channel that was monitored

        Raises
        ------
        RuntimeError
            If the SINAI2 raises an error when attempting call the API
        '''
        channel_names = self.get_voltage_monitor_active_channel_names()
        self.select_voltage_monitor_channels_by_name(channel_names)
        self.clear_voltage_monitor_min_max_by_names(channels)
        time.sleep(hold_time)
        return self.get_voltage_monitor_statistics_by_names(channels)

    def get_voltage_monitor_statistics_by_names(self, channels):
        '''
        Gets the voltage monitor statistics for select channels

        Parameters
        ----------        
        channels: list of string
            List of channel names whose data is requested

        Returns
        -------
        List of StatisticalData object
            One object for each channel that was monitored

        Raises
        ------
        RuntimeError
            If the SINAI2 raises an error when attempting call the API
        '''
        max_values = self.get_voltage_monitor_max_by_names(channels)
        min_values = self.get_voltage_monitor_min_by_names(channels)
        avg_values = self.get_voltage_monitor_avg_by_names(channels)
        statistics = []
        i = 0
        for channel in channels:
            stat = StatisticalData(channel)
            stat.max = max_values[i]
            stat.min = min_values[i]
            stat.avg = avg_values[i]
            statistics.append(stat)
            i = i + 1
        return statistics

class StatisticalData(object):
    
    def __init__(self, channel):
        self.channel = channel
        self.max = None
        self.min = None
        self.avg = None
        
    def __repr__(self):
        return self.__str__()
    
    def __str__(self):
        return "Channel: {0}, Max: {1}, Min: {2}, Avg: {3}".format(self.channel, self.max, self.min, self.avg)