from collections import OrderedDict

from lewis.devices import StateMachineDevice
from .states import DefaultState


class SimulatedSuperlogics(StateMachineDevice):
    """
    Simulated Superlogics 8019R
    """

    def _initialize_data(self):

        """

        Sets the initial state of the device

        """

        self._values = [0.]*8
        self.address = "AB"

    def _get_state_handlers(self):

        """

        Returns: states and their names

        """
        return {
            DefaultState.NAME: DefaultState(),
        }

    def _get_initial_state(self):
        """

        Returns: the name of the initial state

        """
        return DefaultState.NAME

    def _get_transition_handlers(self):

        """

        Returns: the state transitions

        """

        return OrderedDict([
        ])

    def get_values(self):
        return self._values

    @property
    def value1(self):
        """
        Returns: the value of PV Value1
        """
        return self._values[0]

    @value1.setter
    def value1(self, value):
        """

        :param values: set the value for a the Value1 PV
        """
        self._values[0] = value
