"""
Author: Wonkyo Choe
Email: wonkyo.choe@virginia.edu

"""

import erdos
from erdos import Message, ReadStream, WriteStream

from pylot.abstraction.messages import HintMessage

from absl import flags

class AbstractionOperator(erdos.Operator):
    """Programming abstraction layer supporting our novel ideas.

    TBD

    Args:
        TBD


    """

    def __init__(self, 
            waypoints_stream: erdos.ReadStream,
            abstraction_stream: erdos.WriteStream,
            flags):

        waypoints_stream.add_callback(self.update_obstacles, [abstraction_stream])
        self._logger = erdos.utils.setup_logging(self.config.name,
                                                 self.config.log_file_name)
        self._flags = flags

    @staticmethod
    def connect(waypoints_stream: ReadStream):
        """Connects the operator to other streams.

        Args:

        Returns:
        """
        abstraction_stream = erdos.WriteStream()
        return [abstraction_stream]

    @erdos.profile_method()
    def update_obstacles(self, msg: Message, 
            abstraction_stream: WriteStream):
        obstacles = msg.obstacles
        abstraction_stream.send(HintMessage(msg.timestamp, obstacles))
