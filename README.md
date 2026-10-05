# Katana Patch Converter (MkII → Gen 1)

Turns patch files made for the **BOSS Katana MkII** into patch files your **Gen 1 Katana** can import in **BOSS TONE STUDIO**.

## How to use it (no technical knowledge needed)

**One-time setup (Windows):**
1. Install Python from <https://www.python.org/downloads/>. On the first screen of the installer, **tick "Add python.exe to PATH"**, then click *Install Now*.
2. Download `katana_to_gen1.py` from this page (click the file, then the download button).
3. Update your Gen 1 amp to the latest firmware (version 4) and use BOSS TONE STUDIO 4. Converted patches can use Wah 95E, DC-30, Heavy Octave and Pedal FX, which older firmware does not have.

**Every time you want to convert a patch:**
1. Double-click `katana_to_gen1.py`. A window opens.
2. Click **Choose patch files...** and pick your downloaded `.tsl` file(s).
3. Click **Convert to Gen 1**.
4. Click **Open the folder with my new files**. The new file ends in `(Gen1).tsl`.
5. Open BOSS TONE STUDIO with your Gen 1 Katana connected, click **Import**, and choose the `(Gen1).tsl` file.

You can also drag `.tsl` files onto `katana_to_gen1.py`, or run `python katana_to_gen1.py "My Patch.tsl"` in a terminal.

Prefer a normal app with no Python? If a `.exe` is listed under **Releases**, download and double-click that instead.

## What the messages mean

After converting, each patch is listed. Lines starting with `*` are things the Gen 1 amp cannot do exactly:

- **Variation amp**: MkII "Variation" amp voices do not exist on Gen 1, so the normal version of that amp is used. This is the most common reason a converted patch sounds different. Try a little more or less gain and treble to taste.
- **Cab Resonance (Modern / Deep)**: Gen 1 has no Cab Resonance setting, so the low end may sound different.
- **Contour / Solo EQ / second EQ**: Gen 1 has no equivalent, so these are not applied.
- **MkII-only booster** (HM-2, Metal Core, Centa OD): swapped for the closest Gen 1 booster (Metal Zone, Metal DS, Blues Drive).
- **Pedal Bend**: on Gen 1 it lives in the Pedal FX slot, so it is moved there (needs an expression pedal).
- **Both effects ON**: on Gen 1 some effects share one button (Booster/Mod, Delay/FX). By default both stay on, which is closest to the original sound. Tick **Gen 1 button style** to keep only one.

Patches with these notes are still converted. Listen to them and adjust to taste. Your original files are never changed, and existing files are never overwritten.

## What is converted

Patch name, Booster, Amp (type, gain, EQ knobs, level, etc.), EQ (parametric or graphic, amp in/out), MOD and FX effects (all of them, including Wah 95E, DC-30 and Heavy Octave), Pedal FX (wah, pedal bend, Wah 95E), both Delays, Reverb, noise suppressor, send/return, foot volume, patch level, effect order, and the green/red/yellow effect slots.

The effect order is laid out the way real Gen 1 patches are. Older MkII files that only store a chain "pattern" number are converted to the matching order. Earlier versions of this converter got that wrong.

## What is not converted

Variation amp voicing, Contour, Solo EQ, the second EQ, Cab Resonance, and the MkII-only boosters. Settings that control pedals and footswitches (EXP / GA-FC assignments) are also not copied.

## Known limits

- **Katana Gen 3 files can not be converted yet.** Gen 3 stores patches in a completely different layout. The converter says so instead of producing a broken file.
- Converted tones were not compared with the same patch exported from a real Gen 1. A pair of files (the same patch from both amps) would let the mapping be checked exactly.

## How it works (for the curious)

A MkII `.tsl` stores each patch as blocks of hex bytes that are slices of the amp's memory map. The script rebuilds that memory image, then copies each parameter into a real Gen 1 patch, translating values that differ between generations. The Gen 1 structure is built into the script, so there are no other files to keep.

The MkII memory map was checked against the parameter map from [FxFloorBoard / katana-rs](https://github.com/syndicalt/katana-rs). The Gen 1 effect numbers and value ranges were checked against BOSS TONE STUDIO for KATANA 4.0.
