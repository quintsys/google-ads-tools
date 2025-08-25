#!/usr/bin/env python3
# expand_geo.py
import csv, argparse, itertools

STATES = [
 "Alabama","Alaska","Arizona","Arkansas","California","Colorado","Connecticut","Delaware",
 "Florida","Georgia","Hawaii","Idaho","Illinois","Indiana","Iowa","Kansas","Kentucky",
 "Louisiana","Maine","Maryland","Massachusetts","Michigan","Minnesota","Mississippi",
 "Missouri","Montana","Nebraska","Nevada","New Hampshire","New Jersey","New Mexico",
 "New York","North Carolina","North Dakota","Ohio","Oklahoma","Oregon","Pennsylvania",
 "Rhode Island","South Carolina","South Dakota","Tennessee","Texas","Utah","Vermont",
 "Virginia","Washington","West Virginia","Wisconsin","Wyoming"
]

STATE_ABBREV = {
 "Alabama":"AL","Alaska":"AK","Arizona":"AZ","Arkansas":"AR","California":"CA","Colorado":"CO",
 "Connecticut":"CT","Delaware":"DE","Florida":"FL","Georgia":"GA","Hawaii":"HI","Idaho":"ID",
 "Illinois":"IL","Indiana":"IN","Iowa":"IA","Kansas":"KS","Kentucky":"KY","Louisiana":"LA",
 "Maine":"ME","Maryland":"MD","Massachusetts":"MA","Michigan":"MI","Minnesota":"MN",
 "Mississippi":"MS","Missouri":"MO","Montana":"MT","Nebraska":"NE","Nevada":"NV",
 "New Hampshire":"NH","New Jersey":"NJ","New Mexico":"NM","New York":"NY",
 "North Carolina":"NC","North Dakota":"ND","Ohio":"OH","Oklahoma":"OK","Oregon":"OR",
 "Pennsylvania":"PA","Rhode Island":"RI","South Carolina":"SC","South Dakota":"SD",
 "Tennessee":"TN","Texas":"TX","Utah":"UT","Vermont":"VT","Virginia":"VA","Washington":"WA",
 "West Virginia":"WV","Wisconsin":"WI","Wyoming":"WY"
}

# Starter metros – expand as needed (keep commas out of names)
METROS = [
 "Atlanta","Austin","Baltimore","Boston","Charlotte","Chicago","Cincinnati","Cleveland",
 "Columbus","Dallas","Denver","Detroit","Houston","Indianapolis","Jacksonville","Kansas City",
 "Las Vegas","Los Angeles","Miami","Minneapolis","Nashville","New Orleans","New York",
 "Orlando","Philadelphia","Phoenix","Pittsburgh","Portland","Raleigh","Sacramento","Salt Lake City",
 "San Antonio","San Diego","San Francisco","San Jose","Seattle","St Louis","Tampa","Washington"
]

# Optional counties: add only your target ones to keep volume sane
COUNTIES = [
 # "Gwinnett County","Cobb County","Orange County","Harris County"
]

def variants_for_geo(kw: str, geo: str):
    """Generate prefix/suffix, with and without 'in '"""
    g = geo
    return {
        f"{kw} in {g}",
        f"{kw} {g}",
        f"{g} {kw}",
    }

def expand_keywords(keywords, use_states=True, use_abbrev=True, use_metros=True, use_counties=False):
    out = set()
    for kw in keywords:
        kw = " ".join(kw.split())  # collapse spaces
        base = {kw}
        out |= base
        if use_states:
            for st in STATES:
                out |= variants_for_geo(kw, st)
                if use_abbrev:
                    out |= variants_for_geo(kw, STATE_ABBREV[st])
        if use_metros:
            for m in METROS:
                out |= variants_for_geo(kw, m)
        if use_counties:
            for c in COUNTIES:
                out |= variants_for_geo(kw, c)
    # Normalize whitespace and dedupe again
    cleaned = sorted({" ".join(x.split()) for x in out})
    return cleaned

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input_txt", help="Plain text file with one keyword per line")
    ap.add_argument("output_csv", help="CSV to write")
    ap.add_argument("--campaign", default="Ogburn Online School")
    ap.add_argument("--adgroup", default="General - Home School Programs #2")
    ap.add_argument("--action", default="Add")
    ap.add_argument("--status", default="Enabled")
    ap.add_argument("--match", default="Exact match")  # or use Exact if you prefer
    ap.add_argument("--no-states", action="store_true")
    ap.add_argument("--no-abbrev", action="store_true")
    ap.add_argument("--metros", action="store_true")      # off by default; turn on explicitly
    ap.add_argument("--counties", action="store_true")    # off by default; turn on explicitly
    args = ap.parse_args()

    # load seeds
    with open(args.input_txt, "r", encoding="utf-8") as f:
        seeds = [ln.strip() for ln in f if ln.strip()]

    expanded = expand_keywords(
        seeds,
        use_states=not args.no_states,
        use_abbrev=not args.no_abbrev,
        use_metros=args.metros,
        use_counties=args.counties,
    )

    with open(args.output_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
        w.writerow(["Action","Keyword status","Campaign","Ad group","Keyword","Match type"])
        for kw in expanded:
            w.writerow([args.action, args.status, args.campaign, args.adgroup, kw, args.match])

if __name__ == "__main__":
    main()
