import os
import subprocess
from moviepy.editor import VideoFileClip, AudioFileClip

class VideoProcessor:
    def __init__(self, video_id, fps=21.5, sr=22050, prefix="playing_bongo"):
        self.video_id = video_id
        self.fps = fps
        self.sr = sr
        self.prefix = prefix
        self.input_video_path = f"./{video_id}.mp4"
        self.processed_video_dir = f"./processed_data/{prefix}/video_10s_{fps}fps"
        self.processed_audio_dir = f"./processed_data/{prefix}/audio_10s_{sr}hz"
        self.feature_dir = f"./features/{prefix}"
        self.progress_status = "not_started"

    def preprocess(self):
        # Create necessary directories
        os.makedirs(self.processed_video_dir, exist_ok=True)
        os.makedirs(self.processed_audio_dir, exist_ok=True)
        os.makedirs(self.feature_dir, exist_ok=True)

        # Load and trim the video
        clip = VideoFileClip(self.input_video_path)
        trimmed_clip = clip.subclip(0, min(10, clip.duration))

        # Save processed video and audio
        output_video_path = os.path.join(self.processed_video_dir, f'{self.video_id}.mp4')
        output_audio_path = os.path.join(self.processed_audio_dir, f'{self.video_id}.wav')
        trimmed_clip.write_videofile(output_video_path, fps=self.fps, codec="libx264", audio_codec="aac")
        trimmed_clip.audio.write_audiofile(output_audio_path, fps=self.sr)

    def run_subprocess(self, command):
        """ Run a subprocess and return True if successful, False otherwise. """
        try:
            result = subprocess.run(command, capture_output=True, text=True, check=True)
            print(result.stdout)  # Optionally print the output for logging
            return True
        except subprocess.CalledProcessError as e:
            print(f"Error in subprocess: {e.stderr}")
            return False

    def extract_features(self):
        self.progress_status = "extracting_features"

        # Example feature extraction steps using external scripts
        if not self.run_subprocess(["python", "./api/extract_rgb_flow.py", "-i", self.processed_video_dir, "-o", os.path.join(self.feature_dir, f"OF_10s_{self.fps}fps")]):
            self.progress_status = "error"
            return

        if not self.run_subprocess(["python", "./api/extract_mel_spectrogram.py", "-i", self.processed_audio_dir, "-o", os.path.join(self.feature_dir, f"melspec_10s_{self.sr}hz")]):
            self.progress_status = "error"
            return

        if not self.run_subprocess(["CUDA_VISIBLE_DEVICES=0", "python", "./api/extract_feature.py", "-f", self.video_id, "-m", "RGB", "-i", os.path.join(self.feature_dir, f"OF_10s_{self.fps}fps"), "-o", os.path.join(self.feature_dir, f"feature_rgb_bninception_dim1024_{self.fps}fps")]):
            self.progress_status = "error"
            return

        if not self.run_subprocess(["CUDA_VISIBLE_DEVICES=0", "python", "./api/extract_feature.py", "-f", self.video_id, "-m", "Flow", "-i", os.path.join(self.feature_dir, f"OF_10s_{self.fps}fps"), "-o", os.path.join(self.feature_dir, f"feature_flow_bninception_dim1024_{self.fps}fps")]):
            self.progress_status = "error"
            return

    def make_prediction(self):
        self.progress_status = "preprocessing"
        self.preprocess()
        self.progress_status = "feature extracting"
        self.extract_features()
        self.progress_status = "inferencing"

        os.system(f"CUDA_VISIBLE_DEVICES=0 python ./api/test.py --test_name {self.video_id}")

        # Load the video clip
        video_clip = VideoFileClip(os.path.join(self.processed_video_dir, f'{self.video_id}.mp4'))

        # Load the audio clip
        audio_clip = AudioFileClip(os.path.join('./results', f'{self.video_id}.wav'))

        # Set the audio of the video clip to your audio clip
        video_clip = video_clip.set_audio(audio_clip)

        # Write the result to a new file
        video_clip.write_videofile(os.path.join('./results/', f'{self.video_id}.mp4'), codec='libx264', audio_codec='aac')
        
        self.progress_status = "completed"

    def get_status(self):
        return self.progress_status
