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
- MOD/FX types: 0 T.Wah, 1 Auto Wah, 2 Pedal Wah, 3 Compressor, 4 Limiter, 6 Graphic EQ, 7 Para EQ, 9 Guitar Sim, 10 Slow Gear, 12 Wave Synth, 14 Octave, 15 Pitch Shifter, 16 Harmonist, 18 AC Processor, 19 Phaser, 20 Flanger, 21 Tremolo, 22 Rotary, 23 Uni-V, 25 Slicer, 26 Vibrato, 27 Ring Mod, 28 Humanizer, 29 2x2 Chorus, 31 AC Guitar Sim, 35 Phaser 90E, 36 Flanger 117E, 37 Wah 95E, 38 DC-30, 39 Heavy Octave (37-39 need Gen 1 firmware 4; confirmed from the BOSS TONE STUDIO 4.0 type list). MkII-only: 40 Pedal Bend (Gen 1 has Pedal Bend only in the Pedal FX block). Colour slots accept 35+ even though BTS lists the range as 0-31 (factory presets use 35/36).
- Delay types 0-10: Digital, Pan, Stereo, Dual series, Dual parallel, Dual L/R, Reverse, Analog, Tape Echo, Modulate, SDE-3000.
- Reverb types: the BTS 4.0 menu offers 1 Room, 3 Hall, 4 Plate, 5 Spring, 6 Modulate (same ids as MkII; 0 Ambience and 2 Hall1 exist in the engine but are not in the Gen 1 menu). reverb_spring_sens matches MkII byte 5:0x4A (both default 5); MkII 5:0x4B Spring Color has no Gen 1 key.
- Pedal FX: pedal_fx_on_off, pedal_fx_type (0 Wah, 1 Pedal Bend, 2 Wah 95E), pedal_fx_wah_*, pedal_fx_pedal_bend_* (pitch raw 0-48, 24 = 0), pedal_fx_evh95_*, pedal_fx_position (0 input, 1 post amp). Same order as MkII 5:0x50-0x60, position at 6:0x23.
- Patch level raw 100 in every Gen 1 preset (BTS shows it doubled); MkII raw value is copied 1:1.
- Chain ids (both generations): 0 CS, 1 Loop, 2 Amp, 3 Ch B, 4 EQ1, 5 MOD, 6 FX, 7 Delay1, 8 Delay2, 9 Reverb, 10 EQ2, 11 Pedal FX, 12 FV, 13 NS, 14 NS2, 15 Booster, 16 USB, 17 Split, 18 Cab, 19 Merge. Real Gen 1 chains are Split, the used blocks, then 18 0 3 10 19 14 16. chain_ptn 0 = Booster+MOD after amp, 1 = before amp, 2 = Delay/FX also before amp.
- Graphic EQ flat = 24; parametric EQ gain flat = 20. eq_position 0 = amp in, 1 = amp out.
- Effect colour slots: fxbox_asgn_{fx1a=Booster, fx1b=MOD, fx2a=Delay1, fx2b=FX, fx3=Reverb, fx3b=Delay2}_{g,r,y}; fx_active_ab_fx1 (0 booster, 1 mod); fx_active_ab_fx2 (0 delay, 1 FX).
- Level matching is done with preamp_a_level (high-gain patches use a lower amp level) and patch_level; the user must listen to balance channels.

## MkII .tsl format
- JSON device "KATANA MkII", formatRev "0002", data[[{memo, paramSet{"UserPatch%Name":[hex bytes]}}]].
- Each block is a slice of the MkII memory map: address = (page<<7)|offset. Block starts: PatchName (0,0x00), Patch_0 (0,0x10), Eq(2) (0,0x60), Fx(1) (1,0), Fx(2) (3,0), Delay(1) (5,0), Delay(2) (5,0x20), Patch_1 (5,0x40), Patch_2 (6,0x20), Status (6,0x50). The Status block is front-panel state, not patch data.
- formatRev 0001 and 0002 both occur. In many 0001 files Patch_1 is only 50 bytes, so the chain (6:0x00-0x13) is all zero and only the chain pattern 6:0x20 (0-6) is stored. Patterns, from real patches: 0 BST|MOD FX DLY1, 1 BST MOD|FX DLY1, 2 BST MOD FX|DLY1, 3 all before amp, 4 MOD BST|FX DLY1, 6 MOD BST FX DLY1| (5 inferred).
- Amp type ids 28-32 (0x1C-0x20) are the Variation voices; panel Variation flag is 6:0x5C. Colour slot select (6:0x39-0x3D) is 0 green, 1 red, 2 yellow (FxFloorBoard's labels are wrong; checked on 146 patches). Cab Resonance 6:0x43 (0 Vintage, 1 Modern, 2 Deep). Solo 6:0x14, Contour 6:0x16/0x17. Patch_Mk2V2 begins with Solo EQ settings.
- Not convertible to Gen 1: Variation amp voicing, Contour, Solo EQ, EQ2 (unless EQ1 is off), Cab Resonance, MkII-only boosters. The converter notes these.

## Gen 3 .tsl format
- device "KATANA Gen3", blocks named PATCH%AMP, PATCH%BOOSTER(1-3), PATCH%FX(1-6) + FX_DETAIL(1-6), PATCH%DELAY(1-6), PATCH%REVERB(1-3), PATCH%EQ_PEQ/GE10, etc. No address map is available, so the converter refuses Gen 3 files. Sample Gen 3 files are in github.com/syndicalt/katana-rs assets/patches.

## Sources used for verification
- Gen 1: BOSS TONE STUDIO for KATANA 4.0 (C:/Program Files (x86)/BOSS TONE STUDIO for KATANA): _assets/data/addressmap_gt.json, katana_preset_patches.tsl, and the value lists and min/max in the decompressed SWF (ABC bytecode).
- MkII: midi.xml from KATANA-MK2-FxFloorBoard (copy in github.com/syndicalt/katana-rs assets/midi.xml), plus about 80 real MkII .tsl files in the same repo.

## Unverified / still open
- No same-patch pair exported from both a MkII and a Gen 1 exists, so the mapping is checked against the two editors' parameter maps only.
- What the MkII Variation voices and Cab Resonance correspond to on Gen 1 is unknown; Gen 1 hidden amp types 0-27 might get closer but there is no data to choose.
- The tkinter window was only tested with mocks (no display available) - ask him whether it opens correctly on Windows.
- Song-based tones (Decode, Are You Mine, Iron Man, Do I Wanna Know, Back in Black, The Pretender, Thunderstruck, Highway to Hell, Everlong, Between Angels and Insects, For Whom the Bell Tolls, Aerials, 505) were first guesses; ask which channels sounded wrong and refine.
