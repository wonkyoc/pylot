import erdos


class HintMessage(erdos.Message):
    """Message class to be used to send obstacle predictions.

    Args:
        timestamp (:py:class:`erdos.timestamp.Timestamp`): The timestamp of
            the message.
        predictions (list(:py:class:`~pylot.prediction.obstacle_prediction.ObstaclePrediction`)):  # noqa: E501
            Obstacle predictions.

    Attributes:
        predictions (list(:py:class:`~pylot.prediction.obstacle_prediction.ObstaclePrediction`)):
            Obstacle predictions.
    """
    def __init__(self, timestamp: erdos.Timestamp, obstacles):
        super(HintMessage, self).__init__(timestamp, None)
        self.obstacles = obstacles

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return 'HintMessage(timestamp: {}, obstacles: {})'.format(
            self.timestamp, self.obstacles)
