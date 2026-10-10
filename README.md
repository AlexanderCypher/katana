# Katana Patch Converter (MkII → Gen 1)

Convert patch files made for the **BOSS Katana MkII** into patches a **Katana Gen 1** can import in **BOSS TONE STUDIO**.

[![Tests](https://github.com/AlexanderCypher/katana/actions/workflows/test.yml/badge.svg)](https://github.com/AlexanderCypher/katana/actions/workflows/test.yml)
[![Latest release](https://img.shields.io/github/v/release/AlexanderCypher/katana)](https://github.com/AlexanderCypher/katana/releases/latest)

## Download

**Windows:** download `KatanaPatchConverter.exe` from the [latest release](https://github.com/AlexanderCypher/katana/releases/latest) and double-click it. No installation needed.

**Mac, Linux, or Windows without the .exe:** install [Python 3](https://www.python.org/downloads/) (on Windows, tick **"Add python.exe to PATH"** in the installer), download [`katana_to_gen1.py`](katana_to_gen1.py) and double-click it, or run `python katana_to_gen1.py`.

**Before you import:** update your Gen 1 amp to firmware 4 and use BOSS TONE STUDIO 4. Converted patches can use Wah 95E, DC-30, Heavy Octave and Pedal FX, which older firmware does not have.

## How to use

1. Open the converter. A window opens.
2. Click **Choose patch files...** (Ctrl+O) and pick one or more MkII `.tsl` files.
3. Click **Convert to Gen 1** (Enter). A progress bar shows how far it has got.
4. The results list shows each file and its patches. Click one to see its notes on the right.
5. Click **Open the folder with my new files**. Each new file ends in `(Gen1).tsl`.
6. In BOSS TONE STUDIO, with your Gen 1 Katana connected, click **Import** and choose the `(Gen1).tsl` file.

You can also drag `.tsl` files onto the program, or convert from a terminal:

```
python katana_to_gen1.py "My Patch.tsl"            # opens the window and converts the file
python katana_to_gen1.py --cli "My Patch.tsl"      # text only, no window
```

Your original files are never changed, and existing files are never overwritten.

Click **Windows XP look** for a Windows XP style window (click **Modern look** to switch back).

The app remembers the last folder you used, the **Gen 1 button style** choice, the look and the window size. To keep these settings next to the program instead (for example on a USB stick), put an empty file named `portable.txt` in the same folder as the program.

## Live sets for gigs

Click **Build a live set...** to put patches in the order you play them:

1. **Add patches...** takes Gen 1 `.tsl` files, converted `(Gen1).tsl` files, or MkII files (converted for you).
2. Use **Move up / Move down** to set the song order. **Rename...** gives a patch a song name, and **Song note...** adds a note for the set list (for example "capo 2").
3. Leave **Put the first 8 on the amp channels** ticked to place songs 1-8 on A: CH1 to B: CH4.
4. **Save live set** writes `<name> (Live Set).tsl` to import in BOSS TONE STUDIO, plus a printable `<name> (Set List).txt`.

A level check points out patches set much louder or quieter than the rest of the set. It only reads the settings, so always check volumes by ear at rehearsal.

From a terminal: `python katana_to_gen1.py --live-set "Friday gig" song1.tsl song2.tsl song3.tsl`

## What the notes mean

After converting, every patch is listed. Lines starting with `*` are settings the Gen 1 cannot reproduce exactly. The patch is still converted; listen to it and adjust to taste.

| Note | What it means |
|---|---|
| Variation amp | Gen 1 has no MkII "Variation" voices, so the standard voice is used. This is the most common reason a converted patch sounds different; try a little more or less gain and treble. |
| Cab Resonance (Modern / Deep) | Gen 1 has no Cab Resonance setting, so the low end may differ. |
| Contour / Solo EQ / second EQ | Gen 1 has no equivalent, so these are not applied. |
| MkII-only booster | HM-2, Metal Core and Centa OD become the closest Gen 1 booster (Metal Zone, Metal DS, Blues Drive). |
| Pedal Bend | On Gen 1 it lives in the Pedal FX slot, so it is moved there (needs an expression pedal). |
| Hidden amp voice | The patch uses an amp type that is not one of the five panel voices. Gen 1 loads it, but it may not be the same voice as on the MkII. |
| Reverb not in the menu | Ambience and Hall 1 work on Gen 1 but are not listed in BOSS TONE STUDIO, so the editor may show the reverb type oddly. |
| Pedal FX function | The MkII "Pedal FX" pedal setting becomes Gen 1's "Pedal FX / Foot Volume". |
| Both effects ON | On Gen 1, Booster/MOD and Delay/FX share a button. Both stay on by default, which is closest to the original sound. Tick **Gen 1 button style** to keep only one. |

## What is converted

Patch name, booster, amp (type, gain, EQ, level and more), EQ, MOD and FX effects (including Wah 95E, DC-30 and Heavy Octave), Pedal FX, both delays, reverb, noise suppressor, send/return, foot volume, patch level, effect order, the green/red/yellow effect slots, and expression pedal / GA-FC pedal and knob assignments.

**Not converted:** Variation amp voicing, Contour, Solo EQ, the second EQ, Cab Resonance, the MkII-only boosters, and Pedal Bend pedal assignments.

## Known limitations

- **Katana Gen 3 files are not supported yet.** Gen 3 uses a different patch layout; the converter says so instead of producing a broken file.
- The mapping is checked against both editors' parameter lists and real patches from each amp, but not yet against the same patch saved on both amps. See [open issues](https://github.com/AlexanderCypher/katana/issues).

## How it works

A MkII `.tsl` stores each patch as blocks of bytes copied from the amp's memory. The converter rebuilds that memory image, then writes each setting into a complete Gen 1 patch, translating values that differ between the two generations. The Gen 1 patch structure is built into the program, so it is a single file with no dependencies.

The MkII memory map comes from [FxFloorBoard / katana-rs](https://github.com/syndicalt/katana-rs). Gen 1 effect numbers and value ranges were checked against BOSS TONE STUDIO for KATANA 4.0.

## Contributing

Bug reports and patch files that convert badly are welcome in [Issues](https://github.com/AlexanderCypher/katana/issues). A patch saved on both a MkII and a Gen 1 is especially useful.

Run the tests (standard library only):

```
python -m unittest discover -s tests -v
```

Set `KATANA_SAMPLES` to the `assets/patches` folder of [katana-rs](https://github.com/syndicalt/katana-rs) to include real MkII patches (CI does this on every push), and `KATANA_GEN1_SAMPLES` to a folder of Gen 1 `.tsl` files to check the output against real Gen 1 patches. Developer reference data is in [`reference/`](reference/).

BOSS, KATANA and BOSS TONE STUDIO are trademarks of Roland Corporation. This project is not affiliated with or endorsed by Roland.
