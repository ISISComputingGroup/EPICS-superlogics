import unittest

from utils.channel_access import ChannelAccess
from utils.ioc_launcher import get_default_ioc_dir
from utils.test_modes import TestModes
from utils.testing import IOCRegister, get_running_lewis_and_ioc, skip_if_recsim

DEVICE_PREFIX = "SPRLG_01"
OVER_RANGE = 9999.9
UNDER_RANGE = -9999.9


IOCS = [
    {
        "name": DEVICE_PREFIX,
        "directory": get_default_ioc_dir("SPRLG"),
        "macros": {
            "TYPE": "STRAIN",
        },
        "emulator": "superlogics",
        "lewis_protocol": "strain",
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

    def _set_input(self, value):
        if IOCRegister.test_mode == TestModes.DEVSIM:
            self._lewis.backdoor_run_function_on_device("set_channel", [0, value])
        elif IOCRegister.test_mode == TestModes.RECSIM:
            self._ioc.set_simulated_value("SIM:VALUE", value)

    def test_GIVEN_input_value_set_WHEN_value_read_THEN_value_correct(self):
        value = 200.0
        self._set_input(value)
        self.ca.assert_that_pv_is("VALUE", value)

    def test_GIVEN_input_value_over_range_THEN_input_in_alarm(self):
        self._set_input(OVER_RANGE)
        self.ca.assert_that_pv_alarm_is("VALUE", self.ca.Alarms.MAJOR, timeout=30)

    def test_GIVEN_input_value_under_range_THEN_input_in_alarm(self):
        self._set_input(UNDER_RANGE)
        self.ca.assert_that_pv_alarm_is("VALUE", self.ca.Alarms.MAJOR, timeout=30)

    @skip_if_recsim("Need emulator to test disconnection logic.")
    def test_WHEN_device_disconnected_THEN_input_in_alarm(self):
        pv = "VALUE"

        self.ca.assert_that_pv_alarm_is(pv, self.ca.Alarms.NONE, timeout=30)

        with self._lewis.backdoor_simulate_disconnected_device():
            self.ca.assert_that_pv_alarm_is(pv, self.ca.Alarms.INVALID, timeout=30)

        self.ca.assert_that_pv_alarm_is(pv, self.ca.Alarms.NONE, timeout=30)
