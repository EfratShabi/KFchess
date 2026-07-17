import os
import json


def get_frame_count(assets_path, piece_name, state):
    sprites_dir = os.path.join(assets_path, "pieces1", piece_name, "states", state, "sprites")
    return len(os.listdir(sprites_dir))


def get_frames_per_sec(assets_path, piece_name, state):
    config_path = os.path.join(assets_path, "pieces1", piece_name, "states", state, "config.json")
    with open(config_path) as f:
        config = json.load(f)
    return config["graphics"]["frames_per_sec"]


def compute_frame_index(assets_path, piece_name, state, elapsed_ms):
    fps = get_frames_per_sec(assets_path, piece_name, state)
    frame_count = get_frame_count(assets_path, piece_name, state)
    frame_idx = int(elapsed_ms / 1000 * fps)
    return (frame_idx % frame_count) + 1
