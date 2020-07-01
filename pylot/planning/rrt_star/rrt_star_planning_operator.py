"""
Author: Edward Fang
Email: edward.fang@berkeley.edu
"""
import erdos

from pylot.planning.messages import WaypointsMessage
from pylot.planning.planning_operator import PlanningOperator
from pylot.planning.rrt_star.rrt_star_planning.RRTStar.rrt_star_wrapper \
    import apply_rrt_star


class RRTStarPlanningOperator(PlanningOperator):
    """RRTStar Planning operator.

    Args:
        flags: Config flags.
        goal_location: Goal pylot.utils.Location for planner to route to.
    """
    def __init__(self,
                 pose_stream,
                 prediction_stream,
                 static_obstacles_stream,
                 lanes_stream,
                 global_trajectory_stream,
                 open_drive_stream,
                 time_to_decision_stream,
                 waypoints_stream,
                 flags,
                 goal_location=None):
        super().__init__(pose_stream, prediction_stream,
                         static_obstacles_stream, lanes_stream,
                         global_trajectory_stream, open_drive_stream,
                         time_to_decision_stream, waypoints_stream, flags,
                         goal_location)
        self._hyperparameters = {
            "step_size": flags.step_size,
            "max_iterations": flags.max_iterations,
            "end_dist_threshold": flags.end_dist_threshold,
            "obstacle_clearance": flags.obstacle_clearance_rrt,
            "lane_width": flags.lane_width,
        }

    @erdos.profile_method()
    def on_watermark(self, timestamp, waypoints_stream):
        self._logger.debug('@{}: received watermark'.format(timestamp))
        self.update_world(timestamp)
        obstacle_list = self._world.get_obstacle_list()

        if len(obstacle_list) == 0:
            # Do not use RRT* if there are no obstacles.
            # Do not use Hybrid A* if there are no obstacles.
            output_wps = self.folow_waypoints(self._flags.target_speed)
        else:
            # RRT* does not take into account the driveable region.
            # It constructs search space as a top down, minimum bounding
            # rectangle with padding in each dimension.
            self._logger.debug("@{}: Hyperparameters: {}".format(
                timestamp, self._hyperparameters))
            initial_conditions = self._compute_initial_conditions(
                obstacle_list)
            self._logger.debug("@{}: Initial conditions: {}".format(
                timestamp, initial_conditions))
            path_x, path_y, success = apply_rrt_star(initial_conditions,
                                                     self._hyperparameters)
            if success:
                self._logger.debug("@{}: RRT* succeeded".format(timestamp))
                speeds = [self._flags.target_speed] * len(path_x)
                self._logger.debug("@{}: RRT* Path X: {}".format(
                    timestamp, path_x.tolist()))
                self._logger.debug("@{}: RRT* Path Y: {}".format(
                    timestamp, path_y.tolist()))
                self._logger.debug("@{}: RRT* Speeds: {}".format(
                    timestamp, speeds))
                output_wps = self.build_output_waypoints(
                    path_x, path_y, speeds)
            else:
                self._logger.error("@{}: RRT* failed. "
                                   "Sending emergency stop.".format(timestamp))
                output_wps = self.folow_waypoints(0)

        waypoints_stream.send(WaypointsMessage(timestamp, output_wps))

    def _compute_initial_conditions(self, obstacles):
        ego_transform = self._world.ego_transform
        self._world.waypoints.remove_completed(ego_transform.location)
        end_index = min(self._flags.num_waypoints_ahead,
                        len(self._world.waypoints.waypoints) - 1)
        if end_index < 0:
            # If no more waypoints left. Then our location is our end wp.
            self._logger.debug("@{}: No more waypoints left")
            end_wp = ego_transform
        else:
            end_wp = self._world.waypoints.waypoints[end_index]
        initial_conditions = {
            "start": ego_transform.location.as_numpy_array_2D(),
            "end": end_wp.location.as_numpy_array_2D(),
            "obs": obstacles,
        }
        return initial_conditions
