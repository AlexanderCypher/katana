"""Regression tests for katana_to_gen1.py (standard library only).

    python -m unittest discover -s tests -v

Real MkII patches are read from the folder in KATANA_SAMPLES (default: tests/samples).
CI fills it from github.com/syndicalt/katana-rs (assets/patches); without it those tests are skipped.
"""
import glob, json, os, sys, tempfile, unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import katana_to_gen1 as k  # noqa: E402

SAMPLES = os.environ.get("KATANA_SAMPLES", os.path.join(HERE, "samples"))
TEMPLATE_KEYS = set(k.load_template()["patchList"][0]["params"])


def read(path, encoding="utf-8"):
    with open(path, encoding=encoding) as fh:
        return fh.read()


def load(path):
    return json.loads(read(path, "utf-8-sig"))


def fake_mk2(name="TEST PATCH", amp=29, booster=21, chain_pattern=4):
    """A minimal MkII file: every required block present, mostly zeros."""
    blocks = {b: ["00"] * 0x80 for b in k.REQUIRED_BLOCKS}
    blocks["UserPatch%PatchName"] = [f"{ord(ch):02X}" for ch in name.ljust(16)]
    blocks["UserPatch%Patch_0"][0x00] = "01"                  # booster on
    blocks["UserPatch%Patch_0"][0x01] = f"{booster:02X}"
    blocks["UserPatch%Patch_0"][0x11] = f"{amp:02X}"          # 0:0x21 amp type
    patch2 = ["00"] * 0x30
    patch2[0x00] = f"{chain_pattern:02X}"                     # 6:0x20 chain pattern
    blocks["UserPatch%Patch_2"] = patch2
    return {"device": "KATANA MkII", "formatRev": "0001", "name": "fake",
            "data": [[{"memo": "", "paramSet": blocks}]]}


def check_patch(tc, P, where):
    p = P["params"]
    tc.assertEqual(set(p), TEMPLATE_KEYS, f"{where}: key set differs from a real Gen 1 patch")
    tc.assertEqual(len(P["name"]), 16, where)
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
        self.assertIn("Fx(2)", r.patches[0][1][0])


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


if __name__ == "__main__":
    unittest.main()
