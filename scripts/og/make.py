#!/usr/bin/env python3
"""Картинки для соцсетей (og:image, 1200×630) в theme/assets/og/<slug>.jpg — сами, для каждой страницы.

Правила (они же в хранилище Веры, vera-life/projects/opengraph.md):
- страница: сверху заголовок, в центре фото Веры в круге, снизу подзаголовок; инструмент: заголовок и барабан даты;
- тексты не продающие: без цены, «записаться», скидок;
- курсив — Cormorant Garamond, по высоте строчных равен Mulish (1.3em); курсивная часть не переносится;
- всё, что нельзя потерять, — в центральном квадрате 630×630: соцсети, которые режут превью до квадрата, его не теряют.

Тексты — во frontmatter страницы: og_title (обычная часть), og_em (курсив), og_sub (подзаголовок). У новой страницы
их нет — скрипт выводит их из title (до двоеточия; курсив — последние слова) и из того, что после двоеточия,
или из description, пишет во frontmatter вместе с og_image и рисует картинку. Поправить текст — править эти поля.
Перерисовывается только то, что изменилось (тексты, фото, шаблон) — отпечатки в theme/assets/og/made.json.

    python3 scripts/og/make.py            # недостающие и изменившиеся (так зовёт scripts/preview.sh)
    python3 scripts/og/make.py --all      # все заново
    python3 scripts/og/make.py --check    # только проверить: есть ли у каждой страницы картинка; код 1, если нет

Нужны Google Chrome и сеть (шрифты с Google Fonts). Без Chrome скрипт ничего не делает и не мешает сборке.
"""
import base64
import hashlib
import html
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

import yaml
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
CONTENT = ROOT / "content"
OUT = ROOT / "theme/assets/og"
MADE = OUT / "made.json"
PHOTO = ROOT / "theme/assets/vera.jpg"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
SKIP_TYPES = {"notfound"}

FONTS = ('<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@1,500'
         '&family=Mulish:wght@400;500;600&display=swap">')
BASE_CSS = """
*{box-sizing:border-box;margin:0}
html,body{width:1200px;height:630px;overflow:hidden}
body{background:#eceef1;font-family:Mulish,sans-serif;color:#1d2025;-webkit-font-smoothing:antialiased}
.frame{position:absolute;inset:24px;background:#f7f8f9;border-radius:28px;
  box-shadow:0 1px 2px rgba(29,32,37,.04),0 8px 24px rgba(29,32,37,.05);
  display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center}
/* Текст и фото — только в центральном квадрате: где превью режут до квадрата, ничего не теряется */
.safe{width:560px;display:flex;flex-direction:column;align-items:center}
h1{font-weight:500;letter-spacing:-.025em;line-height:1.12}
h1 em{font-family:"Cormorant Garamond",serif;font-style:italic;font-weight:500;font-size:1.3em;line-height:.9;white-space:nowrap;
  letter-spacing:-.01em;color:#5d646e}
.sub{color:#5d646e;font-size:27px;line-height:1.3}
.site{position:absolute;bottom:26px;font-size:17px;color:#959ca5;letter-spacing:.02em}
"""


def page_html(title, em, sub, photo):
    return f"""<!doctype html><html lang="ru"><head><meta charset="utf-8">{FONTS}<style>{BASE_CSS}
h1{{font-size:50px}}
.photo{{width:200px;height:200px;border-radius:50%;margin:26px 0 24px;background:url(data:image/jpeg;base64,{photo})
  center/cover;box-shadow:0 0 0 8px #fff,0 10px 30px rgba(29,32,37,.16)}}
</style></head><body><div class="frame">
<div class="safe">
<h1>{html.escape(title)} <em>{html.escape(em)}</em></h1>
<div class="photo"></div>
<p class="sub">{html.escape(sub)}</p>
</div>
<span class="site">Вера Ложкина · veralozhkina.ru</span>
</div></body></html>"""


def tool_html(title, em):
    # Барабан, как на странице инструмента: три колонки, видно пять строк, выбранная — под полосой.
    days = ["17", "18", "19", "20", "21"]
    months = ["апреля", "мая", "июня", "июля", "августа"]
    years = ["1989", "1990", "1991", "1992", "1993"]
    scale = [.82, .92, 1, .92, .82]
    fade = [.28, .55, 1, .55, .28]

    def col(items):
        rows = "".join(f'<div class="it" style="transform:scale({s});opacity:{o}">{v}</div>'
                       for v, s, o in zip(items, scale, fade))
        return f'<div class="col">{rows}</div>'

    return f"""<!doctype html><html lang="ru"><head><meta charset="utf-8">{FONTS}<style>{BASE_CSS}
h1{{font-size:52px;margin-bottom:30px}}
.wheel{{position:relative;display:grid;grid-template-columns:1fr 1.7fr 1.2fr;width:540px;height:280px;
  background:#fff;border-radius:26px;box-shadow:0 1px 2px rgba(29,32,37,.04),0 8px 24px rgba(29,32,37,.06)}}
.band{{position:absolute;left:12px;right:12px;top:112px;height:56px;border-radius:16px;background:rgba(29,32,37,.07)}}
.col{{display:flex;flex-direction:column;justify-content:center}}
.it{{height:56px;line-height:56px;font-size:30px;font-variant-numeric:tabular-nums;white-space:nowrap}}
.dot{{position:absolute;right:-7px;top:133px;width:14px;height:14px;border-radius:50%;background:#3a4bd1}}
</style></head><body><div class="frame">
<div class="safe">
<h1>{html.escape(title)} <em>{html.escape(em)}</em></h1>
<div class="wheel"><div class="band"></div>{col(days)}{col(months)}{col(years)}<span class="dot"></span></div>
</div>
<span class="site">veralozhkina.ru</span>
</div></body></html>"""


