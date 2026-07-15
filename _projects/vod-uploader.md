---
title: VOD YouTube Uploader
subtitle: Batch Upload Tool for Streamers
status: Active
image: /img/vod-uploader/upload-tab.png
image_alt: YouTube VOD Uploader GUI showing single file and mass folder upload modes
tags: [Python, tkinter, YouTube Data API, ffmpeg, PyInstaller]
gallery:
  - src: /img/vod-uploader/normalizer-tab.png
    alt: Audio normaliser tab with ffmpeg loudnorm settings
  - src: /img/vod-uploader/config-tab.png
    alt: Configuration tab for OAuth credentials
---

## The Problem

YouTube's web uploader is unreliable for large files. Stream recordings — especially long ones at high bitrate — regularly exceed 4–8 GB. At that size, the browser uploader frequently stalls, loses progress, or silently fails partway through. Re-uploading a 6 GB file from scratch every time the browser tab refreshes is not a workflow.

The YouTube Data API v3 supports **resumable uploads**: the upload is chunked, each chunk is acknowledged, and a failed upload can be resumed from the last successful chunk rather than starting over. The web UI doesn't expose this properly. The API does.

## The Tool

A desktop GUI application (tkinter) that wraps the YouTube Data API with a focus on reliability and usability for non-technical streamers. The primary users aren't developers — they're streamers who want to upload last night's VOD without fighting with a browser.

Key decisions made with that user in mind:

**OAuth sign-in instead of API key management.** The app guides the user through a one-time Google sign-in flow and caches the refresh token. No copying of client secrets or managing JSON files manually after the first setup.

**Progress is persisted.** A local JSON log tracks which files have been uploaded successfully. Restarting the app after a failure skips already-completed files and resumes interrupted ones. Uploading a folder of 10 VODs and having the computer restart halfway through doesn't mean starting over.

**Single file and mass folder modes.** The upload tab (shown above) handles both. Mass folder mode processes every video file in a directory in sequence.

## Audio Normalisation

Twitch VODs have inconsistent audio levels. The microphone, game audio, and alert sounds are mixed live — and the mix varies session to session. Uploading a VOD playlist where volume jumps between episodes is a bad viewer experience.

The normaliser tab runs an **ffmpeg loudnorm** two-pass filter on each file before upload:

1. **Analysis pass** — ffmpeg measures the integrated loudness, true peak, and loudness range of the file
2. **Normalisation pass** — ffmpeg re-encodes the audio track to the target loudness level (default: -16 LUFS, matching YouTube's normalisation target)

The video stream is copied without re-encoding (fast), only the audio is processed. The output files are stored in a configurable output directory, leaving originals untouched.

```
Input VOD  ──► [ffmpeg loudnorm analysis]
                         │
                         ▼
               target_i = -16 LUFS
               target_tp = -1.5 dBFS
                         │
                         ▼
           [ffmpeg re-encode audio only]
                         │
                         ▼
           Normalised output file ──► YouTube upload queue
```

## Distribution

The app ships as a single `.exe` built with PyInstaller. The build script bundles the ffmpeg binary alongside the Python application so users don't need to install anything separately. A `User_Guide.md` walks through the one-time Google Cloud project setup needed to generate OAuth credentials.
