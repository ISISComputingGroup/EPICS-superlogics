from collections import OrderedDict

from .states import DefaultState
from lewis.devices import StateMachineDevice


NUMBER_OF_INPUT_CHANNELS = 8


class SimulatedSuperlogics(StateMachineDevice):

    def _initialize_data(self):
        self.connected = True
        self.setup()

    def _get_state_handlers(self):
        return {
            'default': DefaultState(),
        }

    def _get_initial_state(self):
        return 'default'

    def _get_transition_handlers(self):
        return OrderedDict([])

    def setup(self):
        self._channels = [0.0] * NUMBER_OF_INPUT_CHANNELS

    def get_channel(self, channel):
        return self._channels[channel]

    def set_channel(self, channel, value):
        self._channels[channel] = value
