---
title: Stream Chat TTS
subtitle: Twitch Chat-to-Voice System
status: Active
image: /img/chat-tts/tkinter-view.png
image_alt: Animated speaker character — the chat TTS overlay visualiser
tags: [Python, TwitchIO, Google TTS, ElevenLabs, SAM, asyncio]
---

## What is it?

Affectionately named Jerry, they are a Twitch chat reader that gives every viewer their own voice. Instead of a single robotic voice reading everything, each chatter can be assigned a distinct TTS engine and voice profile. The result on stream is a recognisable cast of voices rather than a wall of identical text. Jerry handles the complexity of managing multiple TTS engines and routing messages appropriately.

This was built as a standalone tool that runs alongside OBS — it reads chat via the Twitch IRC API and pipes audio directly to a VLC instance.

Its entire purpose was to vocalize every message as I stated out streaming, this is because I was terrible at reading messages and keeping up with chat in real-time. Jerry was built as a crutch to help me manage the flow of chat without missing important interactions. Instead people now just use it to bully me on stream.

## The Four Engines

The main base of jerry are these four TTS engines:

### 1. Google Cloud TTS
The default for most viewers. High quality, low latency, and a large enough voice catalogue that it's easy to give different viewers noticeably different voices. The API call is wrapped in a cache layer so repeated phrases (greetings, common phrases like "PogChamp") don't cost an API call.

This is the cheapest option for generating voices, as it uses Google's infrastructure and benefits from the caching layer to minimize API calls.

### 2. ElevenLabs
Reserved for regular viewers or subscribers who want a higher-quality AI voice. ElevenLabs voices have far more natural prosody than Google Cloud but cost more per character. The per-viewer voice config stores the ElevenLabs `voice_id` so each user gets a consistent voice across sessions.

AS I worked more with tools like Sharon and the eleven labs API I realized the potential for creating highly personalized and expressive voices for regular viewers. This allows for some viewer customization but its not something I could do for every viewer due to token costs and lack of reusability of audio files.

### 3. SAM (Software Automatic Mouth)
The retro option. SAM is a port of the 1982 Commodore 64 speech synthesiser — it sounds like a robot from a sci-fi B-movie. Some viewers specifically request it. It runs entirely locally with no API calls.

only one person ever asked for this, no one currently uses it but its there.

### 4. Animalese
This bloody THING. This was one of the single most infuriating things to try and get to work and it still did not work in the slightest. This single feature request lead me down a multi week rabbit hole of learning. Do you know how hard it is to get an animal crossing like voice synthesized? BECAUSE I DO!!!!

I have been deep in the bowels of 2000's dated forums learning the mathematics behind the synthesis of Animalese audio, trying to understand how to manipulate pitch, timing, and concatenation to achieve the desired effect. Only to discover that the base is from the japanese alphabet and part of the reason why my attempts always sounded wrong

It's on the back burner to fix at a later date but for now, it alludes me.

Implementation: the `_projects/chat-tts/animalese_letters/` directory contains individual `.mp3` samples for every letter of the alphabet. For each incoming message, the text is iterated character by character, the corresponding sample is loaded, pitch-shifted slightly, and the samples are concatenated into a playable audio buffer.

```python
def create_animalese_audio(text: str) -> bytes:
    audio_segments = []
    for char in text.lower():
        if char.isalpha() and char in letter_samples:
            segment = letter_samples[char]
            # slight pitch randomisation for natural feel
            pitch = random.uniform(0.9, 1.1)
            audio_segments.append(segment._spawn(
                segment.raw_data,
                overrides={"frame_rate": int(segment.frame_rate * pitch)}
            ))
    return AudioSegment.silent(50).join(audio_segments)
```

## Voice Assignment

Viewer-to-voice mappings are stored in a JSON config. The structure allows per-viewer overrides for engine type, voice ID, and speaking rate:

```json
{
  "viewer_name": {
    "type": "elevenlabs",
    "voice": { "voice_id": "abc123" },
    "ai_voice": true
  },
  "another_viewer": {
    "type": "animalese"
  }
}
```

The `voice_selector` module loads this at startup and routes each incoming message to the correct engine at call time.

## Async Architecture

Chat reading and audio playback run on separate async queues so a slow TTS API call doesn't cause a backlog that stalls incoming messages. The `janus.Queue` bridge allows the async Twitch IRC listener to hand messages to the synchronous TTS functions without blocking either side.

The keyboard controller subscribes to its own queue — a hotkey can skip the current TTS playback and clear the pending queue, useful during high-traffic stream moments.

## Caching

A SHA-256 hash of each `(text, voice_config)` pair is computed before synthesis. If the hash exists in the audio cache, the cached `.mp3` is played directly. This is especially useful for common phrases and the streamer's own name being read back.
