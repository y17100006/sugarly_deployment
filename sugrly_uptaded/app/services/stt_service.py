import speech_recognition as sr
from pydub import AudioSegment
import os
import logging

def transcribe_audio(file_path: str) -> str:
    """
    Transcribes an audio file using speech_recognition library.
    Automatically converts non-WAV files to WAV using pydub.
    Returns the concatenated transcription text.
    """
    recognizer = sr.Recognizer()
    
    # Check if the file is WAV, if not, convert it
    is_wav = file_path.lower().endswith('.wav')
    temp_wav_path = None
    
    try:
        if not is_wav:
            logging.info(f"Converting {file_path} to WAV...")
            # AudioSegment.from_file handles many formats if ffmpeg is installed
            audio = AudioSegment.from_file(file_path)
            temp_wav_path = f"{file_path}_{os.getpid()}.wav"
            audio.export(temp_wav_path, format="wav")
            audio_source_path = temp_wav_path
        else:
            audio_source_path = file_path
            
        with sr.AudioFile(audio_source_path) as source:
            # Noise adjustment for files (simulated like the user's snippet)
            recognizer.adjust_for_ambient_noise(source, duration=1)
            audio_data = recognizer.record(source)
            
        try:
            # Using Google Web Speech API with Arabic (Egypt) support
            transcript = recognizer.recognize_google(audio_data, language="ar-EG")
            return transcript
        except sr.UnknownValueError:
            logging.warning("Speech Recognition could not understand audio")
            return ""
        except sr.RequestError as e:
            logging.error(f"Could not request results from Speech Recognition service; {e}")
            # Fallback or re-raise
            return ""
            
    except Exception as e:
        logging.error(f"Transcription failed: {str(e)}")
        # We return empty string or re-raise based on existing logic preference
        # Existing code raised RuntimeError for some cases and returned "" for others
        return ""
    finally:
        # Clean up temporary WAV file if created
        if temp_wav_path and os.path.exists(temp_wav_path):
            try:
                os.remove(temp_wav_path)
            except Exception as cleanup_error:
                logging.error(f"Failed to remove temporary WAV file: {cleanup_error}")
