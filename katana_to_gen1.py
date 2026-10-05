#!/usr/bin/env python3
"""
katana_to_gen1.py  (v5)  -  convert BOSS Katana MkII .tsl patches to Katana Gen 1 (MkI) .tsl

EASIEST WAY TO USE (this one file is all you need):
  Double-click it. A window opens: click "Choose patch files", click "Convert", done.
  (You can also drag .tsl files onto this file, or run:  python katana_to_gen1.py "Patch.tsl")

The new files are saved next to the originals as "<name> (Gen1).tsl" - import them in BOSS TONE STUDIO.

Option (command line only):  --strict-panel   keep only one effect of each pair that shares a button
                             on the Gen 1 amp (Booster/Mod and Delay/FX).

How it works: a MkII .tsl stores each patch as hex byte blocks that are slices of the amp's
memory map. The script rebuilds that memory image, then copies every parameter it understands
into a real Gen 1 patch (named parameters), translating values that differ between generations
(amp voices, booster / effect types, colour slots, EQ, chain order, patch level ...).
"""
import base64, copy, json, os, random, sys, zlib

TEMPLATE_B64 = "eNqNPduO6zaSvxL4uRFYsux291swMwgGO3sQbLJPi4Eg22pbc2zLkeS+JMi/LyXe6ko5QM45FquKxWKxWCwWyT8Xh/q92deL18XPvy2eFu911zft1fzMflz+uDRfbtWwP/2r6YfF6//9uWgOpqjYvOSr52KbZ6b82g4G+3o/n0fYrrr0i9c/F2+fednfd2V7KA99OXzdDEyWPS327eVWXqtLnS0Xr8snAnfomncDuDYFh/pcfeXl+3AsL6aw/xDAd+0wtBcL//aZTSUTXnlqjqdyfzc8Z4XDaoaqM39eyt39jz8WrwWjNrTXWqJVv73V+6E81+/12ZdDerg8WzKAru7bxesqt4THasYmNW9fOs1D0400L82na3ZWflSnl3Vd3upDdS5vbR+qysrjPSBaSTt67X6o3uuyq67HWqZzaa6hAFA5tx+RK0fF8brJJTLVJ2j526djI88QBdiowLujIwoxU3vt1hilLPtT8zbUXfneThqMKQoinO0zTPbWZ6afRsW16If9aln29dlgtp1AlNUoEJw+GMkUgGRzvd0H04jz/QIUUOg8gd5bMyrtZgnI7U9td+8N1aG+Gua+gH4FXe/bcwvHFOezMxI8Gw0Vht2ETFRXJXCaCExG5G/VUB/b7utbdQkWA1OWhxqj7cqfTfn+3nX1dfhlpP+tDZ1yqN+6ehjBq2Go9t8tsEQsD11sOH7/m0QuL4dRqcoAuT9VzfWXYOvMYGwGYzTXpl+fwq9sY8Z8/Gl+ZeBn9jyqXfw9/oTIW/P7Jf42PwtQ+mLtmv/9Yvl3v3JjWbMNgDa/n8HPzOgL+GmAYWm+eN0CWtZqh9LV4hVwZX5la1BamN8A2fyEpWurCe6nm1FM3aYCQ2X9lD8ZARkhFE/Z0/PT5mn79PJkyC2fzNflk5GGaXK2+fdftIeteV2znn9wjOdc1TkIGbWhjgeGfG6HaBGskxnU/dd1OE3/1NGAkoehXZuxbdp7q6vBGIahHnkeu5oQNhNf+/amWcvRapS7aVDMieQUBlRuwJxhmebWCWKcHicllyD8fLG2dZyq7tJeTad7a50xNCdMh7gVmRPnkDhXg+nPiUyb1YfmAsQH+Tt12fjDDkg6Y/MKWJ+cnEgITapmmC5UYgXxJEw5vTHxMpqg1ogqUS8wi9W34QTGU2gjm1BcYXsfbqOnxUQs9BXhEXU16p3qNvWQIhKiv2K7T9ENupbTcGDQIoMjE6O1V8wH4mPvbUJEEywCQjnsyOw/ydZP/kGlJaeLNNQq6TOCnxV5VoP6dS+KIsV24sZotLDrRHsvgYUsLev1PoEJPSGCeMTd5NYaMx1V7VJsMiWzLsKtPVddaLX9po/RbKe0tIrfLQ0z3/xuzMpaorGjwMYUfZeB8wMDnhFDfpBZzPdROmDmcUsdiRBUPIDx1pxHmVohFSJiCu9Q76svxQK+RdYTiyeJJrCAlCbUQYBq/3TDNZdEfxTx5sQPtTDaaDipUYTY6Mq4AYIpE9GgFqkrRDJ7yhNdrlKq5DnbG/N8iZC0ZbWzs5Q7U9Ler4fy1J4PZdf0NZk/CB5asAJMZbEfAcY/gkD0ycxIf2+cpHZf933b+QAIaqCwQE1NcojeruqBTakO7+UUWEGrf4RwaQ6Hcy2g9Pd+qEYprnU0Z368qxRw/dpKRB26eifWiJUX4RizagzBXsIiPYLQSNm5uTTjOEbSuJ2qHn/LHln1OrTRsYtrSCkQAKo9mVacohV0JJxVKbS6kUMWsC7V9V6NbVvLaDmaZj23kxVWKsrJFOtw+qG+uWZqiHAhE/CUwM0jqywnFz4MZtcjefl2HuMivmNWGegYOZySXl9Fgqib8nREJZtdWXmqvhu3OZx7ZWMTmoaWBMGYow73sH09hl6HKXJLEbDv4DHO7YcNkFJw6z1QZjCrG4pku4EiCZNbwHBy9pSMtbiMYSU7NZ6qGxhuEYfT83iWge1asMtc8zyS52GNpwhkNzws6qRMie7mZdea719lf6vrgzMRobNmlvBmRIwhpXromn1Z/z71kLG/5XEyz352dBVMqP0Up12xyUNcBUDEt2oMvkjSgksajxEn04nUrv0sq/54Ld8+V2U3xXgYFehnOjJv1fmskolhBHl9EaggtRlJGBkbCqMnLc2hNeeDdKS2zrlfm/Id2f1Y2+hkiTM2RVe4XWkTfk8JYLNqZr2hMeOj2o1NlomAtc6tumJd9jOUn7eXEW7yiUWZVJggHKCcqZzVNVklG0X0JKxQC9qFFcc148fMETZS6rGdTINee2AnqhUARV0Num8Xajp21e1kh9sqO/1hh5lxQYwLWQ/3bpJLg8wqwNjkHmOyHmezfO6IJQTQWb4WwM1gPx7D+meNC2/VGGQU687XS0/N/IpcZgxyvVwK9c7OuqINeW92pn3B2mKS0myWKXG/PB1XUoNxkQUnuBBHTMba8tlQnSfrp/91gmr0QjwWmcETcR09BmcMVHO1m512iqcyJ2Y4U6NBgJKd+8NGCptfyNzi0RSnbibOFtBF3ZEnt99jiOhunKTmj9FZgptuiWVPxHhvP+pzhjsbLzNw7VOAeqzeyidfiQTzaT+HLx5h/AAi4TGs1IglHpHxkBKQNURqDwVUtBEO5OzXFnIPuVgGq5BtqLCOhX6lEjzPYeD/s303dG1fFIKqgWlZj5kDeiMPbpJZcTS0uU2w/PDfSBMh8CUIGt0NyVO7/ATXGwHJ4uzkKqdOdSsfyW1KYPkGbgUx73U0vt2jhhUT+0B2+BiXoX4/vayFAJMWeZzZJMq0SGOubQ3NR3wm61gbH1+JJUm7SJka9MnUyKQaU5PtpYvESJ2A3Ec9vAY1c+wgedbNjxItak2y2WhRpoUz89kMGy2rBfpU35Fro+88uWwishME/SmFEt+IAmxB8SFqRaBmqdB6QaYNaXOksSU0VBlsCKC8vxkV2oXa14wSsPiMktdLuGrblcfAkLgHQBQwD/2A2pLaDGBqt1TVDqSNKQoVt+3xTJ3cAUhsZWpJJpkeCJWVKktFQR0DWezRpaBGcE5TPA/ramFyJ9n0wq0vEjcN+LBbiUlFMXIWQQ0UTg3s1FzcTebB04BOelfJf3DgORoQ+GO0uXGQgEBXAMYthv0ffc0ADBsXPuoss/0jizN603G5LM+fFTJy1gF3+iuFw7xP4eZTYJoIeWER4HBQCFJNhnHAKvtCNA9o9K49uAWhn/jjmHRfgFOynZbBQUmBe+V9UeiSIH9Y34xzKMpiSNuBEP0UISs02qDOwHQ72BPui21PEX9PNiN/4Ya4m5Z+DizIxVoLDm0FxqBPIDJnfo8u+edqtPF5AA4SzSJXUaSR6MGv6OMnLMYxHO1hpZSeU129f41ZDWXWpoIKccfTUetv0zLUSZcSywExZsXjeiJoKpm4k8llAcn+YzdGkdxey2pDGWGNFrFDWGfN/Vbil0r4DzLJBiJWgM6mNXpEFCFHX0EUapmYWsOGPUZGiwGpqGKiUtJ0ULlgZYDFsjZl/N62fs/I/7W/d2N+Xj6ZlmOMEBYidFjGCEVxsxkUUssgJQYemvfmECIi4MMYqHObC/hrVR6+rtWl2asFwPCgYts/HM1Ops6pf0GFO62ynVAZtn5gxoRogIkp6KBaAYRFWcSoZMwbTYAStT+nlu7M/H6urntYYMxJXVlnBoaFvV3I8OdAFX6c/g1Yh2XuL6W0Ovzn3tsuri63ct9eh661rbj2GTRO40+77zy5Xmv7JcTP1w7kUA9eZ649WQ7hQf81Kf4IRMnmlGwOyVb7/RRj9ycAwJcemcSClxCLRovBBtIalJ4nB3FXVxcQe5dKgQMhIiu1AxDMAdYyZtADARKMfRbLtNojstx6QMD8A9oUDoJzCsEhG75i5MiwfYjD4WOch8WabZHWNFuqtOuj6m7E9ayaa3kb7B4HhtNqmApxBc6Uu60bqIRvdX0Y/XtoHKRCoEZuorlf9+O0V9afNztXYb0HuP5MR+R3G3nyG0QKU3b1AXtPggKkn5dJJjC9lQL83uzA3roG4WSydQc9yr076eHOPEzfYGdeqn5yougmRPwOYl0b+t0uZPG3SMNJ02+QFRCSBNKt3o9HzJwXMa02rfW3OLvbxbnF7sP3+ouWj40CzBtLMbjDG9OGmjWOcQuxdJqMz1+w77nfMyXf3ZkL9r1wNol8Xrs9DPJ542OI5Ls/hoIV+1i97UftzuQmuMMpMk4uM/Di1o9UGku3h0W/20Mr/Ls9rvL92u7M+qZvzApn17Z99CEo/Mo5CPS7O7rCC9YKoY0LGtDvz37JRQvciR5e8OLXolQDll75x22aySiZIXv9Xh7aj6vFYUX3m1UPWHC9X3bjZvLYP5nlTit2SqcVr3w4ESwns2pcIaaIFl7DMVbH67qdOjP+jE1ob26QxTJrevZDd7ZHsIbzZG/9Z6t5SpH3zYWSyTWXSvpuH+cBXzz+33/4ql5Yga/I2SC/9V5wQFKv+xwrBWVjMNr8O3PVboQS2sBYQOoJBamaclfTi1Ci1JSHmvxk9p22PECKVY//21qJsMDkwSpn5ZVzTmCdkbJQkKIuwvgarLFBPrj/ZJY4x3oYp4UN+3iSIE3FLlNBKJAxqs/SjgOhAGP07b3bO+cKfYp94L9X+8EeNzUjENGIBadmnCCeY1FzNbPm4RzTMbZC2eSOrJa8xC2xQcmHPfM6Ohw5+fzWTnkg/mPOZZ9Lss8l2edc9t5vCIorQMokSGfkWmfksDOCs+jnLRs3FMBjRzEcl2iJkFgvMiwbU1eQQg8ztCkjDWFJnc/QXAKljBg0g6G5tBcRLaoNQ7NJfgiLqBRHcUschhQUjqGEfQKAs4L6KGCMOVIIHOkqV4f2cpPATzJ9lwUnYQAVZ30zhsg0HKUmn40rooWhwJVu+uHxoucNLnfwxFKj5DYuCRgstWUrbQiuHhge1R7sQyi4+iiB2wII+aHBEoOAMm4cL9ZaFcRaraQxYkG3DJQODDdzb0TAMBigr+12XwKnBRwDENAG5xEkUn8IywxhgXUfwnIDWHC1hwjM9hVc5SE8NXoFV3UIzo1dwVURInAzV0D9RzKkpq1g2o/AuVkruPZDDMmqFZLSYyRi2ApR01EHY9NWCOoNwblpKwQtR71A7FNBVR0CC/as0DUemzH7ca1p/REZq7Wu8jcZkKuLaJjWaZXX7Nmaaz5do33ZZSaFF1VfNF3rtPbbUBSCh8bfGiS/KV5QoKj3cVcLpmt76KTSo6xnBU239rSH51Q/bFzKWKL+h8xLEUceAcostJ51hlwOAZk21zP+kNt7pQuZjZhdEDYPPVDaEdI6aDPjEWFR20XcdPGUzbXk8EjMET63uYsMvn4/wdkkIqxMrxeMyyibCFlY0gLkiUCuDdNbDhkGYoTcyDRDh0bIZ3tqyUOCgRdhthIMGHcB8AUDsiEH5L/UQMMwA8AZBpbGF4DOFegwrgDsSoaN4wnAFhiWDCIAuOaAYdQAsA0Ee4ajxKY/hc3d5wiERsl0JJatf5/xkMBHgglI1Ed+DFgABRThqV8KGRSSnPQV4ABFuKfhAIE22usahMZSbUR3zQE4pozssjkOGXQR3zS3AcCSLtKb5Bhs0ER+DxeFjZooX7vl4Yk2SjdpFQQ86KR4FYaF3CK1nOD2RknaC1WpLVZNBApv6CPQJ4HwGPcVQKOuIvCQ9CiAC9Rjti6FD1qL4PdmBjEKMfasguQsalePu/MVTArwwNCoejArvi0FKuFFZBbS7lRtQOXcrgaqzq3OROhoWj18PErjoUXb6sFhji1DiOY1cANyXik4sLAeHGe8egRqZj00GwNbYmhDG01LTtDVGmVknAJ3RDzmpiCJT+MxnD7Ced4BEF+g5wFj0iIGJOlrFjiob4S94VMKDi4ig+7Y4+MFdnGYxwwWBn5oegYdjiljuY3g9kAoBgeHjhl5mh6JcOx5Y4QjHEAMKE1fg8Q2j0GtD0QZN/l1FHpPqMeCW/kEpT4ca44gdYVDcL9BIjaoB7dVQcWnCVTNA9aJQgvq56CNZvXGtw0HBDUNjOB7o7edhchQJQkZBDTLdoZOnmu6GXGv90s4cTejoaDCatdc63jeLK2rO5rRmVbTHT6pkFTQnTPXawIsquYO2WsIznVyR4496sq4Y9e8pDVwh+z0rbuU0wGhuqumw6t0QtoBOy3BC61EPBJwn0NCGxuNNq8hOFZI6N5iM3h+DiTgQQPO8Hh2LkJLtSqcfYgot2iqPfh44HE6iHWohztrE7LuDEUQArTvDP5+u5FTmwjPG3qGZ8ZOCg8X0Gbx7PeALB09n9bRL0szYvddcxuw1kmGH2CMFoLIQ7H7LlqcZc91OPxarDkeNv4Q66M5sNGZmAAgaoJPYQLAuF19rK/2tCPFxfPAQ4Kkk8FDspSnhEclqswMD4qWzA0PSlWYHBSZ1r/DaSHuTZ1vbz6nAR4liQAgXZnlssFwHIkV8fOcBY29TmfrxpMe7Kw8petj0eKNMWizZr9aekjhADwKOfq0Vgbvz+sDXvPKHShhITKXigUS4OV4Iwtfju2CWztKwFE6tUQOIWhb5oCnkN0G9yfAsWTcLR1NHfTTGEgeVCiCO+cwzS+bTKRs1NMTXvggmny3gLx5HxrFGPSXqICeYtmSGk1dkO7a7NlKfdYUi67jbQuNPuQZ3VqAldSekWJE4sVa4CB6aivfX8ihtitSRDcexqT4lxRVXZxh74ldykhfWaBNP8qMAoLsbkYWI1NSLVIMH6fkXIlVODOrCRm6hCfCiGXhurwE3ZSMMcv0Rj09FUTn9oa4ZZdyiDsL0Prx5sdjkgKvwokosQo/cSTJS0ImDhy36X6i4SNjr/HO7/PTZxN13O111oXr/bQKVOLwxDnnHF7xp22rhTjmDHmR9Xg8MUFe6VJwuEyxHWFRkdgSPGujBpJXLAlcb8l5SKlh6c4syLzTNZmasqSrjqevMM/XkaktUKUP8P1aUReIxZ0ZXL6eVHfwmk7USODrPlO1PNYawM50tT25DVvJdkzYTEY+NoFeq60S1/UpHiDG/UBv29bdR41xTJkyHa/mljLbHuRYlPWc3vgJ8gG+BWE/MABE08uribdPCTaUXGOaTs1LtAVccSVZUriYm6tDb0pc1Ilt4TemaqmxekNgFfJ0NtProYZ0M6hWTx2v3MiayFlMN4SvvKJ+6SnO4tQi0qeOsXDLq+rDpvjm/rFwJyyjzGYURnu67gSbH+322HRSTMqvCJWcaCXkBlmlASmqxA7JF8zOsQ6I8NOop3DdmHgXbcoZT5ggFNyY9tnY3cpK/nbC5ISDwCpIENoplSL+EOdEH4W7m8V8csZbLh+ay6SLnRWKjNuch3YQRXAnrpbFrvMJ4j6Y6Iwd5PENRhqkHSPSD0x9cpwjl5KUvbOHbtFI5JalOAYRRWiV4nHd1MpSZzemPENm8f0cCRebBqv45V3aUwz6mQGdWZg/DWk/sgiWwh9c42LWNSuD2d5SamhCj2Fy9qRu7AkHmSCVrnzprvy6g+xySnHO3IafUbYAucBbXPULC4acZX2zEpx3nnQsNXnCHHGBfkhR51mfqt3OeTb5KAx6L3iKoq5VKOk8kgW2kRl/KTqRy2npkWBS/8WQBiPtU5ynxSO8UXyGXsJuEYrh7nEeN482mfOFg8PcsMRrehldKbqW6/nyntF4lZnq7mlSZAnZnia8vpfxGU0xI0jS7T05YAh4uByYK0YPuHtQlLPLSiXUwDudpXFP1dBL0xnTwP56/1B8AlC7Tv0B/1PhGCeEI7MKU2D1xHPBL8+VHUFeOcpen6njhMTDborMxFd0UjSF4FIuhY79dZ7oPssZwoq0Q9CYTkRfSpScRxI0rxatCvkrECnK8pZdPm0DOoLCQwdJf05jloaIEW34EIK0GzJH8jQjoOSGSJI4WQSKDyqk/dCZFQSJR4nvL2j7G0HaZGxgm0metNCJJbxEGv0lrMLnGmTHSTcViYhvrh7A0WuhxoLe4yper6x7e3TxTq91zaTHLPToo+I7agHdXA1Y635ZcpGmj8+5iPWcRZfDX+rbGakQmjLD8lik8OaaFuJK00Q881dAeKwjrP3l5SXikr3Xxp0AuOxHDwcdw4sBwuM2mg+dUiQak0UMgpfd5CanxrEei80fzqhIKZiWl5A/vK+s7/TlepoCFBC4TCxBXNE1EoudJuvEgySsAhgKUIkjtvUHSxQNTM2lLGuBGtP4/g+nDsMBCcqIe/H5E0YaL671tbfGNng+SKAdFtYpwgrX0UcX86VSa3mN2XiLv5ZslKaKOBXv85dzkPSIh8bpVqeIYgMKUY1R8BiAnu2TDKFoDIPEKnmZOhucockk6rMxGv2E0WabP6mnjhIJL8Q3oo/+iW9npfNQEMWcPRiSehUpmSQi0bXbJZp09FmFxBIiVegbqjGsuawKQhO6hwmaiTmQRRIiccGByuejyZlqwx1lfA1/ivIDO99aBO/3ZAxOZ5qbcMA1eAlApqozLFlwRxkmR6PNkpg5oUwWiTamNt3zB7MkQhQBMAqStJOVavLV8s7yR/LOxCfFktHBh+t5JNSocjPnu6c8HSWZTH6SLImtMAcfJlMClUrNSQeRLZJV2ogv/aGydJCTxHLU98lUPlN+eCrFS3/TLFXVI3FbFu6Ze6RKiejrypvK+9IfTlOr0Q2JlgE29wavtpegN0nLCJt9klCv6qFmJbuKHOhQFpoPNQr1kfCOpko70QoxS0x6+jOFKgctUAZJIi4vVv3A9kp6/S0GVPjDnzpxXWhaIpfwGKi2dn4odkCToaSnFfUK0vyzHC7xsTplkyjNPU/jEl4cVSkngtQ4fAsdD/1kUD6fn5XaC06cZMiTOVri43U6Kohli0/W8dHHcqvEJ510PJziLbxZp/qVCWuipE2pbzxOa+zxop5l8HDFl8ECXBbXiNKjYAEul+BiHCTArSJc8qXRgFBIhOPrNkAp2U33pBLytmioYSOyRN8UDeDP8XYfd38VauB2bhaME27AeUnh4Ndx4zsz4Di9ghnO4cTezDRvIMZA8FW/4LrhQv8UdJtfUgoujVlzAhv+aS3TzGWam7nPiEjGq9vyTxlFpm9Gjotl8cJlQQaA7jOFpO+U4TtuRLIFba/2lnc4GYz9zluPANCbiWS/K+dtXcvSfpY/Z/RzfFrCPSwh8ZfTBogPnDu29PNCyl6hD9XDZ6416eGtVS3XCDnB6QQy/4oMEpp8N2Bc0c0dY1FzAOk66sGzO9L9V7hfV8r4QAozGexEz+m7KPOL3NRWWjLEQpdgMy/Ao5whNvxVjye9TR2fANNq1OMW0XqnBk16SaOlpGsjShPadOnfOKksXhf/9dNvP337aSG9+6x2NxSHmlE+mz8xnzbwwNJVFWuWFKvCZDYnufTJqpmEl7lMiofDKrPpVw+e2JqA/npatN2h7r5Nr6PYZxVH/fjWGu345adv//jXwn35598Xr9f7+fy0OLfHXyaYSYfst2E/fVq8vlXnvjYwzXv9az3882DIbF9eVi/Zcr3ZGFpI8X4I/5mS+ELT4n9//cf/ZIu//h3o/L0aqsXrn4v7+NaKrdEwdfL/blg1zaUaL0yxf5fZy4+36zHW/rNZzfzw323b1T/8Onyd6x9+npYEP/w2+sdEIuu//vp/zI2/Aw=="

