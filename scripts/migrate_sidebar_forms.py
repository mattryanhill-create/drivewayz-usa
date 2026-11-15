#!/usr/bin/env python3
"""Migrate guide sidebar forms from the alert-only handleSidebarSubmit to /js/lead-capture.js.

Dry run by default. Use --apply to write changes. Idempotent.
Skips: Amazon affiliate guides, thank-you pages, and any path listed in
.sidebar-skip-modified.txt (git status --porcelain format or one path per line).
"""
import json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AMAZON = {
    "guides/best-asphalt-driveway-sealer-top-products-for-2026/index.html",
    "guides/best-concrete-driveway-sealer-penetrating-vs-film-forming/index.html",
    "guides/driveway-crack-filler-best-products-reviewed-for-2026/index.html",
    "guides/pressure-washing-your-driveway-best-practices/index.html",
}
STATES = ["alabama","alaska","arizona","arkansas","california","colorado","connecticut","delaware",
    "florida","georgia","hawaii","idaho","illinois","indiana","iowa","kansas","kentucky","louisiana",
    "maine","maryland","massachusetts","michigan","minnesota","mississippi","missouri","montana",
    "nebraska","nevada","new-hampshire","new-jersey","new-mexico","new-york","north-carolina",
    "north-dakota","ohio","oklahoma","oregon","pennsylvania","rhode-island","south-carolina",
    "south-dakota","tennessee","texas","utah","vermont","virginia","washington","west-virginia",
    "wisconsin","wyoming"]
STATE_MAP_PATH = os.path.join(ROOT, "scripts", "sidebar_state_map.json")
REPORT_PATH = os.path.join(ROOT, "scripts", "migrate_sidebar_forms_report.md")

FORM_RE = re.compile(r'(?P<indent>[ \t]*)<form\s+onsubmit="handleSidebarSubmit\((?:e|event)\)"\s*>(?P<body>.*?)</form>', re.S)
TEXTAREA_RE = re.compile(r'<textarea\b(?P<attrs>[^>]*)>\s*</textarea>', re.S)
FUNC_RES = [
    # single-line / one-statement-per-line variants, with optional trailing newline
    re.compile(r'[ \t]*function handleSidebarSubmit\s*\((?:e|event)\)\s*\{[^{}]*\}[ \t]*\n?', re.S),
]
SEO_TAG = '<script src="/js/seo.js?v=8"></script>'
LEAD_TAG = '<script src="/js/lead-capture.js?v=1" defer></script>'
EMPTY_SCRIPT_RE = re.compile(r'[ \t]*<script>\s*</script>[ \t]*\n?')


USPS = {"al":"Alabama","ak":"Alaska","az":"Arizona","ar":"Arkansas","ca":"California","co":"Colorado",
    "ct":"Connecticut","de":"Delaware","dc":"District of Columbia","fl":"Florida","ga":"Georgia","hi":"Hawaii",
    "id":"Idaho","il":"Illinois","in":"Indiana","ia":"Iowa","ks":"Kansas","ky":"Kentucky","la":"Louisiana",
    "me":"Maine","md":"Maryland","ma":"Massachusetts","mi":"Michigan","mn":"Minnesota","ms":"Mississippi",
    "mo":"Missouri","mt":"Montana","ne":"Nebraska","nv":"Nevada","nh":"New Hampshire","nj":"New Jersey",
    "nm":"New Mexico","ny":"New York","nc":"North Carolina","nd":"North Dakota","oh":"Ohio","ok":"Oklahoma",
    "or":"Oregon","pa":"Pennsylvania","ri":"Rhode Island","sc":"South Carolina","sd":"South Dakota",
    "tn":"Tennessee","tx":"Texas","ut":"Utah","vt":"Vermont","va":"Virginia","wa":"Washington",
    "wv":"West Virginia","wi":"Wisconsin","wy":"Wyoming"}
CITY_RE = re.compile(r'-in-[a-z0-9-]+-(?P<st>[a-z]{2})-how-to-choose$')
# Multi-state slugs: leave untagged rather than pick one state.
MULTI_STATE = {"desert-driveways-new-mexico-and-arizona-tips"}


def detect_state(slug):
    if slug in MULTI_STATE:
        return None
    m = CITY_RE.search(slug)
    if m and m.group("st") in USPS:
        return USPS[m.group("st")]
    tokens = "-" + slug + "-"
    for st in sorted(STATES, key=len, reverse=True):
        if "-" + st + "-" in tokens:
            if st == "virginia" and "-west-virginia-" in tokens:
                continue
            if st == "washington" and ("-dc-" in tokens or "-d-c-" in tokens):
                return None
            return " ".join(w.capitalize() for w in st.split("-"))
    return None


def read_skip_modified():
    path = os.path.join(ROOT, ".sidebar-skip-modified.txt")
    out = set()
    if not os.path.exists(path):
        return out, False
    for line in open(path):
        line = line.rstrip("\n")
        if not line.strip():
            continue
        p = line[3:] if re.match(r'^[ MADRCU?!]{2} ', line) else line.strip()
        if " -> " in p:
            p = p.split(" -> ")[-1]
        p = p.strip().strip('"')
        if p.endswith("/"):
            p += "index.html"
        out.add(p)
    return out, True


