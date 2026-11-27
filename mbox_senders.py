#!/usr/bin/env python3
"""mbox-senders: triage a flood of unwanted email from an exported mailbox.

Reads an .mbox file (Gmail: Google Takeout > Mail) or a folder of .eml files and shows
how many messages came from each sender domain and each day, so you can see the burst
and build filters. Prints a Gmail search you can paste to select the flood.
Nothing is deleted or sent; it only reads.
"""
import argparse
import collections
import email.utils
import mailbox
import os
import sys
from email import policy
from email.parser import BytesParser


def messages(path):
    if os.path.isdir(path):
        for f in sorted(os.listdir(path)):
            if f.lower().endswith(".eml"):
                with open(os.path.join(path, f), "rb") as fh:
                    yield BytesParser(policy=policy.default).parse(fh)
    else:
        for m in mailbox.mbox(path):
            yield m


def info(msg):
    addr = email.utils.parseaddr(str(msg.get("From", "")))[1].lower()
    domain = addr.rsplit("@", 1)[1] if "@" in addr else "(unknown)"
    day = "(no date)"
    try:
        d = email.utils.parsedate_to_datetime(str(msg.get("Date", "")))
        day = d.date().isoformat()
    except (TypeError, ValueError):
        pass
    return addr or "(unknown)", domain, day


def analyze(path):
    addrs, domains, days = collections.Counter(), collections.Counter(), collections.Counter()
    pair = collections.defaultdict(collections.Counter)  # day -> domain counts
    total = 0
    for m in messages(path):
        a, d, day = info(m)
        addrs[a] += 1; domains[d] += 1; days[day] += 1; pair[day][d] += 1
        total += 1
    return {"total": total, "addresses": addrs, "domains": domains, "days": days, "by_day": pair}


def gmail_query(domains):
    return "from:(" + " OR ".join(domains) + ")" if domains else ""


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("source", help=".mbox file or folder of .eml files")
    ap.add_argument("--top", type=int, default=15)
    ap.add_argument("--min-count", type=int, default=3, help="domains with at least this many messages go in the suggested search")
    a = ap.parse_args(argv)
    r = analyze(a.source)
    print("messages: %d, sender domains: %d" % (r["total"], len(r["domains"])))
    print("\nTop sender domains:")
    for k, v in r["domains"].most_common(a.top):
        print("  %5d  %s" % (v, k))
    print("\nBusiest days:")
    for k, v in r["days"].most_common(5):
        top = ", ".join("%s (%d)" % kv for kv in r["by_day"][k].most_common(3))
        print("  %5d  %s   %s" % (v, k, top))
    flood = [d for d, c in r["domains"].most_common() if c >= a.min_count and d != "(unknown)"]
    print("\nGmail search for domains with %d+ messages (review before deleting):" % a.min_count)
    print("  " + (gmail_query(flood[:40]) or "(none)"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
