import os
import torch
import librosa
from moviepy.editor import VideoFileClip
from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor, AutoModelForCausalLM, AutoTokenizer

# Step 1: Extract Audio from Video using moviepy
def extract_audio(video_path, audio_path):
    video = VideoFileClip(video_path)
    video.audio.write_audiofile(audio_path)

# Prompt the user to input the file path to the video
video_path = input("Please enter the file path to the video: ")
audio_path = "output_audio.wav"

# Check if the video file exists
if not os.path.exists(video_path):
    print(f"Error: The file at {video_path} does not exist.")
    exit(1)

# Extract audio from video
extract_audio(video_path, audio_path)

# Step 2: Convert Audio to Text using Wav2Vec2

# Load pre-trained model and processor
model_name = "facebook/wav2vec2-large-960h"
processor = Wav2Vec2Processor.from_pretrained(model_name)
model = Wav2Vec2ForCTC.from_pretrained(model_name)

# Load and preprocess the audio file
speech, sampling_rate = librosa.load(audio_path, sr=16000)

# Tokenize the input
inputs = processor(speech, sampling_rate=sampling_rate, return_tensors="pt", padding=True)

# Perform speech recognition
with torch.no_grad():
    logits = model(inputs.input_values).logits

# Decode the predicted tokens
predicted_ids = torch.argmax(logits, dim=-1)
transcription = processor.batch_decode(predicted_ids)[0]  # Output: Transcription

print("Transcription:", transcription)

'''# Step 3: Process the Text with Mistral AI's Language Model (Optional)

# Load pre-trained language model and tokenizer
model_name = "bigscience/bloom-7b1"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)

# Tokenize the transcription
inputs = tokenizer(transcription, return_tensors="pt")  # Input: Transcription

# Generate text
outputs = model.generate(inputs.input_ids, max_length=50, num_return_sequences=1)

# Decode the generated text
generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)  # Output: Generated Text

print("Generated Text:", generated_text)
'''