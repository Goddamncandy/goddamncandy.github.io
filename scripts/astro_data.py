#!/usr/bin/env python3
"""Собрать данные астро-таро для сайта из трактовок Веры.

Источник — ../vera-life/methods/astro-tarot/traktovki.md (Вера правит и утверждает его, а не этот файл).
Выход — theme/assets/astro-data.js. Картинки карт — theme/assets/cards/<id>.webp, их кладёт --cards.

    scripts/astro_data.py            # пересобрать данные
    scripts/astro_data.py --cards    # и пережать картинки колоды из хранилища
"""
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT.parent / "vera-life" / "methods" / "astro-tarot" / "traktovki.md"
DECK = ROOT.parent / "vera-life" / "files" / "tarot" / "rider-waite"
OUT = ROOT / "theme" / "assets" / "astro-data.js"
CARDS = ROOT / "theme" / "assets" / "cards"

SUITS = {"жезлов": "wands", "кубков": "cups", "мечей": "swords", "пентаклей": "pentacles"}
COURT = {"Рыцарь": 12, "Королева": 13, "Король": 14}
MAJOR = {"Маг": 1, "Верховная Жрица": 2, "Императрица": 3, "Император": 4, "Иерофант": 5, "Влюблённые": 6,
         "Колесница": 7, "Сила": 8, "Отшельник": 9, "Колесо Фортуны": 10, "Справедливость": 11, "См*рть": 13,
         "Умеренность": 14, "Дьявол": 15, "Башня": 16, "Звезда": 17, "Луна": 18, "Солнце": 19, "Мир": 21}
NO_IMAGE = {"major-13", "major-15"}   # XIII и XV арканы никогда не показываются картинкой


def img(card_id):
    return None if card_id in NO_IMAGE else card_id


def section(text, title):
    m = re.search(rf"^## {re.escape(title)}\n(.*?)(?=^## |\Z)", text, re.S | re.M)
    if not m:
        sys.exit(f"нет раздела «{title}» в {SRC}")
    return m.group(1)


def entries(block):
    """Запись: **заголовок** (необязательно: скобки), строка текста, строка «Тень: …»."""
    out = []
    for m in re.finditer(r"^\*\*(.+?)\*\*(?: \(([^)]*)\))?\n(.+?)\nТень: (.+?)$", block, re.M):
        head, note, body, shadow = m.groups()
        shadow = shadow.strip()
        out.append((head, (note or "").replace("≈ ", ""), body.strip(), shadow[:1].upper() + shadow[1:]))
    return out


def main():
    text = SRC.read_text(encoding="utf-8")

    signs = []
    for head, _, body, shadow in entries(section(text, "1. Знак")):
        sign, arcanum = head.split(" · ")
        signs.append({"sign": sign, "arcanum": arcanum, "img": img(f"major-{MAJOR[arcanum]:02d}"),
                      "text": body, "shadow": shadow})

    planets, ruler = {}, {}
    for head, note, body, shadow in entries(section(text, "2. Покровитель знака")):
        planet, arcanum = head.split(" · ")
        planets[planet] = {"arcanum": arcanum, "img": img(f"major-{MAJOR[arcanum]:02d}"), "text": body, "shadow": shadow}
        for sign in note.split(", "):
            ruler[sign] = planet
    for s in signs:
        s["ruler"] = ruler[s["sign"]]

    courts = []
    for head, dates, body, shadow in entries(section(text, "3. Карта двора")):
        rank, suit = head.split(" ")
        courts.append({"card": head, "img": img(f"{SUITS[suit]}-{COURT[rank]:02d}"), "dates": dates,
                       "text": body, "shadow": shadow})

    # Младший аркан «Солнце в знаке» — есть только у пяти знаков; остальным дополнения нет.
    LOC = {"Овне": "Овен", "Тельце": "Телец", "Близнецах": "Близнецы", "Раке": "Рак", "Льве": "Лев", "Деве": "Дева",
           "Весах": "Весы", "Скорпионе": "Скорпион", "Стрельце": "Стрелец", "Козероге": "Козерог", "Водолее": "Водолей",
           "Рыбах": "Рыбы"}
    minors = []
    for head, _, body, shadow in entries(section(text, "Дополняет: младший аркан «Солнце в знаке»")):
        m = re.match(r"(\d+) (\S+) · Солнце (во? (\S+))$", head)
        if not m:
            sys.exit(f"в разделе «Дополняет» не карта «Солнце в знаке»: {head}")
        num, suit, where, loc = m.groups()
        minors.append(LOC[loc])
        sign = next(x for x in signs if x["sign"] == LOC[loc])
        sign["minor"] = {"card": f"{num} {suit}", "img": img(f"{SUITS[suit]}-{int(num):02d}"), "where": f"Солнце {where}",
                         "text": body, "shadow": shadow}

    if (len(signs), len(planets), len(ruler), len(courts)) != (12, 7, 12, 12) or not minors:
        sys.exit(f"разобрано не всё: знаков {len(signs)}/12, покровителей {len(planets)}/7 на {len(ruler)}/12 знаков, "
                 f"карт двора {len(courts)}/12, младших {len(minors)} — проверьте разметку {SRC.name}")
    data = {"signs": signs, "planets": planets, "courts": courts}
    OUT.write_text("// Собрано scripts/astro_data.py из vera-life/methods/astro-tarot/traktovki.md — не править руками.\n"
                   "window.ASTRO = " + json.dumps(data, ensure_ascii=False, indent=1) + ";\n", encoding="utf-8")
    print(f"{OUT.relative_to(ROOT)}: 12 знаков, 7 покровителей, 12 карт двора, младший аркан у: {', '.join(minors)}")

    if "--cards" in sys.argv:
        from PIL import Image
        CARDS.mkdir(exist_ok=True)
        need = {x["img"] for x in signs + courts + list(planets.values()) + [s["minor"] for s in signs if "minor" in s] if x["img"]}
        for cid in sorted(need):
            with Image.open(DECK / f"{cid}.jpg") as im:
                im = im.convert("RGB")
                im.thumbnail((360, 600), Image.LANCZOS)
                im.save(CARDS / f"{cid}.webp", "WEBP", quality=80, method=6)
        print(f"{CARDS.relative_to(ROOT)}: {len(need)} карт")


if __name__ == "__main__":
    main()
