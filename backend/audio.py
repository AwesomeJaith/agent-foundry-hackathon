import asyncio
import json
import wave
import time
import numpy as np
import sounddevice as sd
from pathlib import Path
from deepgram import DeepgramClient, PrerecordedOptions, SpeakOptions
import os
from typing import Optional, Callable
import queue
import pygame

class AudioManager:
    def __init__(self, deepgram_api_key: str):
        self.deepgram = DeepgramClient(api_key=deepgram_api_key)
        self.sample_rate = 16000
        self.channels = 1
        self.silence_threshold = 0.005
        self.silence_duration = 2.0
        self.min_recording_time = 1.0
        
    def record_audio_until_silence(self, duration: int = 5) -> bytes:
        """Record audio until silence is detected or duration reached"""
        print("🎤 Listening for voice...")
        
        buffer = []
        silence_start = None
        recording_start = time.time()
        voice_detected = False
        
        with sd.InputStream(samplerate=self.sample_rate, channels=self.channels, dtype='float32') as stream:
            while True:
                data, overflowed = stream.read(1024)
                amplitude = np.abs(data).mean()
                
                buffer.append(data.copy())
                
                # Check if we've reached the maximum duration
                if time.time() - recording_start > duration:
                    break
                
                # Voice activity detection
                if amplitude > self.silence_threshold:
                    if not voice_detected:
                        voice_detected = True
                        print("🗣️ Voice detected, recording...")
                    silence_start = None  # reset silence timer
                else:
                    # Only start counting silence after voice was detected
                    if voice_detected:
                        if silence_start is None:
                            silence_start = time.time()
                        elif time.time() - silence_start > self.silence_duration:
                            # Stop recording after silence
                            if time.time() - recording_start > self.min_recording_time:
                                print("🔇 Silence detected, stopping recording...")
                                break
        
        audio = np.concatenate(buffer, axis=0)
        pcm16 = (np.clip(audio, -1, 1) * 32767).astype(np.int16)
        
        return pcm16.tobytes()
    
    def record_audio_fixed_duration(self, duration: int = 5) -> bytes:
        """Record audio for fixed duration"""
        print(f"Recording for {duration} seconds...")
        
        buffer = []
        recording_start = time.time()
        
        with sd.InputStream(samplerate=self.sample_rate, channels=self.channels, dtype='float32') as stream:
            while time.time() - recording_start < duration:
                data, overflowed = stream.read(1024)
                buffer.append(data.copy())
        
        audio = np.concatenate(buffer, axis=0)
        pcm16 = (np.clip(audio, -1, 1) * 32767).astype(np.int16)
        
        print("Recording finished!")
        return pcm16.tobytes()
    
    def save_audio(self, audio_data: bytes, filename: str):
        """Save audio data to WAV file"""
        with wave.open(filename, 'wb') as wf:
            wf.setnchannels(self.channels)
            wf.setsampwidth(2)  # 16-bit audio
            wf.setframerate(self.sample_rate)
            wf.writeframes(audio_data)
    
    async def transcribe_audio(self, filename: str) -> str:
        """Transcribe audio using DeepGram STT"""
        try:
            opts = PrerecordedOptions(
                model="nova-2",
                smart_format=True,
                punctuate=True,
                detect_language=False,
                language="en-US",
            )
            
            with open(filename, "rb") as audio_file:
                response = self.deepgram.listen.rest.v("1").transcribe_file(
                    {"buffer": audio_file, "mimetype": "audio/wav"}, 
                    opts
                )
            
            if response and response.results and response.results.channels:
                alt = response.results.channels[0].alternatives[0]
                return alt.transcript.strip() if alt.transcript else ""
            else:
                return ""
                
        except Exception as e:
            print(f"Transcription error: {e}")
            return ""
    
    async def text_to_speech(self, text: str, filename: str = "output.mp3"):
        """Convert text to speech using DeepGram TTS"""
        try:
            options = SpeakOptions(
                model="aura-2-helena-en"
            )
            
            response = self.deepgram.speak.rest.v("1").save(filename, {"text": text}, options)
            return filename
            
        except Exception as e:
            print(f"TTS error: {e}")
            return None
    
    def play_audio(self, filename: str):
        """Play audio file using pygame"""
        try:
            pygame.mixer.init()
            pygame.mixer.music.load(filename)
            pygame.mixer.music.play()
            
            # Wait for the audio to finish playing
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
                
            pygame.mixer.quit()
        except Exception as e:
            print(f"Audio playback error: {e}")
    
    def cleanup(self):
        """Clean up audio resources"""
        pygame.mixer.quit()

