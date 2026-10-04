# Boss Katana Patch Converter (MkII to Gen 1)

A standalone Python utility to safely downgrade and convert **BOSS Katana MkII** tone patch files (`.tsl`) into the named parameter format required by **Gen 1 (MkI) amplifiers**. 

This script features a built-in Gen 1 template and parameter map, meaning it requires **zero external dependencies or spreadsheets** to run.

## ✨ Features

*   **All-in-One Script:** The conversion template and parameter map are fully embedded. You only need `katana_to_gen1.py`.
*   **Batch Processing:** Select or drop multiple `.tsl` files or an entire liveset all at once.
*   **Smart Skipping:** Automatically detects and skips files that are already in Gen 1 format, files already labeled `(Gen1)`, or files that are not valid Katana patches.
*   **Error-Resistant:** If a patch is missing a specific configuration section, the script safely falls back to default values and reports the issue instead of crashing.
*   **Clear Summary Logs:** The console window stays open after processing so you can easily read exactly what changes were made to your patches.

## 🚀 How to Use

There are three flexible ways to run the converter:

### 1. Graphical File Picker (Easiest)
Simply **double-click** `katana_to_gen1.py`. A file explorer window will pop up allowing you to select one or multiple `.tsl` files from your computer.

### 2. Drag and Drop
Highlight your `.tsl` files in Windows File Explorer and **drag and drop** them directly on top of the `katana_to_gen1.py` script icon.

### 3. Command Line
Open your terminal or Command Prompt and pass the file paths as arguments:
```bash
python katana_to_gen1.py "Your Patch Name.tsl"
```

*Output files are cleanly saved right next to the original files as `<original_name> (Gen1).tsl`.*

## ⚠️ Important Architectural Translation Notes

Because Gen 1 (MkI) hardware has a different internal structure than newer models, the converter makes the following safety adjustments during translation:

*   **Amp Types:** MkII-exclusive amp voices (such as Variation modes) do not exist on Gen 1. These are automatically reverted to the **Brown** amp channel, and a note is generated in the summary window.
*   **Booster vs. MOD:** The MkII allows both slots to run simultaneously. Gen 1 hardware shares this slot. The script prioritizes and **keeps the Booster** while turning the MOD effect off.
*   **Delay vs. FX2:** Like the effect slots above, Gen 1 shares this hardware slot. The script **keeps the Delay** settings active and disables FX2.

## 🧪 Gen 3 (Katana-Go / Gen 3 Amps) Support
Gen 3 support is currently **untested** but structurally built-in. The script accepts any patch file containing `KATANA` in its device string under the assumption that Gen 3 retains the standard MkII layout. 

If you encounter an issue or a failed import with a Gen 3 patch, please open an Issue and attach the broken `.tsl` file so it can be analyzed and patched!
