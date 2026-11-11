<div align="center">

# RemnaShop Banned Users

**Публичный реестр Telegram ID, заблокированных за абуз, шаринг и скам.**
Собран из темы «Черный список» чата Remnashop.

[![IDs](https://img.shields.io/badge/Telegram%20IDs-593-2CA5E0?style=for-the-badge&logo=telegram&logoColor=white)](telegram_ids.csv)
[![New](https://img.shields.io/badge/New-558-37D67A?style=for-the-badge)](telegram_ids.csv)
[![Period](https://img.shields.io/badge/Aug%202026%20-%20Nov%202026-555?style=for-the-badge)](data/banned_users.json)
[![License](https://img.shields.io/badge/License-MIT-black?style=for-the-badge)](LICENSE)

[**CSV**](telegram_ids.csv) · [Blacklist TXT](telegram_ids.txt) · [Расширенная таблица](banned_users.csv) · [JSON](data/banned_users.json)

</div>

---

## Что это

Готовый список для бан-листа в Remnawave / Remnashop и любой другой панели: один Telegram ID на строку, по возрастанию, без дублей. Причины и даты — в расширенной таблице, чтобы не банить вслепую.

| Файл | Назначение |
|---|---|
| **[`telegram_ids.csv`](telegram_ids.csv)** | Главное. Одна колонка `telegram_id`, 593 строки. Импорт куда угодно. |
| **[`telegram_ids.txt`](telegram_ids.txt)** | Тот же список в формате Remnashop blacklist: `id # причина`. Дроп-ин для существующего реестра. |
| **[`banned_users.csv`](banned_users.csv)** | Расширенная таблица: username, первое/последнее упоминание, число упоминаний, категория, источник причины. |
| **[`data/banned_users.json`](data/banned_users.json)** | То же в JSON — для скриптов и ботов. |

```bash
curl -sL https://raw.githubusercontent.com/Demyasha-An/RemnaShop-Banned-Users/main/telegram_ids.csv \
  | head -5
```

```
telegram_id
232953109
274236436
308418118
376334438
```

## Цифры

| Метрика | Значение |
|---|---:|
| Уникальных Telegram ID | **593** |
| Упоминаний в чате | 739 |
| Уже были в публичном [remnashop/blacklist](https://github.com/remnashop/blacklist) | 35 |
| Новых, которых там нет | **558** |
| С указанным `@username` | 15 |
| Засветились больше одного раза | 135 |
| Период обсуждения | 2026-08-20 → 2026-11-11 |

### Категории нарушений

| Категория | ID | Распределение | Доля |
|---|---:|---|---:|
| Абуз триалов | 566 | `████████████████████████` | 95% |
| Скам и возвраты | 6 | `█░░░░░░░░░░░░░░░░░░░░░░░` | 1% |
| Шаринг подписки | 6 | `█░░░░░░░░░░░░░░░░░░░░░░░` | 1% |
| Причина не указана | 5 | `█░░░░░░░░░░░░░░░░░░░░░░░` | 1% |
| Неадекватное поведение | 5 | `█░░░░░░░░░░░░░░░░░░░░░░░` | 1% |
| Спам и реклама | 3 | `█░░░░░░░░░░░░░░░░░░░░░░░` | 1% |
| Подозрительный трафик | 2 | `█░░░░░░░░░░░░░░░░░░░░░░░` | 0% |

## Кто в списке чаще всех

| Telegram ID | Username | Упоминаний | Категория | Причина |
|---|---|---:|---|---|
| [8378800425](https://t.me/user?id=8378800425) | @pizdabolchikking | 4 | Абуз триалов | Абуз триала \| Абузеры триалок |
| [501825558](https://t.me/user?id=501825558) | — | 3 | Абуз триалов | абуз пробников \| Абуз триала |
| [5868345353](https://t.me/user?id=5868345353) | — | 3 | Абуз триалов | абуз пробников \| Абуз триала |
| [5979860592](https://t.me/user?id=5979860592) | — | 3 | Абуз триалов | Абуз триала \| Абузеры триалок |
| [6230709806](https://t.me/user?id=6230709806) | — | 3 | Абуз триалов | абуз пробников \| Абуз триала |
| [7463599871](https://t.me/user?id=7463599871) | — | 3 | Абуз триалов | абуз пробников \| Абуз триала |
| [7652993908](https://t.me/user?id=7652993908) | — | 3 | Абуз триалов | Абуз триала \| Абузеры триалок |
| [8629495322](https://t.me/user?id=8629495322) | — | 3 | Абуз триалов | абуз пробников \| Абуз триала |
| [8675344936](https://t.me/user?id=8675344936) | — | 3 | Абуз триалов | абуз пробников \| Абуз триала |
| [8740021830](https://t.me/user?id=8740021830) | — | 3 | Абуз триалов | Абуз триала \| Абузеры триалок |
| [399850197](https://t.me/user?id=399850197) | — | 2 | Подозрительный трафик | Hossein · 2,41 ТБ за 2 дня |
| [516613509](https://t.me/user?id=516613509) | — | 2 | Абуз триалов | Абуз триала |
| [758569282](https://t.me/user?id=758569282) | — | 2 | Абуз триалов | дважды покупает впн, не может разобраться и просит возврат, даже не н… |
| [1216074066](https://t.me/user?id=1216074066) | — | 2 | Абуз триалов | Абуз триала |
| [1289525834](https://t.me/user?id=1289525834) | — | 2 | Абуз триалов | Абуз триала |

## Как этим пользоваться

<details>
<summary><b>Remnawave / Remnashop</b></summary>

Импорт блеклиста: вставьте содержимое `telegram_ids.txt` целиком. Если ваша версия панели умеет тянуть по URL — используйте raw-ссылку:

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
banned = {int(r["telegram_id"]) for r in csv.DictReader(io.StringIO(raw))}

if user_id in banned:
    ...  # отказать / забанить
```
</details>

<details>
<summary><b>Объединить со своим списком</b></summary>

```bash
# только те ID, которых нет в этом реестре
comm -23 <(sort -u мой_список.txt) <(tail -n +2 telegram_ids.csv | sort -u) > новые.txt
```
</details>

## Откуда данные

Экспорт Telegram Desktop темы «Черный список»: **2026-08-19 → 2026-11-12**.

ID вытащены из текста сообщений регуляркой по границам числа (6–11 цифр). Вырезано лишнее:

- ссылки `t.me/c/<chat>/<thread>/<msg>` — это id чатов, тредов и сообщений, а не пользователей;
- `@username` и e-mail;
- хештеги, цены, номера сообщений и прочие числа вне контекста ID.

Проверка сошлась: все 593 ID есть в тексте темы, и ни одно число из экспорта не потерялось незамеченным — кроме перечисленных категорий мусора и id самого чата.

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
`scripts/build.py` детерминированный: одинаковый экспорт всегда даёт одинаковые файлы. CI проверяет, что `telegram_ids.csv`, `telegram_ids.txt` и `banned_users.csv` не разъехались.

## Лицензия

[MIT](LICENSE). Берите, форкайте, встраивайте в свои панели.
