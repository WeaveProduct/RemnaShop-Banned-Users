"""Parse a Telegram Desktop HTML chat export and extract banned Telegram user IDs.

Usage:
    python scripts/build.py "<path to messages.html>" --out .

Produces in --out:
    telegram_ids.csv    - single column, telegram_id only (main deliverable)
    telegram_ids.txt    - "id # reason", drop-in for Remnashop blacklist
    banned_users.csv    - enriched table
    data/banned_users.json
"""

from __future__ import annotations

import argparse
import csv
import html
import json
import re
from collections import Counter, OrderedDict
from pathlib import Path

# ---------------------------------------------------------------- cleaning ---

URL_RE = re.compile(r'(?:https?://|www\.)\S+', re.I)
TME_RE = re.compile(r'\bt\.me/\S+', re.I)
EMAIL_RE = re.compile(r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}')
MENTION_RE = re.compile(r'@[A-Za-z0-9_]{3,}')
HASHTAG_RE = re.compile(r'#[A-Za-z0-9_]+')
ID_RE = re.compile(r'(?<!\d)(\d{6,11})(?!\d)')
BULLET_RE = re.compile(r'^\s*[•\-\*·]\s*', re.M)
LABEL_INLINE_RE = re.compile(r'\b(?:ID|Имя|Трафик|Username|User|TG ID|Telegram ID|TG|tg)\s*:\s*', re.I)
LABEL_ONLY_RE = re.compile(r'^(?:ID|Имя|Трафик|Username|User|TG ID|Telegram ID|TG|tg)\s*:?\s*$', re.I)
NAME_LINE_RE = re.compile(r'^(?:Имя|Name|Username|User|Ник|Никнейм)\s*:\s*\S', re.I)
# phrases that are reactions, not reasons: they get inherited from context instead
NON_REASON_RE = re.compile(
    r'^(?:комментарии излишни|и так понятно\w*|ну если что\b.*|'
    r'\+{2,}|ахах\w*|лол\w*|это триалки\?|и так понятно все)\W*$',
    re.I)
# bot notifications that mention a user but state no violation
BOT_EVENT_RE = re.compile(
    r'(?:Событие:|UserRegisteredEvent|Новый пользователь|Пользовател[ья]:|'
    r'Подписка|Оплата|Платёж|Транзакция)', re.I)
DATE_RE = re.compile(r'(\d{2})\.(\d{2})\.(\d{4})')

# Ids in this topic are often posted as bare dumps under a "reason" message.
# Such a dump inherits the reason of the message it replies to; anything else
# stays explicitly unknown instead of being guessed.
def is_id_dump(text: str) -> bool:
    """True when a message is nothing but ids/links/mentions."""
    rest = TME_RE.sub(' ', URL_RE.sub(' ', text))
    rest = ID_RE.sub(' ', rest)
    rest = EMAIL_RE.sub(' ', rest)
    rest = MENTION_RE.sub(' ', rest)
    rest = HASHTAG_RE.sub(' ', rest)
    return not re.search(r'\w', rest)

CATEGORIES = [
    ("Абуз триалов", r'триал|абуз|пробник'),
    ("Шаринг подписки", r'шейр|шаринг|шара|раздач|раздаёт|раздает|раздача|слив ключ'),
    ("Скам и возвраты", r'скам|мошен|чарджбэк|возврат|слит|угроз'),
    ("Спам и реклама", r'реклам|рассылк|накруч|спам|копипаст|бот'),
    ("Неадекватное поведение", r'\bмат\b|неадекват|еблан|хуесос'),
    ("Подозрительный трафик", r'трафик|тб\b|\bip\b|hwid'),
]
NO_REASON = "Причина не указана"
OTHER = "Прочее"


def parse_iso(date: str | None) -> str:
    if not date:
        return ""
    m = DATE_RE.search(date)
    return f"{m.group(3)}-{m.group(2)}-{m.group(1)}" if m else ""


