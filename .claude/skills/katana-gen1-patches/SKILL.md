---
name: katana-gen1-patches
description: Build, fix or convert BOSS Katana Gen 1 (MkI) .tsl patch files and the MkII/Gen 3 to Gen 1 converter; use for Katana tones, live sets, or converter bugs.
---

# Katana Gen 1 patches and converter

The user (Al) owns a BOSS Katana Gen 1 and publishes a converter at github.com/AlexanderCypher/katana (katana_to_gen1.py, v4, single file with a built-in template and a tkinter window). Work from the script in the repo instead of rebuilding from memory.

## Rules for working
- Claude cannot hear audio. Never claim a tone sounds good; give a starting point and ask him to describe what he hears, then adjust.
- Do not copy preset collections as the user's tones if he asks for self-built ones; he found some preset-based sets unreliable.
- Use documentation and verified data over opinions from tone-matching websites (they disagree with each other).
- Never overwrite his files; output new files.

## Gen 1 .tsl format (verified from real exports)
- JSON: device "GT", version "1.0.0", liveSetData{id,name,...}, patchList[...].
- Each patch: id, name (16 chars, space padded), patchNo ("A: CH1".."B: CH4", or null in library packs), orderNumber, liveSetId, category, params with 1505 named keys.
- Build new patches by copying a full 1505-key patch (the default "KATANA PANEL" patch) and changing only keys; the key set must stay identical.
- 2-byte values are stored as key (=hi*128+lo) plus key_h and key_l (delay_delay_time 400 -> h=3, l=16).
- Patch name is stored as patch_name1..16 (ASCII) plus patchname.

## Verified parameter facts
- Amp types: 8 Clean, 11 Crunch, 23 Brown, 24 Lead (also 0-27 exist). Gain and booster drive go up to 120.
- Booster types: 0 Mid Boost, 1 Clean Boost, 2 Treble Boost, 3 Crunch OD, 4 Natural OD, 5 Warm OD, 6 Fat DS, 8 Metal DS, 9 OCT Fuzz, 10 Blues Drive, 11 Over Drive, 12 Tubescreamer, 13 Turbo OD, 14 Distortion, 15 Rat, 16 GuV DS, 17 DST+, 18 Metal Zone, 19 60s Fuzz, 20 Muff Fuzz. MkII-only: 21 HM-2, 22 Metal Core, 23 Centa OD.
- MOD/FX types: 0 T.Wah, 1 Auto Wah, 2 Pedal Wah, 3 Compressor, 4 Limiter, 6 Graphic EQ, 7 Para EQ, 9 Guitar Sim, 10 Slow Gear, 12 Wave Synth, 14 Octave, 15 Pitch Shifter, 16 Harmonist, 18 AC Processor, 19 Phaser, 20 Flanger, 21 Tremolo, 22 Rotary, 23 Uni-V, 25 Slicer, 26 Vibrato, 27 Ring Mod, 28 Humanizer, 29 2x2 Chorus, 31 AC Guitar Sim, 35 Phaser 90E, 36 Flanger 117E. MkII-only: 37 Wah 95E, 38 Delay/Chorus 30, 39 Heavy Octave, 40 Pedal Bend.
- Delay types 0-10: Digital, Pan, Stereo, Dual series, Dual parallel, Dual L/R, Reverse, Analog, Tape Echo, Modulate, SDE-3000.
- Reverb types (same numbering as MkII, inferred from real Gen 1 presets, fairly but not fully certain): 0 Ambience, 1 Room, 2 Hall1, 3 Hall2, 4 Plate, 5 Spring, 6 Mod. reverb_spring_sens only matters for Spring.
- Graphic EQ flat = 24; parametric EQ gain flat = 20. eq_position 0 = amp in, 1 = amp out.
- Effect colour slots: fxbox_asgn_{fx1a=Booster, fx1b=MOD, fx2a=Delay1, fx2b=FX, fx3=Reverb, fx3b=Delay2}_{g,r,y}; fx_active_ab_fx1 (0 booster, 1 mod); fx_active_ab_fx2 (0 delay, 1 FX).
- Level matching is done with preamp_a_level (high-gain patches use a lower amp level) and patch_level; the user must listen to balance channels.

## MkII .tsl format
- JSON device "KATANA MkII", formatRev "0002", data[[{memo, paramSet{"UserPatch%Name":[hex bytes]}}]].
- Each block is a slice of the MkII memory map: address = (page<<7)|offset. Block starts: PatchName (0,0x00), Patch_0 (0,0x10), Eq(2) (0,0x60), Fx(1) (1,0), Fx(2) (3,0), Delay(1) (5,0), Delay(2) (5,0x20), Patch_1 (5,0x40), Patch_2 (6,0x20), Status (6,0x50). The Status block is front-panel state, not patch data.
- Not convertible to Gen 1: Variation amp voicing, Contour, Solo EQ, EQ2 (unless EQ1 is off), Cab Resonance, Pedal FX slot, Delay/Chorus 30, Pedal Bend. The converter notes these.

## Unverified / still open
- No same-patch pair exported from both a MkII and a Gen 1 exists, so the mapping is checked against documentation only.
- Gen 3 .tsl files are untested.
- The tkinter window was only tested with mocks (no display available) - ask him whether it opens correctly on Windows.
- Song-based tones (Decode, Are You Mine, Iron Man, Do I Wanna Know, Back in Black, The Pretender, Thunderstruck, Highway to Hell, Everlong, Between Angels and Insects, For Whom the Bell Tolls, Aerials, 505) were first guesses; ask which channels sounded wrong and refine.
