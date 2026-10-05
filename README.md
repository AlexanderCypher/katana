# Katana Patch Converter (MkII / Gen 3 → Gen 1)

Turns patch files made for the **BOSS Katana MkII or Gen 3** into patch files your **Gen 1 Katana** can import in **BOSS TONE STUDIO**.

## How to use it (no technical knowledge needed)

**One-time setup (Windows):**
1. Install Python from <https://www.python.org/downloads/>. On the first screen of the installer, **tick "Add python.exe to PATH"**, then click *Install Now*.
2. Download `katana_to_gen1.py` from this page (click the file, then the download button).

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

- **Variation amp** – MkII/Gen 3 "Variation" amp voices do not exist on Gen 1. The normal version of that amp is used.
- **Contour / Solo EQ / second EQ** – Gen 1 has no equivalent, so these are not applied.
- **Effect not available on Gen 1** – a few MkII-only effects/boosters are swapped for the closest Gen 1 one, or switched off. The message says which.
- **Both effects ON** – on Gen 1 some effects share one button (Booster/Mod, Delay/FX). By default both stay on, which is closest to the original sound. Tick **Gen 1 button style** to keep only one.

Patches with these notes are still converted. Listen to them and adjust to taste. Your original files are never changed, and existing files are never overwritten.

## What is converted

Patch name, Booster, Amp (type, gain, EQ knobs, level, etc.), EQ, MOD and FX effects (all parameters Gen 1 has), both Delays, Reverb, noise suppressor, send/return, foot volume, patch level, effect order, and the green/red/yellow effect slots.

## What is not converted

Contour, Solo EQ, the second EQ, Cab Resonance, the pedal-FX slot, the MkII-only effects (Delay/Chorus 30, Pedal Bend), and Variation amp voicing. Settings that control pedals and footswitches (EXP / GAFC assignments) are also not copied.

## Known limits

- Tested with MkII patch files. **Gen 3 files are untested** - if one fails, please open an Issue and attach it.
- Converted tones were not compared to the same patch exported from a real Gen 1; a pair of files (the same patch from both amps) would let the mapping be checked exactly.

## How it works (for the curious)

A MkII `.tsl` stores each patch as blocks of hex bytes that are slices of the amp's memory map. The script rebuilds that memory image, then copies each parameter into a real Gen 1 patch, translating values that differ between generations. The Gen 1 structure is built into the script, so there are no other files to keep.