def clean_reason(text: str) -> str:
    """Message text with ids/links/mentions stripped -> short human readable reason."""
    # links first: t.me/c/<chat>/<thread>/<msg> would otherwise leave id fragments behind
    t = URL_RE.sub(' ', text)
    t = ID_RE.sub(' ', t)
    t = EMAIL_RE.sub(' ', t)
    t = MENTION_RE.sub(' ', t)
    t = HASHTAG_RE.sub(' ', t)
    t = LABEL_INLINE_RE.sub(' ', t)
    t = BULLET_RE.sub('', t)
    lines: list[str] = []
    for line in t.split('\n'):
        line = re.sub(r'[\s\u00a0\u200b\ufeff]+', ' ', line)
        line = re.sub(r'\(\s*[,;:]?\s*\)', '', line)          # empty parens left by stripped links
        line = re.sub(r'^(?:[•\-\*·]|\d+[.)])\s*', '', line)
        line = line.strip(' :;,.-–—·')
        line = re.sub(r'\s*\(\s*$', '', line).strip(' :;,.-–—·')
        if not line or LABEL_ONLY_RE.match(line) or NAME_LINE_RE.match(line):
            continue
        if line not in lines:
            lines.append(line)
    reason = re.sub(r'\s*·\s*(?:·\s*)+', ' · ', ' · '.join(lines)).strip(' ·')
    if NON_REASON_RE.match(reason):
        return ""
    if BOT_EVENT_RE.search(reason) and "абуз" not in reason.lower():
        return ""
    # a bare "Срочный бан:" style label carries no information
    if re.fullmatch(r'(?:срочный бан|бан|в бан|забанить)\W*', reason, re.I):
        return ""
    if len(reason) > 200:
        reason = reason[:197].rstrip(' ·,;') + '…'
    return reason


def categorize(reason: str, source: str = "") -> str:
    if source == "не указана":
        return NO_REASON
    low = reason.lower()
    for name, pattern in CATEGORIES:
        if re.search(pattern, low):
            return name
    return NO_REASON if not reason else OTHER


# ------------------------------------------------------------------ parser ---

def strip_tags(s: str) -> str:
    s = re.sub(r'<br\s*/?>', '\n', s)
    s = re.sub(r'<[^>]+>', '', s)
    return html.unescape(s).strip()


def parse_export(raw: str) -> list[dict]:
    """Telegram Desktop export: one <div class="message ..."> per message.

    Messages with class "... joined" carry no from_name: they continue the
    previous author, so the author is inherited here.
    """
    msgs = []
    last_author = ""
    for frag in re.split(r'(?=<div class="message )', raw):
        m = re.match(r'<div class="message ([^"]*)" id="(message-?\d+)">', frag)
        if not m:
            continue
        fn = re.search(r'<div class="from_name">\s*(.*?)\s*</div>', frag, re.S)
        dt = re.search(r'<div class="pull_right date details" title="([^"]*)"', frag)
        tx = re.search(r'<div class="text">\s*(.*?)\s*</div>\s*(?:<span class="reactions|</div>)', frag, re.S)
        if not tx:
            tx = re.search(r'<div class="text">\s*(.*?)\s*</div>', frag, re.S)
        if not tx:
            # rich messages (bot output with headings/quotes) live in another block
            tx = re.search(r'<div class="text rich_message"[^>]*>\s*(.*?)</div>', frag, re.S)
        has_photo = 'media_photo' in frag
        reply = re.search(r'In reply to <a href="#go_to_message(\d+)"', frag)
        author = html.unescape(fn.group(1)).strip() if fn else ""
        if author:
            last_author = author
        elif "joined" in m.group(1).split():
            author = last_author
        msgs.append({
            "id": m.group(2),
            "cls": m.group(1),
            "author": author,
            "date": dt.group(1) if dt else "",
            "text": strip_tags(tx.group(1)) if tx else "",
            "reply_to": reply.group(1) if reply else "",
            "photo": has_photo,
        })
    return msgs