STRICT_PANEL = "--strict-panel" in sys.argv

# --------------------------------------------------------------------------------------
# MkII memory model.  address = (page << 7) | offset
# --------------------------------------------------------------------------------------
BLOCKS = {                                   # TSL block -> (page, offset) where it starts
    "UserPatch%PatchName": (0, 0x00), "UserPatch%Patch_0": (0, 0x10), "UserPatch%Eq(2)": (0, 0x60),
    "UserPatch%Fx(1)": (1, 0x00), "UserPatch%Fx(2)": (3, 0x00),
    "UserPatch%Delay(1)": (5, 0x00), "UserPatch%Delay(2)": (5, 0x20),
    "UserPatch%Patch_1": (5, 0x40), "UserPatch%Patch_2": (6, 0x20), "UserPatch%Status": (6, 0x50),
}


def A(page, off):
    return (page << 7) | off


def build_image(blocks, log):
    mem = {}
    for name, (pg, off) in BLOCKS.items():
        data = blocks.get(name)
        if data is None:
            if name not in ("UserPatch%Eq(2)", "UserPatch%Status"):
                log.append(f"source has no {name} block - those settings left at template defaults")
            continue
        for i, x in enumerate(data):
            mem[A(pg, off) + i] = int(x, 16)
    return mem


