#!/usr/bin/env python3
"""palimpsest.py -- arithmetic helper for PALIMPSEST RUBRIC v1.0.

Floor = piecewise-linear interpolation over the union of
  * McEvedy & Jones (1978) published anchors (the rubric's default floor),
  * the rubric floors table's own explicit points where they are LOWER
    (160M at 1 CE, 185M plague trough c. 550, 350M at 1450, 5M at 4500 BCE, 9M at 3300 BCE),
  * Maddison / UN anchors for 1870 onward, as the floors table itself uses.
With --deep, cited floors below the default are added (rubric: "Going below the
floor requires a citation") -- each carries its citation in DEEP.

Years: negative = BCE (astronomical convention not used: -500 means 500 BCE, 1 means 1 CE).

Examples
  python3 palimpsest.py floor 100
  python3 palimpsest.py floor 1650 --deep
  python3 palimpsest.py share --year 100 --pop 1.5e6 2.2e6 --mult 2.0 2.5
  python3 palimpsest.py share --year 1650 --pop 1.8e5 2.0e5 --mult 3.0 5.0 --deep
  python3 palimpsest.py share --year 2023 --pop 9.7e6 --gdp 0.84e12 --world-gdp 105e12
  python3 palimpsest.py band 0.0085
"""
import argparse
import math
import sys

# ---- world population anchors (millions) -----------------------------------
MJ = [  # McEvedy & Jones, Atlas of World Population History (1978)
    (-10000, 4), (-5000, 5), (-4000, 7), (-3000, 14), (-2000, 27), (-1000, 50),
    (-500, 100), (-200, 150), (1, 170), (200, 190), (400, 190), (500, 190),
    (600, 200), (700, 210), (800, 220), (900, 240), (1000, 265), (1100, 320),
    (1200, 360), (1300, 360), (1400, 350), (1500, 425), (1600, 545), (1650, 545),
    (1700, 610), (1750, 720), (1800, 900), (1850, 1200), (1900, 1625), (1950, 2500),
]
RUBRIC_POINTS = [  # explicit points in the rubric floors table (used where lower)
    (-4500, 5), (-3300, 9), (1, 160), (550, 185), (1450, 350),
    (1870, 1272), (1918, 1790), (1950, 2500), (1980, 4430), (2000, 6080), (2026, 8200),
]
MADDISON_POP = [  # Maddison 2001/2003, millions
    (1820, 1041.7), (1870, 1271.9), (1900, 1564.4), (1913, 1791.0), (1950, 2524.5),
    (1973, 3913.5), (1998, 5907.7),
]
UN_POP = [(1980, 4434), (2000, 6080), (2010, 6900), (2020, 7795), (2024, 8160), (2026, 8200)]

DEEP = {  # cited floors BELOW the default; VERIFY against the printed table before citing
    (1, 133): "Deevey 1960, Sci. Am. 203(3), table: 2000 BP = 133M",
    (900, 226): "Biraben 1979/1980, table 2: 900 CE = 226M",
    (1000, 254): "Biraben 1979/1980, table 2: 1000 CE = 254M",
    (1100, 301): "Biraben 1979/1980, table 2: 1100 CE = 301M",
    (1650, 470): "Willcox 1931 (NBER, Int. Migrations II): 1650 = 470M",
    (1750, 694): "Willcox 1931: 1750 = 694M",
    (1850, 1091): "Willcox 1931: 1850 = 1,091M",
    (1900, 1571): "Willcox 1931: 1900 = 1,571M",
}

# ---- Maddison world GDP, billions of 1990 international dollars --------------
MADDISON_GDP = [
    (1, 102.5), (1000, 116.8), (1500, 247.1), (1600, 329.4), (1700, 371.4),
    (1820, 694.4), (1870, 1101.4), (1913, 2704.8), (1950, 5336.1), (1973, 16059.2),
    (1998, 33725.6), (2003, 40913.4),
]

# ---- band ladder (fractions, not percent) -----------------------------------
LADDER = [(10, 9e-4), (9, 5e-4), (8, 2.8e-4), (7, 1.5e-4), (6, 7e-5), (5, 3e-5),
          (4, 1.2e-5), (3, 4e-6), (2, 1e-6), (1, 0.0)]
EXT_STEP = 1.8  # proposed open-top extension above band 10 (same ~1.8x step)

MULTIPLIERS = {
    "agrarian": (0.8, 1.2),
    "regional": (1.2, 1.6),
    "capital_or_entrepot": (1.6, 2.0),
    "quantified_fiscal": (2.0, 2.5),
    "extraction": (2.5, None),
}


def _merge_min(*series):
    pts = {}
    for s in series:
        for y, v in s:
            pts[y] = min(v, pts.get(y, float("inf")))
    return sorted(pts.items())


def _interp(points, year):
    if year <= points[0][0]:
        return points[0][1]
    if year >= points[-1][0]:
        return points[-1][1]
    for (y0, v0), (y1, v1) in zip(points, points[1:]):
        if y0 <= year <= y1:
            return v0 + (v1 - v0) * (year - y0) / (y1 - y0)
    raise ValueError(year)


