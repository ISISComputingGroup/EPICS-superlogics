from functools import partial

from lewis.adapters.stream import StreamInterface
from lewis.utils.command_builder import CmdBuilder
from lewis.core.logging import has_log
from lewis.utils.replies import conditional_reply

@has_log
class ThermoStreamInterface(StreamInterface):

    protocol = "thermo"
    in_terminator = "\r"
    out_terminator = "\r"

    def __init__(self):
        super(ThermoStreamInterface, self).__init__()
        self.commands = {
            CmdBuilder(self.get_channel).escape("#").arg("[0-9A-F]{2}").arg("[0-7]{1}", argument_mapping=partial(int)).eos().build(),
        }

    def handle_error(self, request, error):
        """
        If command is not recognised print and error

        Args:
            request: requested string
            error: problem

        """
        self.log.error("An error occurred at request " + repr(request) + ": " + repr(error))

    @conditional_reply("connected")
    def get_channel(self, _, channel):
        return f">{self.device.get_channel(channel)}"