# --------------------------------------------------------------------------------------
# value translation tables (MkII id -> Gen 1 id)
# --------------------------------------------------------------------------------------
AMP_NAMES = {0: "Natural Clean", 1: "ACOUSTIC", 8: "CLEAN", 11: "CRUNCH", 23: "BROWN", 24: "LEAD",
             28: "Var ACOUSTIC", 29: "Var CLEAN", 30: "Var CRUNCH", 31: "Var LEAD", 32: "Var BROWN"}
AMP_MAP = {28: 1, 29: 8, 30: 11, 31: 24, 32: 23}          # MkII "Variation" voices -> base voice
AMP_UNKNOWN_FALLBACK = 11                                   # CRUNCH, for ids newer than MkII

BOOSTER_MAP = {21: 18, 22: 8, 23: 10}                       # HM-2 -> Metal Zone, Metal Core -> Metal DS, Centa OD -> Blues Drive
BOOSTER_NAMES = {21: "HM-2", 22: "Metal Core", 23: "Centa OD"}
BOOSTER_UNKNOWN_FALLBACK = 11

# Gen 1 firmware 4 / BOSS TONE STUDIO 4.0 lists 37 WAH 95E, 38 DC-30 and 39 HEAVY OCTAVE as MOD/FX types
GEN1_FX_TYPES = {0, 1, 2, 3, 4, 6, 7, 9, 10, 12, 14, 15, 16, 18, 19, 20, 21, 22, 23, 25, 26, 27, 28, 29, 31,
                 35, 36, 37, 38, 39}
