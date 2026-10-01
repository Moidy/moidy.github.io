---
title: The Dollhouse
subtitle: Interactive Chat TTS Overlay
status: Active
image: /img/dollhouse/primary.png
image_alt: The Dollhouse interactive chat TTS overlay
tags: [Python, TwitchIO, PyArcade]
---

## What is it?

The dollhouse is heavily based off of the work that Shindigs, a twitch and youtube creator did with interactive chat overlays and character effects.
[www.twitch.tv/shindigs](https://www.twitch.tv/shindigs)

You can check out Shindigs' work for inspiration on interactive chat overlays and character effects.

While his is a source of inspiration, the Dollhouse aims to expand on these ideas by adding more interactive elements and character effects for viewers.

I diverged quite a bit and I tried to make it my own. I built mine in Python arcade to leverage its capabilities for creating interactive and visually appealing character effects.
I use the existing twitch integrations I have built prior for other tools to poll for users in twitch to render their corresponding characters within the dollhouse environment.

Given that a good base fo my twitch community lives for customization and having their own unique presence, I opted for customizable images for viewers depending on their names and if I have an image file associated with them. Often this is sent to me via discord and included within the repository so its still quite high trust basis only, and not something that is publicly accessible without my approval.

## Key Features

- Customizable viewer characters based on Twitch usernames and associated images.
- Interactive chat overlay that responds to viewer actions and commands.
- Visually appealing character effects built using Python arcade.
- Integration with existing Twitch tools for real-time user polling.
- High-trust system for adding new viewer images via Discord submissions.
- A lot of punishment mechanics

## Effects

 - I can tape characters to surfaces within the dollhouse environment.
 - Cursor for lifting and throwing characters within the dollhouse environment.
 - !flip and !spin commands for character manipulation within the dollhouse environment.
 - Punishment mechanics that affect characters within the dollhouse environment.
    - Fire, acts as a mute and makes the character run around faster with
    - Freeze, immobilizes the character with a ice image effect over it.
    - Shame sign, displays a visual indicator of shame over the character.
    - Explosion, causes the character to explode with a visual effect.
    - Knife, Allows viewers to !stab characters within the dollhouse environment.
    - Crown, Just gives a viewer a little crown visual effect.
    - Tiny, shrinks the character to a smaller size within the dollhouse environment.
    - Dunce cap, places a dunce cap on the character's head as a visual indicator of punishment.
    - Black hole, creates a black hole that pulls all characters towards it within the dollhouse environment.
    - Jail, creates a jail area where characters can be dragged into as a form of punishment within the dollhouse environment.
    - Confetti, creates a burst of confetti around the character as a visual effect.
    - Clone, creates temporary clones of the character within the dollhouse environment.

### Quick Reference
- **Left Click + Drag**: Move sprite around
- **Right Click**: Release taped sprite / Clear punishments
- **SPACEBAR**: Tape/Untape sprite (while dragging)
- **DELETE**: Remove sprite from game
- **E**: Explode selected sprite (3s respawn)
- **F**: Toggle fire on selected sprite
- **K**: Cycle crown/knife accessories on selected sprite
- **SHIFT + K / N**: Give/toggle knives on ALL avatars
- **P**: Cycle through punishments (dunce cap, shame sign, tiny)
- **I**: Toggle freeze on/off (no timer)
- **C**: Spawn 5 temporary clones of selected sprite (30s)
- **B**: Toggle black hole on/off (pulls all sprites in)
- **J**: Toggle jail visibility (drag sprites into jail)
- **T**: Test random particle effect on selected sprite

**Chat Commands** (viewers can type in Twitch chat):
- **!flip**: Flip your sprite
- **!spin**: Spin your sprite
- **!stab [username]**: Chase and stab another viewer (requires knife, 10s cooldown)