def shoot(slug, doc):
    with tempfile.TemporaryDirectory() as tmp:
        src = Path(tmp) / "card.html"
        png = Path(tmp) / "card.png"
        src.write_text(doc, encoding="utf-8")
        subprocess.run([CHROME, "--headless=new", "--hide-scrollbars", "--force-device-scale-factor=1",
                        "--window-size=1200,630", "--virtual-time-budget=8000", f"--screenshot={png}",
                        src.as_uri()], check=True, capture_output=True)
        OUT.mkdir(parents=True, exist_ok=True)
        dst = OUT / f"{slug}.jpg"
        Image.open(png).convert("RGB").crop((0, 0, 1200, 630)).save(dst, "JPEG", quality=86, optimize=True,
                                                                     progressive=True)
    print(f"  og: {dst.relative_to(ROOT)}  {dst.stat().st_size // 1024} КБ")


def split_fm(text):
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        return None, None
    return yaml.safe_load(m.group(1)) or {}, m


def derive(fm):
    """Тексты картинки из title и description, если их ещё нет во frontmatter."""
    title = str(fm.get("title", "")).strip()
    head, _, rest = title.partition(":")
    words = head.split()
    n = 2 if len(words) >= 4 else 1
    og_title, og_em = " ".join(words[:-n]), " ".join(words[-n:])
    sub = rest.strip()
    if not sub:
        desc = str(fm.get("description", "")).strip()
        sub = re.split(r"(?<=[.!?:])\s", desc)[0].rstrip(".:")
        if len(sub) > 60:
            sub = sub[:60].rsplit(" ", 1)[0]
    sub = sub[:1].upper() + sub[1:]
    return og_title or og_em, og_em if og_title else "", sub


def add_fields(path, text, m, fields):
    """Дописать поля в конец frontmatter, не трогая остальное."""
    lines = "".join(f"{k}: {json.dumps(v, ensure_ascii=False)}\n" for k, v in fields.items())
    end = m.end() - len("---\n")
    path.write_text(text[:end] + lines + text[end:], encoding="utf-8")
    print(f"  og: {path.relative_to(ROOT)} ← {', '.join(fields)}")


def pages():
    for path in sorted(CONTENT.rglob("*.md")):
        text = path.read_text(encoding="utf-8")
        fm, m = split_fm(text)
        if fm is None or fm.get("type") in SKIP_TYPES or not fm.get("slug"):
            continue
        yield path, text, fm, m


def main(argv):
    check = "--check" in argv
    missing = [p for p, _, fm, _ in pages() if not (OUT / f"{fm['slug']}.jpg").exists() or not fm.get("og_image")]
    if check:
        for p in missing:
            print(f"нет картинки для соцсетей: {p.relative_to(ROOT)} (python3 scripts/og/make.py)")
        return 1 if missing else 0
    if not Path(CHROME).exists():
        print("og: нет Google Chrome — картинки не рисуются", file=sys.stderr)
        return 0
    made = json.loads(MADE.read_text()) if MADE.exists() and "--all" not in argv else {}
    photo_bytes = PHOTO.read_bytes()
    photo = base64.b64encode(photo_bytes).decode()
    tpl = hashlib.sha1((middle_src() + hashlib.sha1(photo_bytes).hexdigest()).encode()).hexdigest()[:12]
    for path, text, fm, m in pages():
        slug = fm["slug"]
        new = {}
        if not all(fm.get(k) for k in ("og_title", "og_sub")) and not (fm.get("type") == "tool" and fm.get("og_title")):
            t, e, sub = derive(fm)
            for k, v in (("og_title", t), ("og_em", e), ("og_sub", sub)):
                if not fm.get(k) and v:
                    new[k] = v
        if not fm.get("og_image"):
            new["og_image"] = f"/assets/og/{slug}.jpg"
        if new:
            add_fields(path, text, m, new)
            fm.update(new)
        texts = [fm.get("og_title", ""), fm.get("og_em", ""), fm.get("og_sub", ""), fm.get("type")]
        key = hashlib.sha1(json.dumps([tpl] + texts, ensure_ascii=False).encode()).hexdigest()[:12]
        if made.get(slug) == key and (OUT / f"{slug}.jpg").exists():
            continue
        if fm.get("type") == "tool":
            doc = tool_html(fm.get("og_title", ""), fm.get("og_em", ""))
        else:
            doc = page_html(fm.get("og_title", ""), fm.get("og_em", ""), fm.get("og_sub", ""), photo)
        shoot(slug, doc)
        made[slug] = key
    MADE.write_text(json.dumps(made, ensure_ascii=False, indent=1, sort_keys=True) + "\n")
    return 0


def middle_src():
    # Отпечаток шаблона карточек: правка вёрстки в этом файле перерисует все картинки.
    src = Path(__file__).read_text(encoding="utf-8")
    return src[src.index("FONTS = ("):src.index("def shoot(")]


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
