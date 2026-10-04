#!/usr/bin/env python3
"""
katana_to_gen1.py - convert BOSS Katana MkII / Gen 3 .tsl patch files to Katana Gen 1.

EASIEST WAYS TO USE (single file, nothing else needed):
  1. Double-click this file -> a file picker opens -> select one or more .tsl files.
  2. Drag one or more .tsl files onto this file.
  3. Command line:  python katana_to_gen1.py "Some Patch.tsl" "Another.tsl"
Each result is saved next to the original as "<name> (Gen1).tsl".
"""
import base64, copy, json, os, random, sys, zlib

TEMPLATE_B64 = "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"
OFFSETS = json.loads('{"od_ds_on_off":48,"od_ds_type":49,"od_ds_drive":50,"od_ds_bottom":51,"od_ds_tone":52,"od_ds_solo_sw":53,"od_ds_solo_level":54,"od_ds_effect_level":55,"od_ds_direct_mix":56,"od_ds_custom_type":57,"od_ds_custom_bottom":58,"od_ds_custom_top":59,"od_ds_custom_low":60,"od_ds_custom_high":61,"od_ds_custom_character":62,"preamp_a_on_off":80,"preamp_a_type":81,"preamp_a_gain":82,"preamp_a_t_comp":83,"preamp_a_bass":84,"preamp_a_middle":85,"preamp_a_treble":86,"preamp_a_presence":87,"preamp_a_level":88,"preamp_a_bright":89,"preamp_a_gain_sw":90,"preamp_a_solo_sw":91,"preamp_a_solo_level":92,"preamp_a_sp_type":93,"preamp_a_mic_type":94,"preamp_a_mic_dis":95,"preamp_a_mic_pos":96,"preamp_a_mic_level":97,"preamp_a_direct_mix":98,"preamp_a_custom_type":99,"preamp_a_custom_bottom":100,"preamp_a_custom_edge":101,"preamp_a_custom_preamp_low":104,"preamp_a_custom_preamp_high":105,"preamp_a_custom_char":106,"preamp_a_custom_sp_size":107,"preamp_a_custom_sp_color_low":108,"preamp_a_custom_sp_color_high":109,"preamp_a_custom_sp_num":110,"preamp_a_custom_sp_cabinet":111}')

MAX_MK1_AMP = 27     # Gen 1 amp types are 0-27
FALLBACK_AMP = 23    # BROWN, used for MkII/Gen3-only amp voices

FX_GROUPS = [
    ("t_wah", ["mode", "polar", "sens", "freq", "peak", "direct_mix", "effect_level"]),
    ("auto_wah", ["mode", "freq", "peak", "rate", "depth", "direct_mix", "effect_level"]),
    ("sub_wah", ["type", "pedal_pos", "pedal_min", "pedal_max", "effect_level", "direct_mix"]),
    ("adv_comp", ["type", "sustain", "attack", "tone", "level"]),
    ("limiter", ["type", "attack", "thresh", "ratio", "release", "level"]),
    ("graphic_eq", ["31hz", "62hz", "125hz", "250hz", "500hz", "1khz", "2khz", "4khz", "8khz", "16khz", "level"]),
    ("parametric_eq", ["low_cut", "low_gain", "low_mid_freq", "low_mid_q", "low_mid_gain",
                       "high_mid_freq", "high_mid_q", "high_mid_gain", "high_gain", "high_cut", "level"]),
    ("tone_modify", ["type", "reso", "low", "high", "level"]),
]
DELAY_FIELDS = ["on_off", "type", "delay_time*", "f_back", "high_cut", "effect_level", "direct_mix",
                "tap_time", "d1_time*", "d1_f_back", "d1_hi_cut", "d1_level", "d2_time*", "d2_f_back",
                "d2_hi_cut", "d2_level", "mod_rate", "mod_depth", "vtg_lpf", "vtg_feedback_phase",
                "vtg_filter", "vtg_effect_phase", "vtg_mod_sw"]   # * = 2-byte value
REVERB_FIELDS = ["on_off", "type", "time", "pre_delay*", "low_cut", "high_cut", "density",
                 "effect_level", "direct_mix", "spring_sens"]


def hx(x):
    return int(x, 16)


def load_template():
    return json.loads(zlib.decompress(base64.b64decode(TEMPLATE_B64)).decode("utf-8"))


def put(params, key, val, log):
    if key in params:
        params[key] = val
    else:
        log.append(f"skipped (not in Gen 1 file): {key}")


def put2(params, base, hi, lo, log):
    put(params, base, hi * 128 + lo, log)
    put(params, base + "_h", hi, log)
    put(params, base + "_l", lo, log)


def block(blocks, name, log):
    v = blocks.get(name)
    if v is None:
        log.append(f"block {name} missing in source - left at template default")
        return None
    return [hx(x) for x in v]


