"""Render README.md from data/banned_users.json so numbers never drift."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "banned_users.json"

BAR_WIDTH = 24
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def bar(count: int, peak: int) -> str:
    filled = max(1, round(count / peak * BAR_WIDTH)) if peak else 0
    return "█" * filled + "░" * (BAR_WIDTH - filled)


def md(text: str) -> str:
    """Escape pipe so a reason never breaks a markdown table cell."""
    return text.replace("|", "\\|")


def clamp(text: str, limit: int = 70) -> str:
    text = md(text)
    return text if len(text) <= limit else text[: limit - 1].rstrip(" ·,;") + "…"


def plural(n: int, one: str, few: str, many: str) -> str:
    """Russian plural form for n."""
    if n % 10 == 1 and n % 100 != 11:
        return one
    if n % 10 in (2, 3, 4) and n % 100 not in (12, 13, 14):
        return few
    return many


def short_date(iso: str) -> str:
    try:
        y, m, _ = iso.split("-")
    except ValueError:
        return iso
    return f"{MONTHS[int(m) - 1]} {y}"


def main() -> None:
    payload = json.loads(DATA.read_text(encoding="utf-8"))
    rows: list[dict] = payload["users"]
    src = payload["source"]

    total = len(rows)
    cats = Counter(r["category"] for r in rows).most_common()
    peak = cats[0][1] if cats else 0
    new = sum(1 for r in rows if r["already_in_public_blacklist"] == "no")
    known = total - new
    with_username = sum(1 for r in rows if r["username"])
    repeat = sum(1 for r in rows if r["mentions"] > 1)
    mentions = sum(r["mentions"] for r in rows)
    dates = sorted(r["first_seen"] for r in rows if r["first_seen"])
    period = f"{short_date(dates[0])} → {short_date(dates[-1])}" if dates else "—"
    badge_period = f"{short_date(dates[0])}%20to%20{short_date(dates[-1])}".replace(" ", "%20") if dates else "n%2Fa"

    top = sorted(rows, key=lambda r: (-r["mentions"], r["telegram_id"]))[:15]
    top_rows = "\n".join(
        f"| [{r['telegram_id']}](https://t.me/user?id={r['telegram_id']}) | "
        f"{r['username'] or '—'} | {r['mentions']} | {r['category']} | {clamp(r['reason'])} |"
        for r in top
    )

    cat_rows = "\n".join(
        f"| {name} | {count} | `{bar(count, peak)}` | {count / total * 100:.0f}% |"
        for name, count in cats
    )

    readme = f"""<div align="center">

# RemnaShop Banned Users

**Публичный реестр Telegram ID, заблокированных за абуз, шаринг и скам.**
Собран из темы «{src['topic']}» чата Remnashop.

