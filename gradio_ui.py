
import gradio as gr
import os
from analyzer import process_video as run_analysis
import shutil
import argparse

def analyze_video(video_path, *features):
    # Call the analysis pipeline from main.py
    try:
        
        parser = argparse.ArgumentParser()
        parser.add_argument(
            "--stats-interval",
            type=int,
            default=30,
            help="Interval in seconds at which to record statistics",
        )
        parser.add_argument(
            "--stats-output",
            default="./output_videos/stats.json",
            help="Path to the JSON file where stats will be saved",
        )
        args = parser.parse_args()
        output_path = run_analysis(video_path, features, stats_interval=args.stats_interval, stats_output=args.stats_output)
        return "Analysis Complete", output_path
    except Exception as e:
        return f"Error: {e}", None

def create_commentary(video_path):
    # Placeholder for future commentary function
    return "Commentary Created", video_path

with gr.Blocks() as interface:
    gr.Markdown("## Isaac Soccer Analyzer")
    video_input = gr.Video(label="Upload Match Video")
    features = [
        gr.Checkbox(label="Player Detection"),
        gr.Checkbox(label="Ball Tracking"),
        gr.Checkbox(label="Emotion Detection"),
        gr.Checkbox(label="Referee Signal Detection"),
        gr.Checkbox(label="Voice Whistle Analysis")
    ]
    analyze_btn = gr.Button("Analyze Video")
    analyze_output = gr.Textbox(label="Analysis Output")
    output_video = gr.Video(label="Processed Video")

    commentary_btn = gr.Button("Create Commentary")
    commentary_output = gr.Textbox(label="Commentary Output")

    analyze_btn.click(
        analyze_video,
        inputs=[video_input] + features,
        outputs=[analyze_output, output_video]
    )

    commentary_btn.click(
        create_commentary,
        inputs=[video_input],
        outputs=[commentary_output, output_video]
    )
if __name__ == "__main__":
    interface.launch(server_name="0.0.0.0", server_port=7861)
