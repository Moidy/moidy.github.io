---
title: Twitter Tools
subtitle: Cross-Platform Posting & Analytics
status: Maintained
image: /img/twitter-tools/views-vs-time-posted.png
image_alt: Scatter chart of tweet views vs time of day, showing a strong peak at 21:00 UTC
tags: [Python, Twitter API, Bluesky, OpenAI, Pandas, Matplotlib]
gallery:
  - src: /img/twitter-tools/views-vs-reposts.png
    alt: Views vs reposts — proportional and unsurprising
  - src: /img/twitter-tools/views-likes-over-time.png
    alt: Views vs likes over time
  - src: /img/twitter-tools/views-vs-date.png
    alt: Views by date
---

## What is it?

Two things bundled together: a cross-platform posting tool that publishes content simultaneously to Twitter/X and Bluesky, and a data analysis layer that processes engagement metrics to find patterns worth acting on.

The posting side is straightforward OAuth-authenticated API calls. The interesting part was the analytics.

## The Data Findings

The analysis was built to answer a simple question: *does any observable variable predict tweet performance?*

Three variables were tested against view counts across a corpus of tweets:

### Date Posted — Not Interesting

Plotting views against calendar date shows one significant outlier (a tweet that happened to go semi-viral) and a flat distribution otherwise. Date alone predicts nothing useful — the distribution is effectively noise with one spike.

### Reposts and Likes — Obvious

Views, reposts, and likes scale together. More-viewed tweets get more reposts and likes. This is exactly what you'd expect and confirms the data pipeline is working, but adds no actionable signal.

### **Time of Posting — Actually Interesting**

This is the chart worth looking at (shown above). Plotting views against the hour the tweet was posted reveals a clear pattern:

- The majority of tweets were posted between **12:00–17:00 UTC**
- Those tweets cluster at low-to-medium view counts
- The single highest-performing tweet was posted at **~21:00 UTC**
- The 21:00 UTC slot outperformed the 12:00–17:00 daytime cluster by **3–4×**

The sample size isn't large enough to claim this is a universal finding, but it's a clear enough signal to be worth testing deliberately. The hypothesis is that 21:00 UTC (22:00 BST / 17:00 EST) hits the evening peak for both European and North American audiences simultaneously — a brief window where both timezones are active.

## Cross-Platform Architecture

Posting to both platforms from one call required handling two completely different authentication models:

- **Twitter/X**: OAuth 1.0a with `requests-oauthlib`, posting via the v2 API
- **Bluesky**: AT Protocol (`atproto` library), which uses a DID-based identity system rather than OAuth

Both are wrapped behind a common interface so the posting logic doesn't need to care which platform it's talking to.

## OpenAI Integration

An optional step in the pipeline passes a draft post through GPT with a short prompt asking it to suggest improvements for engagement. This is useful for converting raw notes into something more polished, but the final edit always stays with the human.