def floor_points(deep=False):
    base = _merge_min(MJ, RUBRIC_POINTS, MADDISON_POP, UN_POP)
    if deep:
        base = _merge_min(base, list(DEEP.keys()))
    return base


def world_pop(year, deep=False):
    """World population floor in persons."""
    return _interp(floor_points(deep), year) * 1e6


def world_gdp_1990(year):
    """Maddison world GDP in 1990 int'l dollars (log-linear interpolation)."""
    pts = [(y, math.log(v)) for y, v in MADDISON_GDP]
    return math.exp(_interp(pts, year)) * 1e9


def band(share):
    """Rubric band 1-10 plus the proposed open-top extension (None if <= 10)."""
    b = 1
    for bb, thr in LADDER:
        if share >= thr:
            b = bb
            break
    ext = None
    if share >= LADDER[0][1]:
        ext = 10 + int(math.floor(math.log(share / LADDER[0][1]) / math.log(EXT_STEP)))
    return b, ext


def deep_citations(year, deep):
    """Citations for deep floors that actually bind at this year."""
    if not deep:
        return []
    fl = world_pop(year, True) / 1e6
    return [c for (y, v), c in DEEP.items() if y == year and abs(v - fl) < 1e-9]


def fmt_share(x):
    return f"{100 * x:.4f}%" if x < 1e-3 else f"{100 * x:.3f}%"


def cmd_floor(a):
    v = world_pop(a.year, a.deep)
    print(f"world population floor at {a.year}: {v / 1e6:,.1f} M (deep={a.deep})")
    for c in deep_citations(a.year, a.deep):
        print("  cite:", c)


def cmd_share(a):
    wp = world_pop(a.year, a.deep)
    print(f"year {a.year}: world pop floor {wp / 1e6:,.1f} M" + (" [deep]" if a.deep else ""))
    for c in deep_citations(a.year, a.deep):
        print("  cite:", c)
    lo, hi = (a.pop + a.pop)[:2]
    ps = (lo / wp, hi / wp)
    b_lo, e_lo = band(ps[0]); b_hi, e_hi = band(ps[1])
    print(f"POP share: {fmt_share(ps[0])} - {fmt_share(ps[1])}  band {b_lo}-{b_hi}"
          + (f" (ext {e_lo}-{e_hi})" if e_lo else ""))
    if a.mult:
        mlo, mhi = (a.mult + a.mult)[:2]
        gs = (ps[0] * mlo, ps[1] * mhi)
        b_lo, e_lo = band(gs[0]); b_hi, e_hi = band(gs[1])
        print(f"GDP share (pop x {mlo}-{mhi}): {fmt_share(gs[0])} - {fmt_share(gs[1])}  band {b_lo}-{b_hi}"
              + (f" (ext {e_lo}-{e_hi})" if e_lo else ""))
    if a.gdp:
        wg = a.world_gdp if a.world_gdp else world_gdp_1990(a.year)
        glo, ghi = (a.gdp + a.gdp)[:2]
        gs = (glo / wg, ghi / wg)
        b_lo, e_lo = band(gs[0]); b_hi, e_hi = band(gs[1])
        label = "given" if a.world_gdp else "Maddison 1990$ interp."
        print(f"GDP share (direct, world GDP {wg:,.3e} {label}): {fmt_share(gs[0])} - {fmt_share(gs[1])}  band {b_lo}-{b_hi}"
              + (f" (ext {e_lo}-{e_hi})" if e_lo else ""))


def cmd_band(a):
    s = a.share / 100 if a.percent else a.share
    b, e = band(s)
    print(f"share {fmt_share(s)} -> band {b}" + (f" (ext {e})" if e else ""))


def cmd_table(a):
    print("year, floor_default_M, floor_deep_M")
    for y in a.years:
        print(f"{y}, {world_pop(y) / 1e6:,.1f}, {world_pop(y, True) / 1e6:,.1f}")


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    f = sub.add_parser("floor"); f.add_argument("year", type=int); f.add_argument("--deep", action="store_true"); f.set_defaults(fn=cmd_floor)
    s = sub.add_parser("share")
    s.add_argument("--year", type=int, required=True)
    s.add_argument("--pop", type=float, nargs="+", required=True, help="numerator population (lo [hi]), persons")
    s.add_argument("--mult", type=float, nargs="+", help="pre-1820 GDP multiplier (lo [hi])")
    s.add_argument("--gdp", type=float, nargs="+", help="direct GDP numerator (lo [hi]) in the same units as --world-gdp")
    s.add_argument("--world-gdp", type=float, help="world GDP denominator (same units as --gdp); default Maddison 1990$")
    s.add_argument("--deep", action="store_true"); s.set_defaults(fn=cmd_share)
    b = sub.add_parser("band"); b.add_argument("share", type=float); b.add_argument("--percent", action="store_true"); b.set_defaults(fn=cmd_band)
    t = sub.add_parser("table"); t.add_argument("years", type=int, nargs="+"); t.set_defaults(fn=cmd_table)
    a = p.parse_args(argv)
    a.fn(a)


if __name__ == "__main__":
    main()
