import streamlit as st
import openai
from google.cloud import speech, texttospeech
import moviepy.editor as mp
import os
import requests

# Set OpenAI API Key
openai.api_key = "22ec84421ec24230a3638d1b7dc"
openai_api_endpoint = "https://internshala.openai.azure.com/openai/deployments/gpt-4o/chat/completions?api-version=2024-08-01-preview"

# Google Cloud Credentials setup
speech_client = speech.SpeechClient()
tts_client = texttospeech.TextToSpeechClient()

def extract_audio(video_file):
    """Extract audio from the uploaded video."""
    clip = mp.VideoFileClip(video_file)
    audio_file = "extracted_audio.wav"
    clip.audio.write_audiofile(audio_file)
    return audio_file

def transcribe_audio(audio_file):
    """Transcribe audio using Google Speech-to-Text."""
    with open(audio_file, "rb") as audio_file_content:
        audio = speech.RecognitionAudio(content=audio_file_content.read())
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            language_code="en-US"
        )
        response = speech_client.recognize(config=config, audio=audio)
        transcript = " ".join([result.alternatives[0].transcript for result in response.results])
        return transcript

def correct_transcription(transcript):
    """Use GPT-4o to correct transcription."""
    headers = {
        "Content-Type": "application/json",
        "api-key": openai.api_key
    }
    data = {
        "messages": [{"role": "user", "content": f"Correct this transcription: {transcript}"}],
        "max_tokens": 500
    }

    response = requests.post(openai_api_endpoint, headers=headers, json=data)
    if response.status_code == 200:
        corrected_text = response.json()["choices"][0]["message"]["content"]
        return corrected_text
    else:
        raise Exception(f"Failed to correct transcription: {response.status_code} - {response.text}")

def text_to_speech(corrected_text):
    """Convert corrected text to speech using Google Text-to-Speech."""
    input_text = texttospeech.SynthesisInput(text=corrected_text)
    voice = texttospeech.VoiceSelectionParams(
        language_code="en-US",
        name="en-US-Wavenet-J"
    )
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3
    )
    response = tts_client.synthesize_speech(input=input_text, voice=voice, audio_config=audio_config)
    audio_output = "corrected_audio.mp3"
    with open(audio_output, "wb") as out:
        out.write(response.audio_content)
    return audio_output

def replace_audio_in_video(video_file, audio_file):
    """Replace the original audio in the video with the corrected one."""
    video_clip = mp.VideoFileClip(video_file)
    audio_clip = mp.AudioFileClip(audio_file)
    new_video = video_clip.set_audio(audio_clip)
    output_file = "final_video.mp4"
    new_video.write_videofile(output_file, codec="libx264", audio_codec="aac")
    return output_file

# Streamlit UI
st.title("AI-Powered Video Audio Replacement")

# Video File Upload
video_file = st.file_uploader("Upload a Video File", type=["mp4", "mov", "avi"])

if video_file:
    st.write("Processing the video...")
    
    # Extract audio from video
    audio_file = extract_audio(video_file)
    st.write("Audio extracted.")
    
    # Transcribe audio
    transcript = transcribe_audio(audio_file)
    st.write("Transcription: ", transcript)
    
    # Correct transcription using GPT-4o
    corrected_transcript = correct_transcription(transcript)
    st.write("Corrected Transcript: ", corrected_transcript)
    
    # Convert corrected text to speech
    corrected_audio_file = text_to_speech(corrected_transcript)
    st.write("Generated Corrected Audio.")
    
    # Replace audio in the original video
    final_video_file = replace_audio_in_video(video_file, corrected_audio_file)
    st.write("Final video generated.")

    # Display the final video
    st.video(final_video_file)
