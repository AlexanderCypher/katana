"""Regression tests for katana_to_gen1.py (standard library only).

    python -m unittest discover -s tests -v

Real MkII patches are read from the folder in KATANA_SAMPLES (default: tests/samples).
CI fills it from github.com/syndicalt/katana-rs (assets/patches); without it those tests are skipped.
Real Gen 1 patches (confirmed working on a Gen 1 amp) are read from KATANA_GEN1_SAMPLES; they are not
kept in the repo because they are other people's patches.
"""
import contextlib, copy, glob, io, json, os, sys, tempfile, unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import katana_to_gen1 as k  # noqa: E402

SAMPLES = os.environ.get("KATANA_SAMPLES", os.path.join(HERE, "samples"))
GEN1_SAMPLES = os.environ.get("KATANA_GEN1_SAMPLES", os.path.join(HERE, "gen1_samples"))
TEMPLATE_KEYS = set(k.load_template()["patchList"][0]["params"])


def read(path, encoding="utf-8"):
    with open(path, encoding=encoding) as fh:
        return fh.read()


def gen1_files():
    return sorted(glob.glob(os.path.join(GEN1_SAMPLES, "*.tsl")))


def load(path):
    return json.loads(read(path, "utf-8-sig"))


def fake_mk2(name="TEST PATCH", amp=29, booster=21, chain_pattern=4):
    """A minimal MkII file: every required block present, mostly zeros. Laid out like real
    files: each patch is {"memo": {"memo": "", "isToneCentralPatch": ...}, "paramSet": {...}}."""
    blocks = {b: ["00"] * 0x80 for b in k.REQUIRED_BLOCKS}
    blocks["UserPatch%PatchName"] = [f"{ord(ch):02X}" for ch in name.ljust(16)]
    blocks["UserPatch%Patch_0"][0x00] = "01"                  # booster on
    blocks["UserPatch%Patch_0"][0x01] = f"{booster:02X}"
    blocks["UserPatch%Patch_0"][0x11] = f"{amp:02X}"          # 0:0x21 amp type
    patch2 = ["00"] * 0x30
    patch2[0x00] = f"{chain_pattern:02X}"                     # 6:0x20 chain pattern
    blocks["UserPatch%Patch_2"] = patch2
    return {"device": "KATANA MkII", "formatRev": "0001", "name": "fake",
            "data": [[{"memo": {"memo": "", "isToneCentralPatch": False}, "paramSet": blocks}]]}


def check_patch(tc, P, where):
    p = P["params"]
    tc.assertEqual(set(p), TEMPLATE_KEYS, f"{where}: key set differs from a real Gen 1 patch")
    tc.assertLessEqual(len(P["name"]), 16, where)              # BOSS exports do not always pad
    name = "".join(chr(p[f"patch_name{i}"]) for i in range(1, 17)).rstrip()
    tc.assertEqual(name, p["patchname"], where)
    for key in p:                                            # 2-byte values must agree with their halves
        if key + "_h" in p and key + "_l" in p:
            tc.assertEqual(p[key], p[key + "_h"] * 128 + p[key + "_l"], f"{where}: {key}")
    chain = [p[f"fx_chain_position{i}"] for i in range(1, 21)]
    tc.assertEqual(sorted(chain), list(range(20)), f"{where}: chain is not a full block order")
    tc.assertEqual(p["chainParams"]["positionList"], chain, where)
    tc.assertIn(p["chain_ptn"], (0, 1, 2), where)
    tc.assertLessEqual(p["preamp_a_gain"], 120, where)
    tc.assertLessEqual(p["od_ds_drive"], 120, where)
    for n in (1, 2):
        if p[f"fx{n}_on_off"]:
            tc.assertIn(p[f"fx{n}_fx_type"], k.GEN1_FX_TYPES, where)


