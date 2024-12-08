import vosk
import pyaudio
import json
from gtts import gTTS
from gemini import GeminiAI
import io
import pygame
import signal
import sys
from datetime import datetime
import random
import re

model_name = "gemini-pro"
your_ai = GeminiAI(model_name=model_name)


# Global variable to control the main loop
running = True

def signal_handler(sig, frame):
    """Handle Ctrl+C to gracefully exit the program"""
    global running
    print("\nCtrl+C detected. Stopping the program...")
    running = False
    sys.exit(0)

# Register the signal handler for Ctrl+C
signal.signal(signal.SIGINT, signal_handler)

def log_interaction(input_text, output_text):
    """Log the interaction to logs.txt"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open('logs.txt', 'a', encoding='utf-8') as log_file:
        log_file.write(f"---\nTimestamp: {timestamp}\n")
        log_file.write(f"Input: {input_text}\n")
        log_file.write(f"Output: {output_text}\n")

def record_voice():
    model_path = "vosk-model-small-en-us-0.15"
    model = vosk.Model(model_path)
    rec = vosk.KaldiRecognizer(model, 16000)
    # Open the microphone stream
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16,
                    channels=1,
                    rate=16000,
                    input=True,
                    frames_per_buffer=8192)
    print("\033[42m                              SPEAK NOW                              \033[0m")
    print("Listening for speech.")
    recognized_text = ""
    while recognized_text == "":
        data = stream.read(4096)
        if rec.AcceptWaveform(data):
            result = json.loads(rec.Result())
            recognized_text = result['text'].strip()
            print(f"[What You Said]: {recognized_text}")

    stream.stop_stream()
    stream.close()
    p.terminate()
    
    return recognized_text


def speak(text):
    language = 'en'

    # Create the audio in memory
    tts = gTTS(text=text, lang=language, slow=False)
    audio_fp = io.BytesIO()
    tts.write_to_fp(audio_fp)
    audio_fp.seek(0)

    # Initialize pygame mixer and play the audio
    pygame.mixer.init()
    pygame.mixer.music.load(audio_fp, 'mp3')
    pygame.mixer.music.play()

    # Wait for the audio to finish playing
    while pygame.mixer.music.get_busy():
        pass

def test_user():
    phrases_completed = 0
    ask_user = ["the quick brown fox jumps over the lazy dog",
                "she sells seashells by the seashore",
                "one two three four five six seven eight nine ten",]
    speak("To check your microphone integrity, Please Repeat After Me")
    while phrases_completed < len(ask_user):
        speak(f'Test Number {phrases_completed+1}: {ask_user[phrases_completed]}')
        input_text = record_voice()
        if input_text == ask_user[phrases_completed].lower():
            phrases_completed += 1
            speak("I heard That Correctly! Lets Move On")
        else:
            speak("I Did Not Hear That, Please Repeat The Phrase")
    if phrases_completed == len(ask_user):
        return True
    return False

def generate_ai_response(input_text):
    # Generate the response
    aires = your_ai.generate_response(input_text=input_text)
    
    # Extract the text value
    try:
        # Option 1: If it's a response object with a .text attribute
        return aires.text
    except AttributeError:
        try:
            # Option 2: If it's a dictionary-like object
            return aires['text']
        except (TypeError, KeyError):
            try:
                # Option 3: If it's a list or has a candidates method
                return aires.result.candidates[0].content.parts[0].text
            except Exception as e:
                # If all else fails, return the raw response
                print(f"Error extracting text: {e}")
                return str(aires)

def clean_job_description(job_description):
    """
    Cleans a job description by removing unnecessary symbols, buzzwords, and fluff, 
    and returns a simplified, AI-readable version of the text.
    """
    if not job_description:  # Handle empty or None descriptions
        return "No description available."
    
    # Remove unnecessary symbols and escape sequences
    job_description = re.sub(r"\\[a-zA-Z]", "", job_description)  # Remove escaped characters
    job_description = re.sub(r"[^\S\r\n]+", " ", job_description)  # Remove excessive spaces
    job_description = re.sub(r"[\*\-]{2,}", "", job_description)  # Remove repeated symbols like "**" or "--"
    job_description = re.sub(r"\n{2,}", "\n", job_description)  # Replace multiple newlines with a single newline
    
    # Remove generic buzzwords/phrases
    buzzwords = [
        # General fluff
        "team player", "passionate", "innovative", "cutting-edge", "fast-paced environment",
        "self-starter", "proactive", "results-driven", "go-getter", "empowered", "dynamic environment",
        "work hard, play hard", "dedicated", "highly motivated", "world-class", "forward-thinking",
        
        # Overused job terms
        "strong communication skills", "problem-solving skills", "attention to detail", 
        "strong work ethic", "ability to multitask", "works well under pressure", 
        "good interpersonal skills", "proven track record", 
        
        # Diversity/inclusion boilerplate (if redundant)
        "equal opportunity employer", "diverse workforce", "inclusive environment", 
        "discrimination-free workplace",
        
        # Benefits-related buzzwords
        "competitive salary", "comprehensive benefits", "attractive compensation package", 
        "exciting career development opportunities", "paid time off", "rewarding experience",
        
        # Other buzzwords
        "join our team", "we are seeking", "opportunity to grow", "best-in-class", 
        "make a difference", "leading company in the industry", "pursue your passion",
        "work-life balance", "collaborative environment", "be part of something great"
    ]
    
    # Remove all buzzwords from text
    for word in buzzwords:
        job_description = job_description.replace(word, "")
    
    # Retain key sections: Responsibilities, Qualifications, etc.
    relevant_sections = ["Responsibilities", "Qualifications", "Job", "Requirements", "Benefits"]
    cleaned_description = []
    for line in job_description.splitlines():
        if any(section in line for section in relevant_sections) or line.strip():
            cleaned_description.append(line.strip())
    
    # Join cleaned lines
    return "\n".join(cleaned_description).strip()

        

def main():

    global running
    running = True
    increment = 0
    
    while running:
        try:
            speak("Welcome To Inquire!")
            mic_test = test_user()
            if mic_test:
                speak("You're Mic Sounds Good!, Lets Begin the Video Test")
        
        except Exception as e:
            print(f"An error occurred: {e}")
            continue


if __name__ == "__main__":
    main()