class AudioConversation:
    def __init__(self, deepgram_api_key: str):
        self.audio_manager = AudioManager(deepgram_api_key)
        self.conversation_history = []
        
    async def listen_and_transcribe(self, duration: int = 5, use_silence_detection: bool = True) -> str:
        """Record audio, transcribe it, and return the text"""
        print("Press Enter to start recording...")
        input()
        
        if use_silence_detection:
            audio_data = self.audio_manager.record_audio_until_silence(duration)
        else:
            audio_data = self.audio_manager.record_audio_fixed_duration(duration)
            
        self.audio_manager.save_audio(audio_data, "temp_input.wav")
        
        print("Transcribing...")
        transcription = await self.audio_manager.transcribe_audio(audio_data)
        
        if transcription:
            print(f"You said: {transcription}")
            self.conversation_history.append({"role": "user", "content": transcription})
        else:
            print("Could not transcribe audio. Please try again.")
            
        return transcription
    
    async def speak_response(self, text: str):
        """Convert text to speech and play it"""
        print(f"AI: {text}")
        self.conversation_history.append({"role": "assistant", "content": text})
        
        filename = await self.audio_manager.text_to_speech(text, "temp_output.wav")
        if filename:
            print("Playing response...")
            self.audio_manager.play_audio(filename)
            
            # Clean up temporary files
            try:
                os.remove("temp_input.wav")
                os.remove("temp_output.wav")
            except:
                pass
    
    def get_conversation_history(self) -> list:
        """Get the conversation history"""
        return self.conversation_history
    
    def cleanup(self):
        """Clean up resources"""
        self.audio_manager.cleanup()

# Global audio manager instance
_audio_manager = None

def initialize_audio(deepgram_api_key: str):
    """Initialize the global audio manager"""
    global _audio_manager
    _audio_manager = AudioManager(deepgram_api_key)

async def listen(duration: int = 5, use_silence_detection: bool = True) -> str:
    """Simple function to listen and transcribe audio"""
    if _audio_manager is None:
        raise RuntimeError("Audio not initialized. Call initialize_audio() first.")
    
    if use_silence_detection:
        audio_data = _audio_manager.record_audio_until_silence(duration)
    else:
        audio_data = _audio_manager.record_audio_fixed_duration(duration)
        
    _audio_manager.save_audio(audio_data, "temp_input.wav")
    
    print("🔄 Transcribing...")
    transcription = await _audio_manager.transcribe_audio("temp_input.wav")
    
    return transcription if transcription else ""

async def speak(text: str):
    """Simple function to convert text to speech and play it"""
    if _audio_manager is None:
        raise RuntimeError("Audio not initialized. Call initialize_audio() first.")
    
    print(f"AI: {text}")
    
    filename = await _audio_manager.text_to_speech(text, "temp_output.mp3")
    if filename:
        print("Playing response...")
        _audio_manager.play_audio(filename)
        
        # Clean up temporary files
        try:
            os.remove("temp_input.wav")
            os.remove("temp_output.mp3")
        except:
            pass

def cleanup_audio():
    """Clean up audio resources"""
    global _audio_manager
    if _audio_manager:
        _audio_manager.cleanup()
        _audio_manager = None