FX_NAMES = {40: "PEDAL BEND"}
FX_PLACEHOLDER = {40: 15}                                   # nearest Gen 1 type (used for non-active colour slots)

REVERB_MAP = {}   # Gen 1 and MkII number reverb types the same way (0 Amb,1 Room,2 Hall1,3 Hall2,4 Plate,5 Spring,6 Mod) - confirmed from real Gen 1 presets

# (Gen 1 name, number of bytes) in MkII memory order
FX_GROUPS = [
    ("on_off", 1), ("fx_type", 1),
    ("t_wah_mode", 1), ("t_wah_polar", 1), ("t_wah_sens", 1), ("t_wah_freq", 1), ("t_wah_peak", 1),
    ("t_wah_direct_mix", 1), ("t_wah_effect_level", 1),
    ("auto_wah_mode", 1), ("auto_wah_freq", 1), ("auto_wah_peak", 1), ("auto_wah_rate", 1),
    ("auto_wah_depth", 1), ("auto_wah_direct_mix", 1), ("auto_wah_effect_level", 1),
    ("sub_wah_type", 1), ("sub_wah_pedal_pos", 1), ("sub_wah_pedal_min", 1), ("sub_wah_pedal_max", 1),
    ("sub_wah_effect_level", 1), ("sub_wah_direct_mix", 1),
    ("adv_comp_type", 1), ("adv_comp_sustain", 1), ("adv_comp_attack", 1), ("adv_comp_tone", 1),
    ("adv_comp_level", 1),
    ("limiter_type", 1), ("limiter_attack", 1), ("limiter_thresh", 1), ("limiter_ratio", 1),
    ("limiter_release", 1), ("limiter_level", 1),
] + [(f"graphic_eq_{b}", 1) for b in
     ("31hz", "62hz", "125hz", "250hz", "500hz", "1khz", "2khz", "4khz", "8khz", "16khz", "level")] + [
    ("parametric_eq_low_cut", 1), ("parametric_eq_low_gain", 1), ("parametric_eq_low_mid_freq", 1),
    ("parametric_eq_low_mid_q", 1), ("parametric_eq_low_mid_gain", 1), ("parametric_eq_high_mid_freq", 1),
    ("parametric_eq_high_mid_q", 1), ("parametric_eq_high_mid_gain", 1), ("parametric_eq_high_gain", 1),
    ("parametric_eq_high_cut", 1), ("parametric_eq_level", 1),
    ("guitar_sim_type", 1), ("guitar_sim_low", 1), ("guitar_sim_high", 1), ("guitar_sim_level", 1),
    ("guitar_sim_body", 1),
    ("slow_gear_sens", 1), ("slow_gear_rise_time", 1), ("slow_gear_level", 1),
    ("wave_synth_wave", 1), ("wave_synth_cutoff", 1), ("wave_synth_reso", 1), ("wave_synth_filter_sens", 1),
    ("wave_synth_filter_decay", 1), ("wave_synth_filter_depth", 1), ("wave_synth_synth_level", 1),
    ("wave_synth_direct_mix", 1),
    ("octave_range", 1), ("octave_level", 1), ("octave_direct_mix", 1),
    ("pitch_shifter_voice", 1), ("pitch_shifter_ps1mode", 1), ("pitch_shifter_ps1pitch", 1),
    ("pitch_shifter_ps1fine", 1), ("pitch_shifter_ps1pre_dly", 2), ("pitch_shifter_ps1level", 1),
    ("pitch_shifter_ps2mode", 1), ("pitch_shifter_ps2pitch", 1), ("pitch_shifter_ps2fine", 1),
    ("pitch_shifter_ps2pre_dly", 2), ("pitch_shifter_ps2level", 1), ("pitch_shifter_ps1f_back", 1),
    ("pitch_shifter_direct_mix", 1),
    ("harmonist_voice", 1), ("harmonist_hr1harm", 1), ("harmonist_hr1pre_dly", 2), ("harmonist_hr1level", 1),
    ("harmonist_hr2harm", 1), ("harmonist_hr2pre_dly", 2), ("harmonist_hr2level", 1),
    ("harmonist_hr1f_back", 1), ("harmonist_direct_mix", 1),
] + [(f"harmonist_hr{v}{n}", 1) for v in (1, 2) for n in
     ("c", "db", "d", "eb", "e", "f", "f_s", "g", "ab", "a", "bb", "b")] + [
    ("ac_processor_type", 1), ("ac_processor_bass", 1), ("ac_processor_middle", 1),
    ("ac_processor_middle_freq", 1), ("ac_processor_treble", 1), ("ac_processor_presence", 1),
    ("ac_processor_level", 1),
    ("phaser_type", 1), ("phaser_rate", 1), ("phaser_depth", 1), ("phaser_manual", 1), ("phaser_reso", 1),
    ("phaser_step_rate", 1), ("phaser_effect_level", 1), ("phaser_direct_mix", 1),
    ("flanger_rate", 1), ("flanger_depth", 1), ("flanger_manual", 1), ("flanger_reso", 1),
    ("flanger_separation", 1), ("flanger_low_cut", 1), ("flanger_effect_level", 1), ("flanger_direct_mix", 1),
    ("tremolo_wave_shape", 1), ("tremolo_rate", 1), ("tremolo_depth", 1), ("tremolo_level", 1),
    ("rotary_speed_select", 1), ("rotary_rate_slow", 1), ("rotary_rate_fast", 1), ("rotary_rise_time", 1),
    ("rotary_fall_time", 1), ("rotary_depth", 1), ("rotary_level", 1),
    ("uni_v_rate", 1), ("uni_v_depth", 1), ("uni_v_level", 1),
    ("slicer_pattern", 1), ("slicer_rate", 1), ("slicer_trigger_sens", 1), ("slicer_effect_level", 1),
    ("slicer_direct_mix", 1),
    ("vibrato_rate", 1), ("vibrato_depth", 1), ("vibrato_trigger", 1), ("vibrato_rise_time", 1),
    ("vibrato_level", 1),
    ("ring_mod_mode", 1), ("ring_mod_freq", 1), ("ring_mod_effect_level", 1), ("ring_mod_direct_mix", 1),
    ("humanizer_mode", 1), ("humanizer_vowel1", 1), ("humanizer_vowel2", 1), ("humanizer_sens", 1),
    ("humanizer_rate", 1), ("humanizer_depth", 1), ("humanizer_manual", 1), ("humanizer_level", 1),
    ("2x2_chorus_xover_freq", 1), ("2x2_chorus_low_rate", 1), ("2x2_chorus_low_depth", 1),
    ("2x2_chorus_low_pre_delay", 1), ("2x2_chorus_low_level", 1), ("2x2_chorus_high_rate", 1),
    ("2x2_chorus_high_depth", 1), ("2x2_chorus_high_pre_delay", 1), ("2x2_chorus_high_level", 1),
    ("2x2_chorus_direct_level", 1),
    ("acsim_high", 1), ("acsim_body", 1), ("acsim_low", 1), (None, 1), ("acsim_level", 1),   # MkII: Top, Body, Low, High, Level
    ("phaser90e_script", 1), ("phaser90e_speed", 1),
    ("flanger117e_manual", 1), ("flanger117e_width", 1), ("flanger117e_speed", 1), ("flanger117e_regen", 1),
    ("wah95e_pedal_pos", 1), ("wah95e_pedal_min", 1), ("wah95e_pedal_max", 1), ("wah95e_effect_level", 1),
    ("wah95e_direct_mix", 1),
    ("dc30_selector", 1), ("dc30_input_volume", 1), ("dc30_chorus_intensity", 1), ("dc30_echo_repeat_rate", 2),
    ("dc30_echo_intensity", 1), ("dc30_echo_volume", 1), ("dc30_tone", 1), ("dc30_output", 1),
    ("heavy_oct_1oct_level", 1), ("heavy_oct_2oct_level", 1), ("heavy_oct_direct_mix", 1),
    ("@bend_pitch", 1), ("@bend_position", 1), ("@bend_effect_level", 1), ("@bend_direct_mix", 1),  # PEDAL BEND
]
assert sum(n for _, n in FX_GROUPS) == 225

