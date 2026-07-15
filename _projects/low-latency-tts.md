---
title: Low-Latency TTS
subtitle: Realtime Audio Pipeline
status: Active
image: /img/tts/low-latency-tts-system.png
image_alt: Low-Latency TTS configuration UI showing provider settings
tags: [Python, Google TTS, ElevenLabs, Azure Speech, Whisper, PyInstaller]
gallery:
  - src: /img/tts/tts-latency-log.png
    alt: Per-utterance latency log showing synth, queue, and total times
  - src: /img/tts/tts-system-log.png
    alt: System log showing the full pipeline in operation
---

## What is it?

A real-time text-to-speech pipeline where the input is speech (via OpenAI Whisper) and the output is synthesised audio through one of three cloud TTS providers. The use case is live voice processing — say something, hear it played back in a different voice within a second.

The "low-latency" part is the actual engineering challenge. Cloud TTS APIs have non-trivial round-trip times. The goal was to minimise the gap between speech input completing and audio output starting.

## The Pipeline

```
Microphone input
     │
     ▼
OpenAI Whisper (STT)      ~0.3–0.8s recognition
     │
     ▼
Provider selection
     │
     ├──► Google Cloud TTS  ┐
     ├──► ElevenLabs        ├──► ~0.4–0.7s synthesis
     └──► Azure Cognitive   ┘
               │
               ▼
         Audio queue
               │
               ▼
          VLC playback
```

The key design decision: STT and TTS run in separate async tasks. While one utterance is being synthesised, the next can be transcribed. This is what the latency log shows — the synthesis time (~0.69s) and queue wait time overlap with the previous utterance's playback, so the *perceived* gap is much shorter than the raw numbers suggest.

## Measured Latency

From the latency log (captured during a real session):

| Utterance | Synth time | Queue wait | Total |
|-----------|-----------|------------|-------|
| 1 | 1.34s | 0.00s | 4.58s |
| 2 | 0.69s | 0.22s | 4.15s |
| 3 | 0.69s | 0.31s | 4.22s |

The first utterance is slower (cold start, no cached connection). Subsequent utterances settle around **0.69s synthesis** with the total time (including recognition and playback startup) around **4.2s**. For a real-time voice pipeline running on consumer hardware over a standard internet connection, that's acceptable.

## Provider Comparison

All three providers were benchmarked during development:

**Google Cloud TTS** — Fastest synthesis, most consistent latency. The voice quality is good but noticeably synthetic at slower speaking rates. Best for high-throughput usage where cost matters.

**ElevenLabs** — Best voice quality by a significant margin. The natural prosody makes synthesised speech sound almost indistinguishable from a real voice in normal listening conditions. Higher latency and cost.

**Azure Cognitive Services** — Middle ground. Solid latency, good quality, and the Neural voices are noticeably better than Google's standard voices. Good option if you're already in the Azure ecosystem.

## Distribution

The tool ships as a PyInstaller `.exe` so it can be used on machines without a Python environment. The build script bundles all dependencies including the ffmpeg binary. The config UI (shown above) lets users enter their API keys and select providers without editing any files.
