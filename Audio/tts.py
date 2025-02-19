import azure.cognitiveservices.speech as speechsdk
from decouple import config
import os
import re

# Load API Key and region from environment variables
API_Key = config("AZURE_TTS_KEY")
region = "westus"

# Initialize Azure Speech SDK with timestamps enabled
speech_config = speechsdk.SpeechConfig(subscription=API_Key, region=region)
speech_config.request_word_level_timestamps()

def generate_ssml(text, voice="en-US-JennyNeural", rate="1.0", pitch="default", volume="default"):
    """Generate SSML dynamically based on user settings."""
    return f"""
    <speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="en-US">
        <voice name="{voice}">
            <prosody rate="{rate}" pitch="{pitch}" volume="{volume}">
                {text}
            </prosody>
        </voice>
    </speak>
    """

def generate_tts(text, output_file="output.wav", voice="en-US-JennyNeural", rate="1.0", pitch="default", volume="default"):
    """Synthesize speech with word-level timestamps and save to file."""
    
    # Generate SSML
    ssml = generate_ssml(text, voice=voice, rate=rate, pitch=pitch, volume=volume)

    # Configure audio output
    audio_config = speechsdk.audio.AudioConfig(filename=output_file)
    speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)

    timestamps = []

    def on_word_boundary(evt):
        start_time_sec = evt.audio_offset / 10_000_000  # Convert to seconds
        # evt.text is the "word" (or punctuation). We store (word, start_time_sec)
        timestamps.append((evt.text, start_time_sec))
        print(f"🕒 {start_time_sec:.2f}s - {evt.text}")

    # Attach event handler for word boundary timestamps
    speech_synthesizer.synthesis_word_boundary.connect(on_word_boundary)

    # Synthesize speech
    result = speech_synthesizer.speak_ssml_async(ssml).get()

    if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        print(f"✅ Speech synthesis completed successfully! Audio saved to {output_file}")
    else:
        print(f"❌ Speech synthesis failed. Reason: {result.reason}")
        if result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = result.cancellation_details
            print(f"CancellationReason: {cancellation_details.reason}")
            if cancellation_details.reason == speechsdk.CancellationReason.Error:
                print(f"ErrorDetails: {cancellation_details.error_details}")

    # ================================
    # 1) MERGE PUNCTUATION WITH PREVIOUS WORD
    # ================================
    processed = []
    punctuation_pattern = re.compile(r'^[^\w\d]+$')  # e.g., matches ",", "!", "?", "." (non-alphanumeric)
    
    for i, (token, start_sec) in enumerate(timestamps):
        token = token.strip()
        if i > 0 and punctuation_pattern.match(token):
            # This token is just punctuation, so merge it with the previous word
            prev_word, prev_start = processed[-1]
            processed[-1] = (prev_word + token, prev_start)
        else:
            # Normal word, add as is
            processed.append((token, start_sec))
    
    # ================================
    # 2) GENERATE PER-WORD SUBTITLES USING NEXT WORD'S START AS END TIME
    # ================================
    subtitles_file = output_file.replace(".mp3", ".srt").replace(".wav", ".srt")
    with open(subtitles_file, "w", encoding="utf-8") as f:
        for idx in range(len(processed)):
            word, start_time = processed[idx]
            # Look ahead to find the end time
            if idx < len(processed) - 1:
                # End time is the start of the next word
                end_time = processed[idx+1][1]
            else:
                # For the last token, just add e.g. 0.5s of buffer
                # Or measure final audio length, if you prefer
                end_time = start_time + 0.50

            # Convert float times into SRT HH:MM:SS,mmm
            start_h = int(start_time // 3600)
            start_m = int((start_time % 3600) // 60)
            start_s = int(start_time % 60)
            start_ms = int((start_time - int(start_time)) * 1000)

            end_h = int(end_time // 3600)
            end_m = int((end_time % 3600) // 60)
            end_s = int(end_time % 60)
            end_ms = int((end_time - int(end_time)) * 1000)

            start_str = f"{start_h:02}:{start_m:02}:{start_s:02},{start_ms:03}"
            end_str   = f"{end_h:02}:{end_m:02}:{end_s:02},{end_ms:03}"

            f.write(f"{idx+1}\n")
            f.write(f"{start_str} --> {end_str}\n")
            f.write(f"{word}\n\n")

    print(f"✅ Subtitles saved to {subtitles_file}")
    
    return processed  # Return the processed (word, timestamp) list


# Example usage
if __name__ == "__main__":
    text_to_speak = """hello my name is jiho!"""
    generate_tts(
        text=text_to_speak,
        output_file="example.wav",
        voice="en-US-AndrewNeural",
        rate="1.0",
        pitch="default",
        volume="default"
    )