DELAY_LAYOUT = [
    ("on_off", 1), ("type", 1), ("delay_time", 2), ("f_back", 1), ("high_cut", 1), ("effect_level", 1),
    ("direct_mix", 1), ("tap_time", 1), ("d1_time", 2), ("d1_f_back", 1), ("d1_hi_cut", 1), ("d1_level", 1),
    ("d2_time", 2), ("d2_f_back", 1), ("d2_hi_cut", 1), ("d2_level", 1), ("mod_rate", 1), ("mod_depth", 1),
    ("vtg_lpf", 1), ("vtg_filter", 1), ("vtg_feedback_phase", 1), ("vtg_effect_phase", 1), ("vtg_mod_sw", 1),
]
assert sum(n for _, n in DELAY_LAYOUT) == 26

REVERB_LAYOUT = [("on_off", 1), ("type", 1), ("time", 1), ("pre_delay", 2), ("low_cut", 1), ("high_cut", 1),
                 ("density", 1), ("effect_level", 1), ("direct_mix", 1), ("spring_sens", 1)]

BOOSTER_LAYOUT = ["on_off", "type", "drive", "bottom", "tone", "solo_sw", "solo_level", "effect_level",
                  "direct_mix", "custom_type", "custom_bottom", "custom_top", "custom_low", "custom_high",
                  "custom_character"]

AMP_LAYOUT = ["on_off", "type", "gain", "t_comp", "bass", "middle", "treble", "presence", "level", "bright",
              "gain_sw", "solo_sw", "solo_level", "sp_type", "mic_type", "mic_dis", "mic_pos", "mic_level",
              "direct_mix", "custom_type", "custom_bottom", "custom_edge", None, None, "custom_preamp_low",
              "custom_preamp_high", "custom_char", "custom_sp_size", "custom_sp_color_low",
              "custom_sp_color_high", "custom_sp_num", "custom_sp_cabinet"]

EQ_LAYOUT = (["eq_on_off", "eq_type", "eq_low_cut", "eq_low_gain", "eq_low_mid_freq", "eq_low_mid_q",
              "eq_low_mid_gain", "eq_high_mid_freq", "eq_high_mid_q", "eq_high_mid_gain", "eq_high_gain",
              "eq_high_cut", "eq_level"] +
             [f"eq_geq_{b}" for b in ("31hz", "62hz", "125hz", "250hz", "500hz", "1khz", "2khz", "4khz",
                                      "8khz", "16khz", "level")])

COLOURS = ("g", "r", "y")

RANGE2 = {"delay_delay_time": (1, 2000), "delay_d1_time": (1, 1000), "delay_d2_time": (1, 1000),
          "delay2_delay_time": (1, 2000), "delay2_d1_time": (1, 1000), "delay2_d2_time": (1, 1000),
          "reverb_pre_delay": (0, 500), "dc30_echo_repeat_rate": (40, 600)}   # 2-byte values (BOSS TONE STUDIO limits)

PEDAL_FX_LAYOUT = ["pedal_fx_on_off", "pedal_fx_type", "pedal_fx_wah_type", "pedal_fx_wah_position",
                   "pedal_fx_wah_pedal_min", "pedal_fx_wah_pedal_max", "pedal_fx_wah_effect_level",
                   "pedal_fx_wah_direct_mix", "pedal_fx_pedal_bend_pitch", "pedal_fx_pedal_bend_position",
                   "pedal_fx_pedal_bend_effect_level", "pedal_fx_pedal_bend_direct_mix", "pedal_fx_evh95_position",
                   "pedal_fx_evh95_pedal_min", "pedal_fx_evh95_pedal_max", "pedal_fx_evh95_effect_level",
                   "pedal_fx_evh95_direct_mix"]                 # MkII 5:0x50..0x60, same order

CAB_RESONANCE = {1: "Modern", 2: "Deep"}

# Chain block ids (same on both generations)
CS, LOOP, AMP, CH_B, EQ1, MOD, FX, DLY1, DLY2, REV, EQ2, PDL, FV, NS, NS2, BST, USB, SPLIT, CAB, MERGE = range(20)
CHAIN_MOVABLE = {PDL, BST, MOD, FX, EQ1, AMP, NS, FV, LOOP, DLY1, DLY2, REV}
GEN1_CHAIN_TAIL = [CAB, CS, CH_B, EQ2, MERGE, NS2, USB]     # how real Gen 1 patches end the chain
# MkII "chain pattern" -> blocks before / after the amp (used when the file stores no explicit order).
# 0-4 and 6 are confirmed from real MkII patches; 5 follows the same pattern.
MK2_CHAIN_PATTERNS = {0: ([BST], [MOD, FX, DLY1]), 1: ([BST, MOD], [FX, DLY1]), 2: ([BST, MOD, FX], [DLY1]),
                      3: ([BST, MOD, FX, DLY1], []), 4: ([MOD, BST], [FX, DLY1]), 5: ([MOD, BST, FX], [DLY1]),
                      6: ([MOD, BST, FX, DLY1], [])}


def gen1_chain(src, pattern, eq_pos, c):
    """Signal chain for Gen 1, laid out the way real Gen 1 patches are:
    SPLIT, the blocks in use (in the MkII order), then CAB and the unused channel-B blocks."""
    if sorted(src) == list(range(20)):
        body = [b for b in src if b in CHAIN_MOVABLE]
    else:                                   # older MkII files only store the chain pattern number
        pre, post = MK2_CHAIN_PATTERNS.get(pattern, MK2_CHAIN_PATTERNS[1])
        if pattern not in MK2_CHAIN_PATTERNS:
            c.note(f"Unknown MkII chain pattern {pattern}; used Booster/MOD before the amp")
        eq_in = [EQ1] if eq_pos == 0 else []
        body = [PDL] + pre + eq_in + [AMP, NS, FV] + ([] if eq_in else [EQ1]) + [LOOP] + post + [DLY2, REV]
    return [SPLIT] + body + GEN1_CHAIN_TAIL


def gen1_chain_ptn(chain):
    """Nearest Gen 1 chain preset (0: Booster+MOD after amp, 1: before amp, 2: Delay/FX also before amp)."""
    before = set(chain[:chain.index(AMP)])
    if BST not in before and MOD not in before:
        return 0
    return 2 if {FX, DLY1} <= before else 1