def new_form(indent, body, state):
    ta = TEXTAREA_RE.search(body)
    i2 = indent + "  "
    attrs = ' data-lead-form="guide-sidebar"'
    if state:
        attrs += ' data-page-state="%s"' % state
    lines = [
        indent + '<form%s novalidate>' % attrs,
        i2 + '<input type="text" name="name" placeholder="Your Name" required aria-label="Your Name" autocomplete="name">',
        i2 + '<input type="tel" name="phone" placeholder="Phone Number" required aria-label="Phone Number" autocomplete="tel">',
        i2 + '<input type="text" name="zip" placeholder="ZIP Code" required aria-label="ZIP Code" autocomplete="postal-code" inputmode="numeric" pattern="\\d{5}" maxlength="5">',
        i2 + '<input type="email" name="email" placeholder="Email (optional)" aria-label="Email (optional)" autocomplete="email">',
    ]
    if ta:
        a = ta.group("attrs")
        if 'name=' not in a:
            a = ' name="message"' + a
        lines.append(i2 + '<textarea%s></textarea>' % a)
    lines += [
        i2 + '<div class="lead-hp" style="position:absolute;left:-9999px;width:1px;height:1px;overflow:hidden;" aria-hidden="true">',
        i2 + '  <label>Leave this field empty <input type="text" name="hp_ref" tabindex="-1" autocomplete="new-password" readonly></label>',
        i2 + '</div>',
        i2 + '<button type="submit">Request Free Estimate</button>',
        i2 + '<p class="lead-consent">By submitting, you agree Drivewayz USA and local driveway pros may contact you about your project. See our <a href="/privacy-policy/">Privacy Policy</a>.</p>',
        indent + '</form>',
    ]
    return "\n".join(lines)


def migrate(text, state):
    forms = list(FORM_RE.finditer(text))
    if len(forms) != 1:
        return None, "expected 1 sidebar form, found %d" % len(forms)
    m = forms[0]
    out = text[:m.start()] + new_form(m.group("indent"), m.group("body"), state) + text[m.end():]
    n_func = 0
    for rx in FUNC_RES:
        out, n = rx.subn("", out)
        n_func += n
    if n_func != 1:
        return None, "expected 1 handleSidebarSubmit function, removed %d" % n_func
    out = EMPTY_SCRIPT_RE.sub("", out)
    if "handleSidebarSubmit" in out:
        return None, "handleSidebarSubmit still present after edits"
    if out.count(SEO_TAG) != 1:
        return None, "expected 1 seo.js tag, found %d" % out.count(SEO_TAG)
    if LEAD_TAG not in out:
        idx = out.index(SEO_TAG)
        line_start = out.rfind("\n", 0, idx) + 1
        indent = out[line_start:idx] if out[line_start:idx].strip() == "" else ""
        out = out[:line_start] + indent + LEAD_TAG + "\n" + out[line_start:]
    return out, None


def main():
    apply = "--apply" in sys.argv
    skip_mod, have_skip_file = read_skip_modified()
    files = []
    for dp, dn, fn in os.walk(ROOT):
        dn[:] = [d for d in dn if not d.startswith(".") and d != "node_modules"]
        for f in fn:
            if f.endswith(".html"):
                p = os.path.relpath(os.path.join(dp, f), ROOT)
                with open(os.path.join(ROOT, p), encoding="utf-8") as fh:
                    if "handleSidebarSubmit" in fh.read():
                        files.append(p)
    files.sort()
    skipped = {"amazon": [], "thank-you": [], "pre-modified": [], "failed-to-match": []}
    changed, state_tagged, state_map = [], [], {}
    for p in files:
        if p in AMAZON:
            skipped["amazon"].append(p); continue
        if os.path.basename(os.path.dirname(p)).startswith("thank-you") or os.path.basename(p).startswith("thank-you"):
            skipped["thank-you"].append(p); continue
        if p in skip_mod:
            skipped["pre-modified"].append(p); continue
        slug = os.path.basename(os.path.dirname(p))
        state = detect_state(slug)
        src = open(os.path.join(ROOT, p), encoding="utf-8").read()
        out, err = migrate(src, state)
        if err:
            skipped["failed-to-match"].append("%s (%s)" % (p, err)); continue
        changed.append(p)
        if state:
            state_tagged.append(p); state_map[slug] = state
        if apply:
            with open(os.path.join(ROOT, p), "w", encoding="utf-8") as fh:
                fh.write(out)
    lines = ["# Sidebar form migration report", "",
             "Mode: %s" % ("apply" if apply else "dry run"),
             "Skip file .sidebar-skip-modified.txt: %s (%d paths)" % ("found" if have_skip_file else "NOT FOUND", len(skip_mod)), "",
             "- Files with handleSidebarSubmit: %d" % len(files),
             "- Migrated: %d" % len(changed),
             "- State-tagged: %d" % len(state_tagged),
             "- Skipped: %d" % sum(len(v) for v in skipped.values()), ""]
    for k, v in skipped.items():
        lines.append("## Skipped: %s (%d)" % (k, len(v)))
        lines += ["- " + x for x in v] or ["- none"]
        lines.append("")
    report = "\n".join(lines)
    print(report)
    if apply:
        with open(REPORT_PATH, "w") as fh:
            fh.write(report + "\n")
        with open(STATE_MAP_PATH, "w") as fh:
            json.dump(dict(sorted(state_map.items())), fh, indent=2)
            fh.write("\n")


if __name__ == "__main__":
    main()
