import openai
from google.cloud import texttospeech
from google.cloud import speech_v1p1beta1 as speech
import speech_recognition as sr
import streamlit as st
import os

# Set your OpenAI GPT-3 API key
openai.api_key = "YOUR_OPENAI_API_KEY"

# Set your Google Cloud credentials path
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "path/to/your/credentials.json"

def child_rights_chatbot(prompt):
    # Generate a response from the chatbot using OpenAI GPT-3
    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=prompt,
        temperature=0.7,
        max_tokens=150,
        n=1,
    )

    # Extract and return the generated response
    reply = response['choices'][0]['text'].strip()
    return reply

def text_to_speech(text, output_file="output.mp3"):
    # Convert text to speech using Google Cloud Text-to-Speech API
    client = texttospeech.TextToSpeechClient()
    synthesis_input = texttospeech.types.SynthesisInput(text=text)
    voice = texttospeech.types.VoiceSelectionParams(
        language_code='en-US',
        name='en-US-Wavenet-D',
        ssml_gender=texttospeech.enums.SsmlVoiceGender.NEUTRAL
    )
    audio_config = texttospeech.types.AudioConfig(
        audio_encoding=texttospeech.enums.AudioEncoding.MP3
    )

    response = client.synthesize_speech(
        input=synthesis_input, voice=voice, audio_config=audio_config
    )

    # Save the generated speech to a file
    with open(output_file, 'wb') as out:
        out.write(response.audio_content)

def speech_to_text(audio_file):
    # Convert speech to text using Google Cloud Speech-to-Text API
    client = speech.SpeechClient()
    with open(audio_file, 'rb') as audio_file:
        content = audio_file.read()

    audio = speech.RecognitionAudio(content=content)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=16000,
        language_code='en-US',
    )

    response = client.recognize(config=config, audio=audio)

    # Extract and return the transcribed text
    return response.results[0].alternatives[0].transcript

# Streamlit app
st.title("Child Rights Chatbot")

# Record user's voice input
user_voice_input_file = "user_input.wav"
recognizer = sr.Recognizer()
with sr.Microphone() as source:
    st.write("Speak something:")
    audio = recognizer.listen(source)

# Save user's voice input to a file
with open(user_voice_input_file, "wb") as f:
    f.write(audio.get_wav_data())

# Convert voice input to text
user_input_text = speech_to_text(user_voice_input_file)

# Display user's text input
st.write("You said:", user_input_text)

# Get a text-based response from the chatbot
bot_response = child_rights_chatbot(user_input_text)

# Display the bot's response
st.write("Chatbot Response:", bot_response)

# Convert the text-based response to speech
bot_voice_output_file = "bot_output.mp3"
text_to_speech(bot_response, bot_voice_output_file)

# Output the bot's speech response
st.audio(bot_voice_output_file, format="audio/mp3")