# --------------------------------------------------------------------------------------
class Conv:
    def __init__(self, tpl_patch):
        self.P = copy.deepcopy(tpl_patch)
        self.p = self.P["params"]
        self.notes = []
        self.dropped = set()

    def note(self, s):
        if s not in self.notes:
            self.notes.append(s)

    def put(self, key, val):
        if key in self.p:
            self.p[key] = val
        else:
            self.dropped.add(key)

    def put2(self, key, hi, lo):
        v = hi * 128 + lo
        lo_lim, hi_lim = RANGE2.get(key.split("_", 1)[1] if key.startswith(("fx1_", "fx2_")) else key, (0, v))
        if not lo_lim <= v <= hi_lim:                    # damaged value in the source file
            v = min(max(v, lo_lim), hi_lim)
            hi, lo = divmod(v, 128)
        self.put(key, v)
        self.put(key + "_h", hi)
        self.put(key + "_l", lo)


def read_seq(mem, page, off, layout):
    """yield (name, value, hi, lo) walking a layout starting at (page, off)"""
    a = A(page, off)
    for name, n in layout:
        if n == 1:
            yield name, mem.get(a, 0), None, None
        else:
            yield name, mem.get(a, 0) * 128 + mem.get(a + 1, 0), mem.get(a, 0), mem.get(a + 1, 0)
        a += n


def fx_type_for_slot(c, t, active, where):
    """translate a MOD/FX type id; returns (gen1_type, supported)"""
    if t in GEN1_FX_TYPES:
        return t, True
    if t in FX_PLACEHOLDER:
        if active:
            c.note(f"{where}: {FX_NAMES.get(t, t)} does not exist on Gen 1")
        return FX_PLACEHOLDER[t], False
    if active:
        c.note(f"{where}: effect type {t} does not exist on Gen 1")
    return 0, False


def convert_patch(blocks, tpl_patch):
    c = Conv(tpl_patch)
    p = c.p
    mem = build_image(blocks, c.notes)
    g = lambda pg, off: mem.get(A(pg, off), 0)

    # ---- name -------------------------------------------------------------------------
    raw = [g(0, i) for i in range(16)]
    name = bytes(b if 32 <= b < 127 else 32 for b in raw).decode("ascii").rstrip()
    for i, b in enumerate(raw):
        c.put(f"patch_name{i+1}", b)
    c.p["patchname"] = name
    c.P["name"] = name.ljust(16)

    # ---- booster ----------------------------------------------------------------------
    for i, nm in enumerate(BOOSTER_LAYOUT):
        c.put("od_ds_" + nm, g(0, 0x10 + i))
    bt = g(0, 0x11)
    if bt in BOOSTER_MAP:
        c.put("od_ds_type", BOOSTER_MAP[bt])
        if g(0, 0x10):
            c.note(f"Booster {BOOSTER_NAMES[bt]} is MkII-only; used the closest Gen 1 booster instead")
    elif bt > 20:
        c.put("od_ds_type", BOOSTER_UNKNOWN_FALLBACK)
        c.note(f"Booster type {bt} unknown on Gen 1; used Over Drive")
    if p["od_ds_drive"] > 120:
        c.note(f"Booster drive {p['od_ds_drive']} is above the Gen 1 maximum; limited to 120")
        c.put("od_ds_drive", 120)

    # ---- amp --------------------------------------------------------------------------
    for i, nm in enumerate(AMP_LAYOUT):
        if nm:
            c.put("preamp_a_" + nm, g(0, 0x20 + i))
    at = g(0, 0x21)
    if at in AMP_MAP:
        c.put("preamp_a_type", AMP_MAP[at])
        c.note(f"Amp {AMP_NAMES[at]} (MkII Variation) -> {AMP_NAMES[AMP_MAP[at]]}: Gen 1 has no Variation "
               f"voice, so the base voice was used - it may sound a little different")
    elif at > 27:
        c.put("preamp_a_type", AMP_UNKNOWN_FALLBACK)
        c.note(f"Amp id {at} is not a Gen 1 amp; used CRUNCH - check the amp type")
    if p["preamp_a_gain"] > 120:
        c.note(f"Amp gain {p['preamp_a_gain']} is above the Gen 1 maximum; limited to 120")
        c.put("preamp_a_gain", 120)

    # ---- EQ (EQ1; if EQ1 is off and EQ2 is on, EQ2 takes its place) -------------------
    eq_page, eq_off = 0, 0x40
    eq_pos = g(6, 0x22)
    if not g(0, 0x40) and g(0, 0x60):
        eq_off, eq_pos = 0x60, g(6, 0x19)
        c.note("MkII EQ 2 was the one in use; copied into the Gen 1 EQ")
    elif g(0, 0x40) and g(0, 0x60):
        c.note("MkII EQ 2 is also on; Gen 1 has one EQ, so EQ 2 was not applied")
    for i, key in enumerate(EQ_LAYOUT):
        c.put(key, g(eq_page, eq_off + i))
    c.put("eq_position", eq_pos)

    # ---- MOD (FX1) and FX (FX2) -------------------------------------------------------
    bend = []
    for n, page in ((1, 1), (2, 3)):
        a = A(page, 0)
        vals = {}
        for name_, size in FX_GROUPS:
            if name_ is not None:
                if size == 1:
                    vals[name_] = mem.get(a, 0)
                else:
                    vals[name_] = (mem.get(a, 0), mem.get(a + 1, 0))
            a += size
        label = "MOD" if n == 1 else "FX"
        on, typ = vals["on_off"], vals["fx_type"]
        c.put(f"fx{n}_on_off", on)
        gtype, ok = fx_type_for_slot(c, typ, on, label)
        c.put(f"fx{n}_fx_type", gtype)
        if not ok and on:
            c.put(f"fx{n}_on_off", 0)
            if typ == 40:                                   # Pedal Bend lives in the Gen 1 Pedal FX block instead
                bend.append(vals)
            else:
                c.note(f"{label}: switched off (no Gen 1 equivalent)")
        for name_, v in vals.items():
            if name_ in ("on_off", "fx_type") or name_.startswith("@"):
                continue
            key = f"fx{n}_{name_}"
            if isinstance(v, tuple):
                c.put2(key, *v)
            else:
                c.put(key, v)

    # ---- delays -----------------------------------------------------------------------
    for n, off, pre in ((1, 0x00, "delay_"), (2, 0x20, "delay2_")):
        for name_, v, hi, lo in read_seq(mem, 5, off, DELAY_LAYOUT):
            if hi is None:
                c.put(pre + name_, v)
            else:
                c.put2(pre + name_, hi, lo)

    # ---- reverb -----------------------------------------------------------------------
    for name_, v, hi, lo in read_seq(mem, 5, 0x40, REVERB_LAYOUT):
        if hi is None:
            c.put("reverb_" + name_, v)
        else:
            c.put2("reverb_" + name_, hi, lo)
    rt = g(5, 0x41)
    if rt in REVERB_MAP:
        c.put("reverb_type", REVERB_MAP[rt])
        c.note("Reverb Hall 1 -> Gen 1 Hall")

    # ---- pedal FX (wah / pedal bend / wah 95E, worked by an expression pedal) ----------
    for i, key in enumerate(PEDAL_FX_LAYOUT):
        c.put(key, g(5, 0x50 + i))
    c.put("pedal_fx_position", g(6, 0x23))
    if bend:
        if g(5, 0x50):
            c.note("Pedal Bend in MOD/FX switched off: the Gen 1 has it only in the Pedal FX slot, which this "
                   "patch already uses")
        else:
            v = bend[0]
            c.put("pedal_fx_on_off", 1)
            c.put("pedal_fx_type", 1)
            for k in ("pitch", "position", "effect_level", "direct_mix"):
                c.put("pedal_fx_pedal_bend_" + k, v["@bend_" + k])
            c.note("Pedal Bend moved from MOD/FX to the Gen 1 Pedal FX slot (needs an expression pedal)")

    # ---- foot volume, send/return, noise suppressor, patch level ----------------------
    c.put("foot_volume_level", g(5, 0x61))
    c.put("send_return_on_off", g(5, 0x62))
    c.put("send_return_mode", g(5, 0x63))
    c.put("send_return_send_level", g(5, 0x64))
    c.put("send_return_return_level", g(5, 0x65))
    c.put("send_return_position", g(6, 0x21))
    c.put("ns1_on_off", g(5, 0x66))
    c.put("ns1_threshold", g(5, 0x67))
    c.put("ns1_release", g(5, 0x68))
    c.put("patch_level", g(5, 0x70))
    c.put("master_key", g(5, 0x71))

    # ---- signal chain order -------------------------------------------------------------
    chain = gen1_chain([g(6, i) for i in range(20)], g(6, 0x20), g(6, 0x22), c)
    for i, v in enumerate(chain):
        c.put(f"fx_chain_position{i+1}", v)
    cp = {f"position{i+1}": v for i, v in enumerate(chain)}
    cp["positionList"] = chain
    if "chainParams" in p:
        p["chainParams"] = cp
    c.put("chain_ptn", gen1_chain_ptn(chain))

    # ---- colour slots (green / red / yellow) and which one is selected -----------------
    boxes = [("fx1a", 0x24, "Booster"), ("fx1b", 0x27, "MOD"), ("fx2b", 0x2A, "FX"),
             ("fx2a", 0x2D, "Delay 1"), ("fx3", 0x30, "Reverb"), ("fx3b", 0x33, "Delay 2")]
    sel_off = {"fx1a": 0x39, "fx1b": 0x3A, "fx2b": 0x3B, "fx2a": 0x3C, "fx3": 0x3D}
    for box, base, label in boxes:
        for i, col in enumerate(COLOURS):
            t = g(6, base + i)
            if box == "fx1a" and t in BOOSTER_MAP:
                t = BOOSTER_MAP[t]
            elif box in ("fx1b", "fx2b") and t not in GEN1_FX_TYPES:
                t = FX_PLACEHOLDER.get(t, 0)
            elif box == "fx3" and t in REVERB_MAP:
                t = REVERB_MAP[t]
            c.put(f"fxbox_asgn_{box}_{col}", t)
    for i, col in enumerate(COLOURS):
        c.put(f"fxbox_layer_fx3_{col}", g(6, 0x36 + i))
    for box, off in sel_off.items():
        c.put(f"fxbox_sel_{box}", min(g(6, off), 2))

    # ---- which of each shared pair is "active" on the Gen 1 panel -----------------------
    bst_on, mod_on = g(0, 0x10), g(1, 0x00)
    dly_on, fx_on = g(5, 0x00), g(3, 0x00)
    c.put("fx_active_ab_fx1", 0 if (bst_on or not mod_on) else 1)
    c.put("fx_active_ab_fx2", 0 if (dly_on or not fx_on) else 1)
    if bst_on and mod_on:
        c.note("Booster and MOD are both ON (Gen 1 panel shows only one of the pair)" +
               (": MOD switched off (--strict-panel)" if STRICT_PANEL else ": both kept on"))
        if STRICT_PANEL:
            c.put("fx1_on_off", 0)
    if dly_on and fx_on:
        c.note("Delay and FX are both ON (Gen 1 panel shows only one of the pair)" +
               (": FX switched off (--strict-panel)" if STRICT_PANEL else ": both kept on"))
        if STRICT_PANEL:
            c.put("fx2_on_off", 0)

    # ---- things that cannot be carried over ---------------------------------------------
    if g(6, 0x16):
        c.note(f"Contour {g(6, 0x17) + 1} is ON in the MkII patch - Gen 1 has no Contour (tone will differ)")
    if g(6, 0x14):
        c.note("MkII Solo EQ is ON - Gen 1 has no Solo EQ")
    if g(6, 0x43) in CAB_RESONANCE:
        c.note(f"Cab Resonance {CAB_RESONANCE[g(6, 0x43)]} is set in the MkII patch - Gen 1 has no Cab "
               f"Resonance, so the low end may sound different")
    c.P["id"] = str(random.randint(10 ** 9, 10 ** 10 - 1))
    return c


