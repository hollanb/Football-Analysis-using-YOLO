
import gradio as gr
from analyzer import process_video as run_analysis

def analyze_video(video_path, stats_interval, *features):
    # Call the analysis pipeline from main.py
    try:
        output_path = run_analysis(
            video_path,
            features,
            stats_interval=int(stats_interval),
            stats_output="./output_videos/stats.json",
        )
        return "Analysis Complete", output_path
    except Exception as e:
        return f"Error: {e}", None

def create_commentary(video_path):
    # Placeholder for future commentary function
    return "Commentary Created", video_path

with gr.Blocks() as interface:
    gr.Markdown("## Isaac Soccer Analyzer")
    video_input = gr.Video(label="Upload Match Video")
    stats_interval = gr.Number(value=30, label="Stats Interval (sec)")
    features = [
        gr.Checkbox(label="Player Detection"),
        gr.Checkbox(label="Ball Tracking"),
        gr.Checkbox(label="Emotion Detection"),
        gr.Checkbox(label="Referee Signal Detection"),
        gr.Checkbox(label="Voice Whistle Analysis"),
    ]
    analyze_btn = gr.Button("Analyze Video")
    analyze_output = gr.Textbox(label="Analysis Output")
    output_video = gr.Video(label="Processed Video")

    commentary_btn = gr.Button("Create Commentary")
    commentary_output = gr.Textbox(label="Commentary Output")

    analyze_btn.click(
        analyze_video,
        inputs=[video_input, stats_interval] + features,
        outputs=[analyze_output, output_video],
    )

    commentary_btn.click(
        create_commentary,
        inputs=[video_input],
        outputs=[commentary_output, output_video]
    )
if __name__ == "__main__":
    interface.launch(server_name="0.0.0.0", server_port=7861)