def export_meta(raw: str) -> dict:
    title = re.search(r'<div class="text bold">\s*(.*?)\s*</div>', raw[:4000], re.S)
    topic = re.search(r'created topic &laquo;(.*?)&raquo;', raw)
    dates = re.findall(r'<div class="pull_right date details" title="([^"]*)"', raw)
    return {
        "chat": html.unescape(title.group(1)).strip() if title else "",
        "topic": html.unescape(topic.group(1)).strip() if topic else "",
        "export_first": parse_iso(dates[0]) if dates else "",
        "export_last": parse_iso(dates[-1]) if dates else "",
    }


def iso_ts(date: str) -> int:
    """Rough sortable timestamp from 'dd.mm.yyyy HH:MM:SS GMT+10:00'."""
    m = re.search(r'(\d{2})\.(\d{2})\.(\d{4})\s+(\d{2}):(\d{2}):(\d{2})', date or "")
    if not m:
        return 0
    d, mo, y, h, mi, s = (int(x) for x in m.groups())
    return ((((y * 12 + mo) * 31 + d) * 24 + h) * 60 + mi) * 60 + s


# ------------------------------------------------------------------ main ----

def build(html_path: Path, out: Path, known: set[int] | None = None) -> dict:
    known = known or set()
    raw = html_path.read_text(encoding="utf-8")
    meta = export_meta(raw)
    msgs = parse_export(raw)

    # Reason per message: its own stated reason; for bare id dumps, the reason of
    # the replied-to message or that of the same author's previous stated dump.
    # Anything else stays explicitly "not stated" rather than guessed.
    def stated(text: str) -> str:
        r = clean_reason(text)
        return r if r and categorize(r) != NO_REASON else ""
    reason_of: dict[str, str] = {}
    source_of: dict[str, str] = {}
    for m in msgs:
        r = stated(m["text"])
        if r:
            reason_of[m["id"]], source_of[m["id"]] = r, "own"
    last_by_author: dict[str, str] = {}
    for m in msgs:
        mid = m["id"]
        if mid not in reason_of and is_id_dump(m["text"]):
            parent_id = "message" + m["reply_to"] if m["reply_to"] else ""
            if reason_of.get(parent_id):
                reason_of[mid], source_of[mid] = reason_of[parent_id], "thread"
            elif last_by_author.get(m["author"]):
                reason_of[mid], source_of[mid] = last_by_author[m["author"]], "author"
        if m["author"] and mid in reason_of:
            last_by_author[m["author"]] = reason_of[mid]

    ids: "OrderedDict[int, dict]" = OrderedDict()
    for m in msgs:
        text = m["text"]
        if not text:
            continue
        # deep-link chat/thread/message ids are not user ids
        searchable = TME_RE.sub(' ', URL_RE.sub(' ', text))
        found = list(dict.fromkeys(ID_RE.findall(searchable)))
        if not found:
            continue
        reason = reason_of.get(m["id"], "")
        users = [u.lstrip('@') for u in dict.fromkeys(MENTION_RE.findall(text))]
        date = parse_iso(m["date"])
        for raw_id in found:
            i = int(raw_id)
            rec = ids.setdefault(i, {"telegram_id": i, "username": "", "first_seen": date,
                                     "last_seen": date, "mentions": 0, "reasons": [],
                                     "message_reasons": [], "messages": []})
            rec["mentions"] += 1
            if date:
                rec["first_seen"] = min(filter(None, [rec["first_seen"], date]))
                rec["last_seen"] = max(filter(None, [rec["last_seen"], date]))
            if reason and reason not in rec["reasons"]:
                rec["reasons"].append(reason)
            src = source_of.get(m["id"], "none")
            if src not in rec["message_reasons"]:
                rec["message_reasons"].append(src)
            if m["id"] not in rec["messages"]:
                rec["messages"].append(m["id"])
            if len(found) == 1 and len(users) == 1 and not rec["username"]:
                rec["username"] = users[0]

    rows = []
    for rec in sorted(ids.values(), key=lambda r: r["telegram_id"]):
        reason = " | ".join(rec["reasons"]) or "причина не указана"
        srcs = rec["message_reasons"]
        if "own" in srcs or "thread" in srcs:
            confidence = "указана в сообщении"
        elif "author" in srcs:
            confidence = "по контексту обсуждения"
        else:
            confidence = "не указана"
        rows.append({
            "telegram_id": rec["telegram_id"],
            "username": f"@{rec['username']}" if rec["username"] else "",
            "first_seen": rec["first_seen"],
            "last_seen": rec["last_seen"],
            "mentions": rec["mentions"],
            "category": categorize(reason, confidence),
            "already_in_public_blacklist": "yes" if rec["telegram_id"] in known else "no",
            "reason_source": confidence,
            "reason": reason,
            "message_ids": " ".join(m.replace("message", "") for m in rec["messages"]),
        })

    (out / "data").mkdir(parents=True, exist_ok=True)

    with (out / "telegram_ids.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["telegram_id"])
        for r in rows:
            w.writerow([r["telegram_id"]])

    # bare list: one id per line, no header, no comments — for panels that
    # reject anything but plain numbers
    with (out / "telegram_ids_plain.txt").open("w", encoding="utf-8", newline="\n") as f:
        for r in rows:
            f.write(f"{r['telegram_id']}\n")

    with (out / "telegram_ids.txt").open("w", encoding="utf-8", newline="\n") as f:
        for r in rows:
            f.write(f"{r['telegram_id']} # {r['reason'].replace(chr(10), ' ')}\n")

    cols = ["telegram_id", "username", "first_seen", "last_seen", "mentions",
            "category", "already_in_public_blacklist", "reason_source", "reason", "message_ids"]
    with (out / "banned_users.csv").open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols, lineterminator="\n")
        w.writeheader()
        for r in rows:
            w.writerow({**r, "reason": r["reason"].replace("\n", " ")})

    (out / "data" / "banned_users.json").write_text(
        json.dumps({"source": meta, "count": len(rows), "users": rows},
                   ensure_ascii=False, indent=1), encoding="utf-8")

    dates = [r["first_seen"] for r in rows if r["first_seen"]]
    stats = {
        "chat": meta["chat"],
        "topic": meta["topic"],
        "export_first": meta["export_first"],
        "export_last": meta["export_last"],
        "total": len(rows),
        "new": sum(1 for r in rows if r["already_in_public_blacklist"] == "no"),
        "known": sum(1 for r in rows if r["already_in_public_blacklist"] == "yes"),
        "with_username": sum(1 for r in rows if r["username"]),
        "with_reason": sum(1 for r in rows if r["reason_source"] != "не указана"),
        "mentions": sum(r["mentions"] for r in rows),
        "messages": len({m for r in rows for m in r["message_ids"].split()}),
        "first_date": min(dates) if dates else "",
        "last_date": max(dates) if dates else "",
        "categories": dict(Counter(r["category"] for r in rows).most_common()),
    }
    return stats


def load_known_blacklist(path: Path) -> set[int]:
    known: set[int] = set()
    if not path.exists():
        return known
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        head = re.split(r"[\s#]", line, maxsplit=1)[0].strip()
        if head.isdigit():
            known.add(int(head))
    return known


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("html", type=Path)
    ap.add_argument("--out", type=Path, default=Path("."))
    ap.add_argument("--known", type=Path, help="existing blacklist.txt to cross-reference")
    a = ap.parse_args()
    s = build(a.html, a.out, load_known_blacklist(a.known) if a.known else None)
    print(json.dumps(s, ensure_ascii=False, indent=1))