# --------------------------------------------------------------------------------------
def load_template():
    return json.loads(zlib.decompress(base64.b64decode(TEMPLATE_B64)).decode("utf-8"))


SLOTS = ["A: CH1", "A: CH2", "A: CH3", "A: CH4", "B: CH1", "B: CH2", "B: CH3", "B: CH4"]
REQUIRED_BLOCKS = ("UserPatch%PatchName", "UserPatch%Patch_0", "UserPatch%Fx(1)", "UserPatch%Fx(2)",
                   "UserPatch%Delay(1)", "UserPatch%Patch_1")


class Result:
    """What happened to one input file (used by both the window and the text mode)."""

    def __init__(self, source):
        self.source = source
        self.out_path = None
        self.status = "skipped"          # "ok" | "skipped" | "error"
        self.message = ""
        self.patches = []                # [(patch name, [notes])]


def free_name(path):
    """never overwrite an existing file: add ' 2', ' 3' ... if the name is taken"""
    if not os.path.exists(path):
        return path
    root, ext = os.path.splitext(path)
    n = 2
    while os.path.exists(f"{root} {n}{ext}"):
        n += 1
    return f"{root} {n}{ext}"


def convert_file(src_path, out_dir=None):
    """Convert one MkII .tsl file. Never raises: problems are reported in the Result."""
    res = Result(src_path)
    folder, fname = os.path.split(src_path)
    base = os.path.splitext(fname)[0]
    try:
        if base.endswith("(Gen1)"):
            res.message = "Already converted - skipped."
            return res
        try:
            with open(src_path, encoding="utf-8-sig") as fh:
                src = json.load(fh)
        except Exception:
            res.status = "error"
            res.message = "This does not look like a BOSS Tone Studio .tsl patch file."
            return res
        if not isinstance(src, dict):
            res.status = "error"
            res.message = "This does not look like a BOSS Tone Studio .tsl patch file."
            return res
        device = str(src.get("device", ""))
        if "patchList" in src:
            res.message = f"Already a Gen 1 file (amp type '{device}') - nothing to convert."
            return res
        if "data" not in src or "KATANA" not in device.upper():
            res.status = "error"
            res.message = f"Not a Katana MkII patch file (found amp type '{device or 'unknown'}')."
            return res
        if "GEN3" in device.upper().replace(" ", ""):
            res.status = "error"
            res.message = ("This is a Katana Gen 3 patch file. Gen 3 stores patches in a different layout that "
                           "this converter can not read yet - only MkII files can be converted.")
            return res

        tpl = load_template()
        out = copy.deepcopy(tpl)
        out["liveSetData"]["name"] = str(src.get("name") or base)[:40]
        out["liveSetData"]["id"] = str(random.randint(10 ** 9, 10 ** 10 - 1))
        out["patchList"] = []
        used_ids = set()
        rev = str(src.get("formatRev", ""))
        extra = []
        if rev and rev not in ("0001", "0002"):
            extra.append(f"File format revision {rev} has not been tested (MkII files are 0001 or 0002). "
                         f"Please listen carefully to this patch.")
        k = 0
        for liveset in src["data"]:
            for patch in liveset:
                blocks = patch.get("paramSet", {}) if isinstance(patch, dict) else {}
                missing = [b.split("%")[1] for b in REQUIRED_BLOCKS if b not in blocks]
                label = patch.get("memo") if isinstance(patch, dict) else ""
                if missing:
                    res.patches.append((label or f"patch {k + 1}",
                                        [f"SKIPPED: this patch is missing data ({', '.join(missing)}), "
                                         f"so it can not be converted safely."]))
                    continue
                k += 1
                c = convert_patch(blocks, tpl["patchList"][0])
                P = c.P
                while P["id"] in used_ids:
                    P["id"] = str(random.randint(10 ** 9, 10 ** 10 - 1))
                used_ids.add(P["id"])
                P["orderNumber"] = k
                P["liveSetId"] = out["liveSetData"]["id"]
                P["patchNo"] = SLOTS[k - 1] if k <= len(SLOTS) else None
                P["category"] = "USER1"
                out["patchList"].append(P)
                res.patches.append((P["name"].strip() or f"patch {k}", extra + c.notes if k == 1 else c.notes))
        if not out["patchList"]:
            res.status = "error"
            res.message = "No patches could be converted from this file."
            return res
        out_dir = out_dir or folder or "."
        os.makedirs(out_dir, exist_ok=True)
        res.out_path = free_name(os.path.join(out_dir, base + " (Gen1).tsl"))
        with open(res.out_path, "w", encoding="utf-8") as fh:
            json.dump(out, fh, separators=(",", ":"))
        res.status = "ok"
        res.message = f"Saved {len(out['patchList'])} patch(es)."
        return res
    except Exception as e:                       # last resort - never crash on the user
        res.status = "error"
        res.message = f"Something unexpected went wrong ({type(e).__name__}: {e})."
        return res


