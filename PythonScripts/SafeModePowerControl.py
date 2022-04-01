import sys
from Helpers.instances import InstanceFactory

factory = InstanceFactory.getInstance()
power_control = factory.get_power_control()
sys.modules[__name__] = power_control