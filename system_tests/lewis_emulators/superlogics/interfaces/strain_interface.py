from lewis.adapters.stream import StreamInterface
from lewis.core.logging import has_log
from lewis.utils.command_builder import CmdBuilder
from lewis.utils.replies import conditional_reply


@has_log
class StrainStreamInterface(StreamInterface):
    protocol = "strain"
    in_terminator = "\r"
    out_terminator = "\r"

    def __init__(self):
        super(StrainStreamInterface, self).__init__()
        self.commands = {
            CmdBuilder(self.get_value).escape("#").arg("[0-9A-F]{2}").eos().build(),
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
    def get_value(self, _):
        return f">{self.device.get_channel(0)}"