def describe(res):
    """plain-text report for one file"""
    icon = {"ok": "[OK]", "skipped": "[--]", "error": "[!!]"}[res.status]
    lines = [f"{icon} {os.path.basename(res.source)}", f"     {res.message}"]
    for name, notes in res.patches:
        lines.append(f"     - {name}")
        for n in notes:
            lines.append(f"         * {n}")
    if res.out_path:
        lines.append(f"     New file: {res.out_path}")
    return "\n".join(lines)


def run_batch(files, out_dir=None):
    results = [convert_file(f, out_dir) for f in files]
    ok = sum(r.status == "ok" for r in results)
    return results, ok


# --------------------------------------------------------------------------------------
# Simple window (tkinter ships with the normal Windows / Mac Python installer)
# --------------------------------------------------------------------------------------
HELP_TEXT = (
    "1. Click 'Choose patch files' and pick the .tsl file(s) you downloaded for a Katana MkII.\n"
    "2. Click 'Convert to Gen 1'.\n"
    "3. Open BOSS TONE STUDIO, connect your Gen 1 Katana, click Import, and pick the new file "
    "that ends in (Gen1).tsl.\n\n"
    "Lines marked * under a patch are things that cannot be copied exactly to Gen 1. "
    "Those patches are still converted - listen to them and adjust to taste."
)


def run_window(preselected=()):
    import tkinter as tk
    from tkinter import filedialog, messagebox, ttk

    root = tk.Tk()
    root.title("Katana Patch Converter - MkII to Gen 1")
    root.geometry("760x640")
    root.minsize(640, 520)
    state = {"files": [], "last_dir": None}

    big = ("Segoe UI", 12)
    ttk.Style().configure("Big.TButton", font=("Segoe UI", 12, "bold"), padding=8)

    ttk.Label(root, text="Katana Patch Converter", font=("Segoe UI", 18, "bold")).pack(pady=(14, 0))
    ttk.Label(root, text="Turn patches made for the Katana MkII into patches your Gen 1 Katana can use",
              font=big, wraplength=700, justify="center").pack(pady=(2, 10))

    top = ttk.Frame(root)
    top.pack(fill="x", padx=16)
    ttk.Label(top, text="Step 1", font=("Segoe UI", 11, "bold")).grid(row=0, column=0, sticky="w")
    pick_btn = ttk.Button(top, text="Choose patch files...", style="Big.TButton")
    pick_btn.grid(row=0, column=1, padx=10, sticky="w")
    files_var = tk.StringVar(value="No files chosen yet")
    ttk.Label(top, textvariable=files_var, font=big, wraplength=420).grid(row=0, column=2, sticky="w")

    mid = ttk.Frame(root)
    mid.pack(fill="x", padx=16, pady=(10, 0))
    ttk.Label(mid, text="Step 2", font=("Segoe UI", 11, "bold")).grid(row=0, column=0, sticky="w")
    go_btn = ttk.Button(mid, text="Convert to Gen 1", style="Big.TButton", state="disabled")
    go_btn.grid(row=0, column=1, padx=10, sticky="w")
    strict_var = tk.BooleanVar(value=False)
    ttk.Checkbutton(mid, variable=strict_var,
                    text="Gen 1 button style (only one effect per shared button)").grid(row=0, column=2, sticky="w")

    ttk.Label(root, text="Step 3: import the new files into BOSS TONE STUDIO (see 'How do I use this?')",
              font=("Segoe UI", 11, "bold")).pack(anchor="w", padx=16, pady=(10, 2))

    box = ttk.Frame(root)
    box.pack(fill="both", expand=True, padx=16, pady=(0, 6))
    txt = tk.Text(box, wrap="word", font=("Consolas", 10), state="disabled", height=14)
    sb = ttk.Scrollbar(box, command=txt.yview)
    txt.configure(yscrollcommand=sb.set)
    sb.pack(side="right", fill="y")
    txt.pack(side="left", fill="both", expand=True)

    def show(text, clear=False):
        txt.configure(state="normal")
        if clear:
            txt.delete("1.0", "end")
        txt.insert("end", text)
        txt.configure(state="disabled")
        txt.see("end")

    bottom = ttk.Frame(root)
    bottom.pack(fill="x", padx=16, pady=(0, 14))
    open_btn = ttk.Button(bottom, text="Open the folder with my new files", state="disabled")
    open_btn.pack(side="left")
    ttk.Button(bottom, text="How do I use this?",
               command=lambda: messagebox.showinfo("How to use", HELP_TEXT)).pack(side="left", padx=8)
    ttk.Button(bottom, text="Close", command=root.destroy).pack(side="right")

    def set_files(files):
        state["files"] = [f for f in files if f]
        n = len(state["files"])
        if n == 0:
            files_var.set("No files chosen yet")
            go_btn.configure(state="disabled")
        else:
            names = ", ".join(os.path.basename(f) for f in state["files"][:3])
            files_var.set(f"{n} file(s) chosen: {names}" + (" ..." if n > 3 else ""))
            go_btn.configure(state="normal")

    def choose():
        files = filedialog.askopenfilenames(
            title="Choose Katana MkII patch file(s)",
            filetypes=[("Katana patch files", "*.tsl"), ("All files", "*.*")])
        if files:
            set_files(list(files))
            show("Ready. Click 'Convert to Gen 1'.\n", clear=True)

    def open_folder():
        d = state["last_dir"]
        if not d:
            return
        try:
            if os.name == "nt":
                os.startfile(d)                                   # noqa
            elif sys.platform == "darwin":
                os.system(f'open "{d}"')
            else:
                os.system(f'xdg-open "{d}" >/dev/null 2>&1 &')
        except Exception:
            messagebox.showinfo("Folder", d)

    def convert():
        global STRICT_PANEL
        STRICT_PANEL = bool(strict_var.get())
        show("Converting...\n", clear=True)
        root.update_idletasks()
        results, ok = run_batch(state["files"])
        show("\n\n".join(describe(r) for r in results), clear=True)
        done = [r for r in results if r.out_path]
        if done:
            state["last_dir"] = os.path.dirname(os.path.abspath(done[-1].out_path))
            open_btn.configure(state="normal")
            show(f"\n\nDone: {ok} of {len(results)} file(s) converted. "
                 f"Next: import the (Gen1).tsl file(s) into BOSS TONE STUDIO.\n")
        else:
            show("\n\nNothing was converted - see the messages above.\n")

    pick_btn.configure(command=choose)
    go_btn.configure(command=convert)
    open_btn.configure(command=open_folder)

    show(HELP_TEXT + "\n", clear=True)
    if preselected:
        set_files(list(preselected))
        root.after(200, convert)
    root.mainloop()


def run_text_mode(files):
    if not files:
        print("Type or drag the path of a .tsl file here and press Enter (empty = quit):")
        line = input("> ").strip()
        if not line:
            return
        import shlex
        files = shlex.split(line, posix=(os.name != "nt"))
    results, ok = run_batch([f.strip('"') for f in files])
    print()
    for r in results:
        print(describe(r))
        print()
    print(f"Done: {ok} of {len(results)} file(s) converted.")


def main():
    files = [a.strip('"') for a in sys.argv[1:] if not a.startswith("--")]
    if "--cli" in sys.argv:
        run_text_mode(files)
        return
    try:
        import tkinter  # noqa: F401
    except Exception:
        run_text_mode(files)
        return
    run_window(files)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("Error:", e)
        if os.name == "nt":
            input("\nPress Enter to close...")
