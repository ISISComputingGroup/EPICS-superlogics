import unittest

from parameterized import parameterized

from utils.channel_access import ChannelAccess
from utils.ioc_launcher import get_default_ioc_dir
from utils.test_modes import TestModes
from utils.testing import get_running_lewis_and_ioc, parameterized_list, IOCRegister, skip_if_recsim


DEVICE_PREFIX = "SPRLG_01"
CONNECTED_CHANNELS = [0, 1, 2, 3, 4, 5, 6]
DISCONNECTED_CHANNEL = 7
OVER_RANGE = 9999.9
UNDER_RANGE = -9999.9


IOCS = [
    {
        "name": DEVICE_PREFIX,
        "directory": get_default_ioc_dir("SPRLG"),
        "macros": {
            f"INP_{DISCONNECTED_CHANNEL}_CONNECTED": "NO"
        },
        "emulator": "superlogics",
    },
]


TEST_MODES = [TestModes.DEVSIM, TestModes.RECSIM]


class SuperlogicsTests(unittest.TestCase):
    """
    Tests for the Superlogics device
    """

    def setUp(self):
        self._lewis, self._ioc = get_running_lewis_and_ioc("superlogics", DEVICE_PREFIX)
        self._lewis.backdoor_run_function_on_device("setup")
        self.ca = ChannelAccess(device_prefix=DEVICE_PREFIX, default_wait_time=0)
        
    def _set_channel_value(self, channel, value):
        if IOCRegister.test_mode == TestModes.DEVSIM:
            self._lewis.backdoor_run_function_on_device("set_channel", [channel, value])
        elif IOCRegister.test_mode == TestModes.RECSIM:
            self._ioc.set_simulated_value(f"SIM:CHANNEL:{channel}:VALUE", value)

    @parameterized.expand(parameterized_list(CONNECTED_CHANNELS))
    def test_GIVEN_channel_value_set_WHEN_value_read_THEN_value_correct(self, _, channel):
        value = 200.0
        self._set_channel_value(channel, value)
        self.ca.assert_that_pv_is(f"CHANNEL:{channel}:VALUE", value)

    def test_GIVEN_no_channel_input_THEN_no_channel_pv(self):
        self.ca.assert_that_pv_does_not_exist(f"CHANNEL:{DISCONNECTED_CHANNEL}:VALUE")

    @parameterized.expand(parameterized_list(CONNECTED_CHANNELS))
    def test_GIVEN_channel_value_over_range_THEN_pv_in_alarm(self, _, channel):
        self._set_channel_value(channel, OVER_RANGE)
        self.ca.assert_that_pv_alarm_is(f"CHANNEL:{channel}:VALUE", self.ca.Alarms.MAJOR, timeout=30)

    @parameterized.expand(parameterized_list(CONNECTED_CHANNELS))
    def test_GIVEN_channel_value_under_range_THEN_pv_in_alarm(self, _, channel):
        self._set_channel_value(channel, UNDER_RANGE)
        self.ca.assert_that_pv_alarm_is(f"CHANNEL:{channel}:VALUE", self.ca.Alarms.MAJOR, timeout=30)

    @parameterized.expand(parameterized_list(CONNECTED_CHANNELS))
    @skip_if_recsim("Need emulator to test disconnection logic.")
    def test_WHEN_device_disconnected_THEN_pv_in_alarm(self, _, channel):
        pv = f"CHANNEL:{channel}:VALUE"

        self.ca.assert_that_pv_alarm_is(pv, self.ca.Alarms.NONE, timeout=30)

        with self._lewis.backdoor_simulate_disconnected_device():
            self.ca.assert_that_pv_alarm_is(pv, self.ca.Alarms.INVALID, timeout=30)

        self.ca.assert_that_pv_alarm_is(pv, self.ca.Alarms.NONE, timeout=30)
