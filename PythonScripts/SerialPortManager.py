import sys

def close_configured_serial_port():
    import fusion
    api = fusion.api_access()
    defn = api.product_definition
    ports = []
    for config in defn.EnvironmentConfigurations[0].ComponentConfigurations:
        if hasattr(config,'ComPortNumber'):
            ports.append(config.ComPortNumber)
            print('Found Com port {}'.format(config.ComPortNumber))
    for port in ports:
        try:
            print('Configuring Port {} to python api'.format(port))
            api.serial_port.configure_then_listen_on_serial_port(int(port),'BR_115200','DB_8','NO_PARITY','ONE','NONE')
            print('setting marionette serial port to {}'.format(port))
            api.marionette.set_serial(int(port))
            print('Exiting marionette')
            api.marionette.execute_command_no_redirect('exitmarionette')
            print('closing serial port {}'.format(port))
#            api.serial_port.configure_then_listen_on_serial_port(int(port),'BR_115200','DB_8','NO_PARITY','ONE','NONE')
            api.serial_port.close_serial_port(int(port))
            print('closed serial port {}'.format(port))
        except Exception as e:
            print('Failed to close serial port {} with error {}'.format(port,str(e)))
            return 'Failed'
    return 'Passed'

def set_configured_serial_port():
    import fusion
    api = fusion.api_access()
    defn = api.product_definition
    ports = []
    for config in defn.EnvironmentConfigurations[0].ComponentConfigurations:
        if hasattr(config,'ComPortNumber'):
            ports.append(config.ComPortNumber)
            print('Found Com port {}'.format(config.ComPortNumber))
    
    for port in ports:
        try:
            print('Configuring serial port {}'.format(port))
            api.serial_port.configure_then_listen_on_serial_port(int(port),'BR_115200','DB_8','NO_PARITY','ONE','NONE')
            print('move to fs1')
            api.serial_port.send_data_string(port,'fs1:')
            import time
            time.sleep(5)
            print('running startup.nsh to start marionette agent')
            api.serial_port.send_data_string(port,'startup.nsh')
            print('Configured serial port {}'.format(port))
            print('setting marionette to port {}'.format(port))
            api.marionette.set_serial(int(port))
        except Exception as e:
            print('Failed to configure serial port {} with error {}'.format(port,str(e)))
            return 'Failed'
    
    return 'Passed'
    
    
