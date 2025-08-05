import json
from collections import Counter, defaultdict


def collect_interval_stats(tracks, team_ball_control, fps, interval_seconds):
    interval_frames = int(fps * interval_seconds)
    player_tracks = tracks.get("players", [])
    num_frames = len(player_tracks)
    stats = []

    for start in range(0, num_frames, interval_frames):
        end = min(start + interval_frames, num_frames)
        interval_stat = {
            "start_time": start / fps,
            "end_time": end / fps,
            "players": [],
            "team_ball_control": {},
        }

        player_data = defaultdict(
            lambda: {
                "team": None,
                "distance": 0.0,
                "speeds": [],
                "has_ball_frames": 0,
            }
        )

        for frame_idx in range(start, end):
            for pid, pdata in player_tracks[frame_idx].items():
                entry = player_data[pid]
                if entry["team"] is None:
                    entry["team"] = pdata.get("team")
                if "distance" in pdata:
                    entry["distance"] = pdata["distance"]
                if "speed" in pdata:
                    entry["speeds"].append(pdata["speed"])
                if pdata.get("has_ball"):
                    entry["has_ball_frames"] += 1

        for pid, pdata in player_data.items():
            avg_speed = (
                sum(pdata["speeds"]) / len(pdata["speeds"])
                if pdata["speeds"]
                else None
            )
            team_value = pdata["team"]
            if team_value is not None:
                try:
                    team_value = int(team_value)
                except Exception:
                    pass
            interval_stat["players"].append(
                {
                    "id": int(pid),
                    "team": team_value,
                    "distance": float(pdata["distance"]),
                    "avg_speed": float(avg_speed) if avg_speed is not None else None,
                    "ball_possession_time": pdata["has_ball_frames"] / fps,
                }
            )

        counter = Counter(team_ball_control[start:end])
        interval_stat["team_ball_control"] = {
            str(team): frames / fps for team, frames in counter.items()
        }

        stats.append(interval_stat)

    return stats


def save_stats_to_json(stats, output_path):
    with open(output_path, "w") as f:
        json.dump(stats, f, indent=2)