[![IDs](https://img.shields.io/badge/Telegram%20IDs-{total}-2CA5E0?style=for-the-badge&logo=telegram&logoColor=white)](telegram_ids.csv)
[![New](https://img.shields.io/badge/New-{new}-37D67A?style=for-the-badge)](telegram_ids.csv)
[![Period](https://img.shields.io/badge/{badge_period}-555?style=for-the-badge)](data/banned_users.json)
[![License](https://img.shields.io/badge/License-MIT-black?style=for-the-badge)](LICENSE)

[**CSV**](telegram_ids.csv) · [Plain TXT](telegram_ids_plain.txt) · [Blacklist TXT](telegram_ids.txt) · [Расширенная таблица](banned_users.csv) · [JSON](data/banned_users.json)

</div>

---

## Что это

Готовый список для бан-листа в Remnawave / Remnashop и любой другой панели: один Telegram ID на строку, по возрастанию, без дублей. Причины и даты — в расширенной таблице, чтобы не банить вслепую.

| Файл | Назначение |
|---|---|
| **[`telegram_ids.csv`](telegram_ids.csv)** | Главное. Одна колонка `telegram_id`, {total} {plural(total, 'строка', 'строки', 'строк')}. Импорт куда угодно. |
| **[`telegram_ids_plain.txt`](telegram_ids_plain.txt)** | Голый список: только цифры, по одной на строку. Без заголовка и без комментариев — для панелей, которые не переваривают ничего лишнего. |
| **[`telegram_ids.txt`](telegram_ids.txt)** | Тот же список в формате Remnashop blacklist: `id # причина`. Дроп-ин для существующего реестра. |
| **[`banned_users.csv`](banned_users.csv)** | Расширенная таблица: username, первое/последнее упоминание, число упоминаний, категория, источник причины. |
| **[`data/banned_users.json`](data/banned_users.json)** | То же в JSON — для скриптов и ботов. |

```bash
curl -sL https://raw.githubusercontent.com/Demyasha-An/RemnaShop-Banned-Users/main/telegram_ids_plain.txt \\
  | head -4
```

```
232953109
274236436
308418118
376334438
```

## Цифры

| Метрика | Значение |
|---|---:|
| Уникальных Telegram ID | **{total}** |
| Упоминаний в чате | {mentions} |
| Уже были в публичном [remnashop/blacklist](https://github.com/remnashop/blacklist) | {known} |
| Новых, которых там нет | **{new}** |
| С указанным `@username` | {with_username} |
| Засветились больше одного раза | {repeat} |
| Период обсуждения | {dates[0] if dates else '—'} → {dates[-1] if dates else '—'} |

### Категории нарушений

| Категория | ID | Распределение | Доля |
|---|---:|---|---:|
{cat_rows}

## Кто в списке чаще всех

| Telegram ID | Username | Упоминаний | Категория | Причина |
|---|---|---:|---|---|
{top_rows}

## Как этим пользоваться

<details>
<summary><b>Remnawave / Remnashop</b></summary>

Импорт блеклиста: вставьте содержимое `telegram_ids.txt` целиком. Если нужен голый список без комментариев — берите `telegram_ids_plain.txt`. Если ваша версия панели умеет тянуть по URL — используйте raw-ссылку:

```
https://raw.githubusercontent.com/Demyasha-An/RemnaShop-Banned-Users/main/telegram_ids.txt
```
</details>

<details>
<summary><b>Свой бот или скрипт</b></summary>

```python
import csv, io, urllib.request

URL = "https://raw.githubusercontent.com/Demyasha-An/RemnaShop-Banned-Users/main/telegram_ids.csv"
raw = urllib.request.urlopen(URL).read().decode()
banned = {{int(r["telegram_id"]) for r in csv.DictReader(io.StringIO(raw))}}

if user_id in banned:
    ...  # отказать / забанить
```
</details>

<details>
<summary><b>Объединить со своим списком</b></summary>

```bash
# только те ID, которых нет в этом реестре
comm -23 <(sort -u мой_список.txt) <(sort -u telegram_ids_plain.txt) > новые.txt
```
</details>

## Откуда данные

Экспорт Telegram Desktop темы «{src['topic']}»: **{src['export_first']} → {src['export_last']}**.

ID вытащены из текста сообщений регуляркой по границам числа (6–11 цифр). Вырезано лишнее:

- ссылки `t.me/c/<chat>/<thread>/<msg>` — это id чатов, тредов и сообщений, а не пользователей;
- `@username` и e-mail;
- хештеги, цены, номера сообщений и прочие числа вне контекста ID.

Проверка сошлась: все {total} ID есть в тексте темы, и ни одно число из экспорта не потерялось незамеченным — кроме перечисленных категорий мусора и id самого чата.

Причины взяты из того же сообщения. Для «дампов» из одних ID — из сообщения, на которое отвечали, либо из предыдущего сообщения с причиной от того же автора. Где причины не было — так и написано, ничего не додумано.

### Столбцы `banned_users.csv`

| Столбец | Смысл |
|---|---|
| `telegram_id` | Числовой ID пользователя |
| `username` | `@username`, если он был в том же сообщении |
| `first_seen` / `last_seen` | Первое и последнее упоминание |
| `mentions` | Сколько раз ID встречался в чате |
| `category` | Категория нарушения |
| `already_in_public_blacklist` | `yes`, если ID уже есть в remnashop/blacklist |
| `reason_source` | `указана в сообщении` / `по контексту обсуждения` / `не указана` |
| `reason` | Причина как её написал автор |
| `message_ids` | Номера сообщений в экспорте — для проверки |

## Оговорки

- Это **не приговор**, а сигнал: список собран из сообщений участников чата, часть причин — со слов заказчиков.
- ID числовые. Username меняется, числовой ID — нет.
- Ложные срабатывания бывают: если ваш ID здесь по ошибке — [откройте issue](../../issues/new?template=appeal.yml).
- В списке только пользователи. ID чатов, каналов и групп отфильтрованы.

## Добавить нарушителя

[Форма заявки](../../issues/new?template=ban-request.yml): **числовой Telegram ID**, категория, причина и подтверждение (скриншот, лог, ссылка). Без подтверждения не добавляем.

## Пересобрать список

```bash
python scripts/build.py "путь/к/messages.html" --out .                 # только свои файлы
python scripts/build.py "путь/к/messages.html" --out . --known bl.txt  # сверить с внешним блеклистом
python scripts/render_readme.py
python scripts/validate.py
```
`scripts/build.py` детерминированный: одинаковый экспорт всегда даёт одинаковые файлы. CI проверяет, что `telegram_ids.csv`, `telegram_ids_plain.txt`, `telegram_ids.txt` и `banned_users.csv` не разъехались.

## Лицензия

[MIT](LICENSE). Берите, форкайте, встраивайте в свои панели.
"""

    (ROOT / "README.md").write_text(readme, encoding="utf-8")
    print(f"README.md: {total} ids, {len(cats)} categories")


if __name__ == "__main__":
    main()
