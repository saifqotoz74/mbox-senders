import os, tempfile, unittest
import mbox_senders as m

def eml(frm, date, n=0):
    return "From: %s\nTo: me@x.com\nSubject: s%d\nDate: %s\n\nbody\n" % (frm, n, date)

class T(unittest.TestCase):
    def folder(self):
        d = tempfile.mkdtemp()
        items = [("Shop <no-reply@spam.example>", "Mon, 23 Nov 2026 10:00:00 +0000")] * 4 + [("a@news.example", "Mon, 23 Nov 2026 11:00:00 +0000"), ("Bob <bob@friend.org>", "Tue, 24 Nov 2026 09:00:00 +0000")]
        for i, (f, dt) in enumerate(items):
            open(os.path.join(d, "%d.eml" % i), "w").write(eml(f, dt, i))
        return d

    def test_eml_folder(self):
        r = m.analyze(self.folder())
        self.assertEqual(r["total"], 6)
        self.assertEqual(r["domains"]["spam.example"], 4)
        self.assertEqual(r["days"]["2026-11-23"], 5)
        self.assertEqual(r["by_day"]["2026-11-23"]["spam.example"], 4)

    def test_mbox(self):
        p = os.path.join(tempfile.mkdtemp(), "x.mbox")
        with open(p, "w") as f:
            for i in range(3):
                f.write("From MAILER-DAEMON Mon Nov 23 10:00:00 2026\n" + eml("x@a.test", "Mon, 23 Nov 2026 10:00:00 +0000", i) + "\n")
        r = m.analyze(p)
        self.assertEqual((r["total"], r["domains"]["a.test"]), (3, 3))

    def test_missing_headers(self):
        d = tempfile.mkdtemp()
        open(os.path.join(d, "a.eml"), "w").write("Subject: hi\n\nbody\n")
        r = m.analyze(d)
        self.assertEqual(r["domains"]["(unknown)"], 1)
        self.assertEqual(r["days"]["(no date)"], 1)

    def test_query_and_main(self):
        self.assertEqual(m.gmail_query(["a.com", "b.org"]), "from:(a.com OR b.org)")
        self.assertEqual(m.main([self.folder()]), 0)

if __name__ == "__main__":
    unittest.main()