class Synthetic(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = self.tmp.name

    def tearDown(self):
        self.tmp.cleanup()

    def write(self, name, data):
        path = os.path.join(self.dir, name)
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(data, fh)
        return path

    def test_converts_and_maps_mk2_only_values(self):
        r = k.convert_file(self.write("a.tsl", fake_mk2()))
        self.assertEqual(r.status, "ok", r.message)
        P = load(r.out_path)["patchList"][0]
        check_patch(self, P, "fake")
        self.assertEqual(P["params"]["preamp_a_type"], 8)      # Var CLEAN -> CLEAN
        self.assertEqual(P["params"]["od_ds_type"], 18)        # HM-2 -> Metal Zone
        self.assertEqual(P["patchNo"], "A: CH1")

    def test_pedal_assignments_are_copied(self):
        data = fake_mk2()
        blocks = data["data"][0][0]["paramSet"]
        blocks["UserPatch%Patch_2"][0x1E] = "05"              # 6:0x3E EXP pedal -> Delay 1 (assign)
        blocks["UserPatch%Patch_2"][0x20] = "09"              # 6:0x40 GA-FC EXP2 -> Pedal FX (MkII-only)
        asgn = ["00"] * 34
        asgn[1] = "01"                                        # Delay: Delay Time
        blocks["UserPatch%ExpPedalAsgn"] = asgn
        mm = ["00"] * 78
        mm[2:6] = ["00", "0A", "03", "10"]                    # Delay min 10, max 3*128+16 = 400
        mm[0x0A:0x0C] = ["05", "50"]                          # Chorus min 5, max 80
        blocks["UserPatch%ExpPedalAsgnMinMax"] = mm
        blocks["UserPatch%KnobAsgn"] = ["00", "03"] + ["00"] * 32   # Delay knob: High Cut
        r = k.convert_file(self.write("e.tsl", data))
        P = load(r.out_path)["patchList"][0]
        check_patch(self, P, "pedal")
        p = P["params"]
        self.assertEqual(p["pedal_function_exp_pedal"], 5)
        self.assertEqual(p["pedal_function_gafc_exp2"], 2)
        self.assertEqual(p["exp_pedal_assign_delay"], 1)
        self.assertEqual((p["exp_pedal_assign_delay_min"], p["exp_pedal_assign_delay_max"]), (10, 400))
        self.assertEqual((p["exp_pedal_assign_chorus_min"], p["exp_pedal_assign_chorus_max"]), (5, 80))
        self.assertEqual(p["exp_pedal_assign_booster_max"], 100)  # 0/0 in the file keeps the Gen 1 default
        self.assertEqual(p["knob_assign_delay"], 3)
        self.assertTrue(any("GA-FC EXP 2" in n for _, notes in r.patches for n in notes))

    def test_hidden_amp_and_unlisted_reverb_get_a_note(self):
        data = fake_mk2(amp=19)
        blocks = data["data"][0][0]["paramSet"]
        blocks["UserPatch%Patch_1"][0:2] = ["01", "02"]       # 5:0x40 reverb on, type Hall 1
        r = k.convert_file(self.write("h.tsl", data))
        notes = " ".join(n for _, ns in r.patches for n in ns)
        self.assertIn("hidden amp voice", notes)
        self.assertIn("Reverb type Hall 1", notes)
        self.assertEqual(load(r.out_path)["patchList"][0]["params"]["preamp_a_type"], 19)

    def test_every_chain_pattern_gives_full_order(self):
        for pat in range(8):                                    # 7 is unknown on purpose
            r = k.convert_file(self.write(f"c{pat}.tsl", fake_mk2(chain_pattern=pat)))
            P = load(r.out_path)["patchList"][0]
            check_patch(self, P, f"pattern {pat}")

    def test_never_overwrites(self):
        src = self.write("b.tsl", fake_mk2())
        before = read(src)
        first = k.convert_file(src).out_path
        second = k.convert_file(src).out_path
        self.assertNotEqual(first, second)
        self.assertTrue(second.endswith("(Gen1) 2.tsl"))
        self.assertEqual(read(src), before)

    def test_refuses_other_files(self):
        gen3 = self.write("g3.tsl", {"device": "KATANA Gen3", "data": []})
        self.assertEqual(k.convert_file(gen3).status, "error")
        junk = self.write("junk.tsl", [1, 2, 3])
        self.assertEqual(k.convert_file(junk).status, "error")
        done = self.write("x (Gen1).tsl", fake_mk2())
        self.assertEqual(k.convert_file(done).status, "skipped")

    def test_missing_blocks_are_skipped_not_guessed(self):
        data = fake_mk2()
        del data["data"][0][0]["paramSet"]["UserPatch%Fx(2)"]
        r = k.convert_file(self.write("m.tsl", data))
        self.assertEqual(r.status, "error")
        name, notes = r.patches[0]
        self.assertEqual(name, "TEST PATCH")                   # not the memo object
        self.assertIn("Fx(2)", notes[0])


@unittest.skipUnless(glob.glob(os.path.join(SAMPLES, "*.tsl")), f"no sample patches in {SAMPLES}")
class RealPatches(unittest.TestCase):
    def test_all_samples(self):
        with tempfile.TemporaryDirectory() as out:
            converted = 0
            for f in sorted(glob.glob(os.path.join(SAMPLES, "*.tsl"))):
                device = load(f).get("device", "")
                r = k.convert_file(f, out)
                with self.subTest(file=os.path.basename(f)):
                    if "Gen3" in device:
                        self.assertEqual(r.status, "error")
                        continue
                    self.assertEqual(r.status, "ok", r.message)
                    for P in load(r.out_path)["patchList"]:
                        check_patch(self, P, os.path.basename(f))
                        converted += 1
            self.assertGreater(converted, 0)


@unittest.skipUnless(gen1_files(), f"no Gen 1 patches in {GEN1_SAMPLES}")
class RealGen1Patches(unittest.TestCase):
    """The checks applied to converted patches must also hold for real, working Gen 1 patches."""

    def test_real_patches_follow_the_same_rules(self):
        full = 0
        for f in gen1_files():
            for P in load(f)["patchList"]:
                p = P["params"]
                where = f"{os.path.basename(f)}: {P['name'].strip()}"
                with self.subTest(patch=where):
                    chain = [p[f"fx_chain_position{i}"] for i in range(1, 21)]
                    self.assertEqual(sorted(chain), list(range(20)))
                    self.assertEqual(k.gen1_chain_ptn(chain), p["chain_ptn"])
                    for key in p:
                        if key + "_h" in p and key + "_l" in p:
                            self.assertEqual(p[key], p[key + "_h"] * 128 + p[key + "_l"], key)
                    if len(p) == len(TEMPLATE_KEYS):                # newer BTS export (older ones have 1057)
                        full += 1
                        check_patch(self, P, where)
                        tpl = k.load_template()["patchList"][0]["params"]
                        self.assertEqual({x: type(v) for x, v in p.items()},
                                         {x: type(v) for x, v in tpl.items()})
                    else:
                        self.assertLessEqual(set(p), TEMPLATE_KEYS)

    def test_gen1_files_are_left_alone(self):
        with tempfile.TemporaryDirectory() as out:
            for f in gen1_files():
                r = k.convert_file(f, out)
                self.assertEqual(r.status, "skipped", f)
                self.assertIsNone(r.out_path)

    def test_live_set_from_real_patches(self):
        entries = []
        for f in gen1_files():
            new, problems = k.load_patches(f)
            self.assertEqual(problems, [], f)
            entries += new
        with tempfile.TemporaryDirectory() as out:
            tsl, _ = k.save_live_set(out, "Real set", entries)
            data = load(tsl)
        self.assertEqual(len(data["patchList"]), len(entries))
        for P, e in zip(data["patchList"], entries):
            self.assertEqual(P["params"], e.patch["params"])        # settings untouched


class LiveSet(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = self.tmp.name

    def tearDown(self):
        self.tmp.cleanup()

    def write(self, name, data):
        path = os.path.join(self.dir, name)
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(data, fh)
        return path

    def gen1_file(self, names):
        """a converted Gen 1 file holding one patch per name"""
        data = fake_mk2()
        data["data"] = [[copy.deepcopy(data["data"][0][0]) for _ in names]]
        for P, n in zip(data["data"][0], names):
            P["paramSet"]["UserPatch%PatchName"] = [f"{ord(ch):02X}" for ch in n.ljust(16)]
        return k.convert_file(self.write("src.tsl", data)).out_path

    def test_order_channels_and_ids(self):
        entries, problems = k.load_patches(self.gen1_file([f"SONG {i}" for i in range(1, 11)]))
        self.assertEqual((len(entries), problems), (10, []))
        entries.reverse()
        entries[0].song_note = "capo 2"
        tsl, txt = k.save_live_set(self.dir, "Friday: pub/gig", entries)
        self.assertEqual(os.path.basename(tsl), "Friday_ pub_gig (Live Set).tsl")
        data = load(tsl)
        self.assertEqual(data["device"], "GT")
        self.assertEqual(data["liveSetData"]["name"], "Friday: pub/gig")
        pl = data["patchList"]
        self.assertEqual([P["name"].strip() for P in pl], [f"SONG {i}" for i in range(10, 0, -1)])
        self.assertEqual([P["orderNumber"] for P in pl], list(range(1, 11)))
        self.assertEqual([P["patchNo"] for P in pl], k.SLOTS + [None, None])
        self.assertEqual(len({P["id"] for P in pl}), 10)
        self.assertTrue(all(P["liveSetId"] == data["liveSetData"]["id"] for P in pl))
        self.assertEqual(pl[0]["note"], "capo 2")
        for P in pl:
            check_patch(self, P, P["name"])
        text = read(txt)
        self.assertIn(" 1. A: CH1  SONG 10", text)
        self.assertIn("capo 2", text)
        self.assertIn("Songs 9+", text)
        tsl2, _ = k.save_live_set(self.dir, "Friday: pub/gig", entries)     # never overwrites
        self.assertNotEqual(tsl, tsl2)

    def test_without_channels(self):
        entries, _ = k.load_patches(self.gen1_file(["A", "B"]))
        pl = k.build_live_set("x", entries, use_channels=False)["patchList"]
        self.assertEqual([P["patchNo"] for P in pl], [None, None])

    def test_mk2_files_are_converted_and_others_refused(self):
        entries, problems = k.load_patches(self.write("mk2.tsl", fake_mk2()))
        self.assertEqual(len(entries), 1)
        self.assertIn("converted from MkII", entries[0].notes)
        _, problems = k.load_patches(self.write("g3.tsl", {"device": "KATANA Gen3", "data": []}))
        self.assertIn("Gen 3", problems[0])
        _, problems = k.load_patches(self.write("junk.tsl", [1]))
        self.assertTrue(problems)

    def test_rename(self):
        entries, _ = k.load_patches(self.gen1_file(["OLD"]))
        k.rename_patch(entries[0].patch, "Thunderstruck Intro!")      # cut to 16
        P = k.build_live_set("x", entries)["patchList"][0]
        check_patch(self, P, "renamed")
        self.assertEqual(P["params"]["patchname"], "Thunderstruck In")

    def test_level_warnings(self):
        entries, _ = k.load_patches(self.gen1_file(["A", "B", "C"]))
        self.assertEqual(k.level_warnings(entries), [])
        entries[1].patch["params"]["patch_level"] += 30
        warn = k.level_warnings(entries)
        self.assertEqual(len(warn), 1)
        self.assertIn("2. B: patch level", warn[0])
        self.assertIn("louder", warn[0])

    def test_command_line(self):
        src = self.gen1_file(["ONE", "TWO"])
        old = sys.argv
        try:
            sys.argv = ["katana_to_gen1.py", "--live-set", "Cli set", src]
            with contextlib.redirect_stdout(io.StringIO()) as out:
                k.main()
        finally:
            sys.argv = old
        self.assertTrue(os.path.exists(os.path.join(self.dir, "Cli set (Live Set).tsl")))
        self.assertIn(" 2. A: CH2  TWO", out.getvalue())


if __name__ == "__main__":
    unittest.main()