def convert_patch(blocks, tpl_patch, log):
    P = copy.deepcopy(tpl_patch)
    p = P["params"]

    raw = block(blocks, "UserPatch%PatchName", log)
    if raw:
        name = bytes(raw).decode("ascii", "replace").rstrip()
        for i, c in enumerate(raw):
            put(p, f"patch_name{i+1}", c, log)
        p["patchname"] = name
        P["name"] = name.ljust(16)

    p0 = block(blocks, "UserPatch%Patch_0", log)
    if p0:
        for key, off in OFFSETS.items():
            if key.startswith("od_ds_") and 48 <= off <= 62:
                put(p, key, p0[off - 48], log)
            elif key.startswith("preamp_a_") and 80 <= off <= 111:
                put(p, key, p0[off - 80 + 16], log)
        if p0[17] > MAX_MK1_AMP:
            log.append(f"amp type {p0[17]} is not a Gen 1 amp - set to BROWN ({FALLBACK_AMP}); check it in Tone Studio")
            p["preamp_a_type"] = FALLBACK_AMP

    for n in (1, 2):
        blk = block(blocks, f"UserPatch%Fx({n})", log)
        if not blk:
            continue
        put(p, f"fx{n}_on_off", blk[0], log)
        put(p, f"fx{n}_fx_type", blk[1], log)
        i = 2
        for grp, names in FX_GROUPS:
            for nm in names:
                put(p, f"fx{n}_{grp}_{nm}", blk[i], log)
                i += 1

    for n, pre in ((1, "delay_"), (2, "delay2_")):
        d = block(blocks, f"UserPatch%Delay({n})", log)
        if not d:
            continue
        i = 0
        for f in DELAY_FIELDS:
            if f.endswith("*"):
                put2(p, pre + f[:-1], d[i], d[i + 1], log)
                i += 2
            else:
                put(p, pre + f, d[i], log)
                i += 1

    r = block(blocks, "UserPatch%Patch_1", log)
    if r:
        i = 0
        for f in REVERB_FIELDS:
            if f.endswith("*"):
                put2(p, "reverb_" + f[:-1], r[i], r[i + 1], log)
                i += 2
            else:
                put(p, "reverb_" + f, r[i], log)
                i += 1

    put(p, "fxbox_asgn_fx1a_g", p["od_ds_type"], log); put(p, "fxbox_sel_fx1a", 0, log)
    put(p, "fxbox_asgn_fx1b_g", p["fx1_fx_type"], log); put(p, "fxbox_sel_fx1b", 0, log)
    put(p, "fxbox_asgn_fx2a_g", p["delay_type"], log); put(p, "fxbox_sel_fx2a", 0, log)
    put(p, "fxbox_asgn_fx2b_g", p["fx2_fx_type"], log); put(p, "fxbox_sel_fx2b", 0, log)
    put(p, "fxbox_asgn_fx3_g", p["reverb_type"], log); put(p, "fxbox_sel_fx3", 0, log)
    if p["od_ds_on_off"] and p["fx1_on_off"]:
        log.append("BOOSTER and MOD are both on; Gen 1 runs one at a time - kept BOOSTER, MOD turned off")
        p["fx1_on_off"] = 0
    put(p, "fx_active_ab_fx1", 0 if p["od_ds_on_off"] else 1, log)
    if p["delay_on_off"] and p["fx2_on_off"]:
        log.append("DELAY and FX2 are both on; Gen 1 runs one at a time - kept DELAY, FX2 turned off")
        p["fx2_on_off"] = 0
    put(p, "fx_active_ab_fx2", 0 if p["delay_on_off"] else 1, log)

    P["id"] = str(random.randint(10**9, 10**10 - 1))
    return P


def convert_file(src_path):
    folder, fname = os.path.split(src_path)
    base = os.path.splitext(fname)[0]
    if base.endswith("(Gen1)"):
        print(f"- {fname}: already converted, skipping")
        return False
    try:
        src = json.load(open(src_path, encoding="utf-8"))
    except Exception as e:
        print(f"- {fname}: could not read as a .tsl file ({e})")
        return False
    device = str(src.get("device", ""))
    if "patchList" in src:
        print(f"- {fname}: already a Gen 1 style file (device {device!r}), skipping")
        return False
    if "data" not in src or "KATANA" not in device.upper():
        print(f"- {fname}: not a Katana MkII/Gen 3 patch (device {device!r}), skipping")
        return False

    tpl = load_template()
    out = copy.deepcopy(tpl)
    out["liveSetData"]["name"] = src.get("name", base)
    out["patchList"] = []
    k = 0
    for liveset in src["data"]:
        for patch in liveset:
            k += 1
            log = []
            P = convert_patch(patch.get("paramSet", {}), tpl["patchList"][0], log)
            P["orderNumber"] = k
            P["liveSetId"] = out["liveSetData"]["id"]
            out["patchList"].append(P)
            print(f"- {fname}: patch {k} '{P['name'].strip()}'")
            for line in sorted(set(log)):
                print("      *", line)
    out_path = os.path.join(folder, base + " (Gen1).tsl")
    json.dump(out, open(out_path, "w", encoding="utf-8"), separators=(",", ":"))
    print(f"  saved: {out_path}")
    return True


def pick_files():
    try:
        import tkinter
        from tkinter import filedialog
        root = tkinter.Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        files = filedialog.askopenfilenames(
            title="Select Katana MkII / Gen 3 .tsl file(s) to convert to Gen 1",
            filetypes=[("Katana patch files", "*.tsl"), ("All files", "*.*")])
        root.destroy()
        return list(files)
    except Exception:
        print("Drag your .tsl file(s) into this window and press Enter")
        print("(or just press Enter to convert every .tsl in this script's folder):")
        line = input("> ").strip()
        if not line:
            here = os.path.dirname(os.path.abspath(__file__))
            return [os.path.join(here, f) for f in os.listdir(here) if f.lower().endswith(".tsl")]
        import shlex
        return shlex.split(line, posix=False) if os.name == "nt" else shlex.split(line)


def main():
    files = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not files:
        files = pick_files()
    files = [f.strip('"') for f in files]
    if not files:
        print("No files selected.")
        return
    done = sum(convert_file(f) for f in files)
    print(f"\nConverted {done} of {len(files)} file(s).")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("Error:", e)
    # keep the window open when launched by double-click / drag-and-drop
    if os.name == "nt" and not os.environ.get("PROMPT"):
        input("\nPress Enter to close...")
