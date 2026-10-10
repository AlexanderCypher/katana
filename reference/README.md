# Reference files

These files are kept for developers. The converter does not use them; its Gen 1 template is built into `katana_to_gen1.py`.

| File | What it is |
|---|---|
| `gen1_template.tsl` | A one-patch Gen 1 export ("Clean") in the older BOSS TONE STUDIO format with **1057** parameter keys. Current exports, and the converter's output, have **1505** keys, so do not use this file to check converter output. |
| `katana_tsl_map.csv` | 906 Gen 1 parameter names with their address, byte offset and size in the Gen 1 patch memory map (`Supported` = 1 when the parameter exists on the amp). Useful for mapping work such as Gen 3 support or new parameters. |
