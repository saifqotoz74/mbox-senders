# mbox-senders

Triage a flood of unwanted email from an exported mailbox. It counts messages per sender domain and per day, shows which domains drove the busiest days, and prints a Gmail search (`from:(a.com OR b.com)`) you can paste to select the flood. Read-only: it never deletes or sends anything. Python 3 standard library only.

**Problem (Reddit):** [Woke up to someone signing me up for 500 foreign spam accounts using my email](https://www.reddit.com/r/techsupport/comments/1y3qbhr/) (r/techsupport). The poster needs to see who is sending the flood and how to filter it.

## Use
Export your mail (Gmail: Google Takeout, Mail, `.mbox`) or save messages as `.eml` files into a folder.
```
python3 mbox_senders.py All-mail.mbox
python3 mbox_senders.py ./eml-folder --top 30 --min-count 5
```
Review the suggested Gmail search before deleting anything: it matches every message from those domains, including real ones. A mail flood is often sign-up confirmations sent by real services, so filtering by sender domain is more reliable than by address.

## Test
`python3 -m unittest -v`
