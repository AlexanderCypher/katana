# Katana patch converter

Single-file Python tool (katana_to_gen1.py) that converts BOSS Katana MkII / Gen 3 .tsl patches to Gen 1.
- Keep it one file with no third-party dependencies (tkinter window + text fallback).
- Windows .exe is built by .github/workflows/build-exe.yml.
- For format details, parameter numbers and open questions, use the katana-gen1-patches skill (.claude/skills/katana-gen1-patches/SKILL.md).
- Test by converting real .tsl files and checking the output has the same 1505 keys as a real Gen 1 patch; never claim a tone "sounds right" (no audio access).
