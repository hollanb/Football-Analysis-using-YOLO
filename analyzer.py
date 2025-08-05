from utils import read_video, save_video
from trackers import Tracker
import numpy as np
import uuid
from team_assigner import TeamAssigner
from player_ball_assigner import PlayerBallAssigner
from camera_movement_estimator import CameraMovementEstimator
from view_transformer import ViewTransformer
from speed_and_distance_estimator import SpeedAndDistance_Estimator
from stats_collector import collect_interval_stats, save_stats_to_json


def process_video(video_path, features, stats_interval=30, stats_output="./output_videos/stats.json"):
    """Run analysis on the provided video.

    Parameters
    ----------
    video_path : str
        Path to the input video.
    features : tuple(bool)
        Flags for (player_detection, ball_tracking, emotion_detection,
        referee_signal, voice_whistle).
    stats_interval : int, optional
        Interval (in seconds) at which statistics are aggregated.
    stats_output : str, optional
        Where to save the statistics JSON.
    """

    player_detection, ball_tracking, emotion_detection, referee_signal, voice_whistle = features

    video_frames, fps = read_video(video_path)
    video_id = str(uuid.uuid4())
    output_path = f"/app/output_videos/{video_id}.avi"

    if not player_detection:
        save_video(video_frames, output_path, fps=fps)
        save_stats_to_json([], stats_output)
        if emotion_detection:
            print("Emotion detection not implemented yet.")
        if referee_signal:
            print("Referee signal detection not implemented yet.")
        if voice_whistle:
            print("Voice whistle analysis not implemented yet.")
        return output_path

    tracker = Tracker("./models/best.pt")

    tracks = tracker.get_object_tracks(
        video_frames, read_from_stub=True, stub_path="stubs/track_stubs.pkl"
    )
    tracker.add_position_to_tracks(tracks)

    camera_movement_estimator = CameraMovementEstimator(video_frames[0])
    camera_movement_per_frame = camera_movement_estimator.get_camera_movement(
        video_frames, read_from_stub=True, stub_path="stubs/camera_movement_stub.pkl"
    )
    camera_movement_estimator.add_adjust_positions_to_tracks(
        tracks, camera_movement_per_frame
    )

    view_transformer = ViewTransformer()
    view_transformer.add_transformed_position_to_tracks(tracks)

    tracks["ball"] = tracker.interpolate_ball_positions(tracks["ball"])

    speed_and_distance_estimator = SpeedAndDistance_Estimator(frame_rate=fps)
    speed_and_distance_estimator.add_speed_and_distance_to_tracks(tracks)

    team_assigner = TeamAssigner()
    team_assigner.assign_team_color(video_frames[0], tracks["players"][0])

    for frame_num, player_track in enumerate(tracks["players"]):
        for player_id, track in player_track.items():
            team = team_assigner.get_player_team(
                video_frames[frame_num], track["bbox"], player_id
            )
            tracks["players"][frame_num][player_id]["team"] = team
            tracks["players"][frame_num][player_id]["team_color"] = (
                team_assigner.team_colors[team]
            )

    team_ball_control = []
    if ball_tracking:
        player_assigner = PlayerBallAssigner()
        for frame_num, player_track in enumerate(tracks["players"]):
            ball_bbox = tracks["ball"][frame_num][1]["bbox"]
            assigned_player = player_assigner.assign_ball_to_player(
                player_track, ball_bbox
            )

            if assigned_player != -1:
                tracks["players"][frame_num][assigned_player]["has_ball"] = True
                team_ball_control.append(
                    tracks["players"][frame_num][assigned_player]["team"]
                )
            else:
                team_ball_control.append(
                    team_ball_control[-1] if team_ball_control else None
                )
    else:
        team_ball_control = [None] * len(video_frames)

    team_ball_control = np.array(team_ball_control)

    output_video_frames = tracker.draw_annotations(
        video_frames, tracks, team_ball_control
    )

    output_video_frames = camera_movement_estimator.draw_camera_movement(
        output_video_frames, camera_movement_per_frame
    )

    speed_and_distance_estimator.draw_speed_and_distance(
        output_video_frames, tracks
    )

    save_video(output_video_frames, output_path, fps=fps)

    stats = collect_interval_stats(tracks, team_ball_control, fps, stats_interval)
    save_stats_to_json(stats, stats_output)

    if emotion_detection:
        print("Emotion detection not implemented yet.")
    if referee_signal:
        print("Referee signal detection not implemented yet.")
    if voice_whistle:
        print("Voice whistle analysis not implemented yet.")

    return output_path

