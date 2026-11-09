# veralozhkina.ru

Сайт Веры Ложкиной: аналитические расклады на таро в духе Юнга и блог. Собирается движком Notepub из текстовых
файлов, публикуется GitHub Pages из репозитория `Goddamncandy/goddamncandy.github.io`: **push в `main` выкладывает
сайт.** Домен `veralozhkina.ru` — в настройках Pages, DNS в reg.ru. Открыт для поиска с 02.11.2026; закрыть с плашкой
«черновик» — `settings.closed: "yes"` и `"/"` в `robots` в `config.yaml`. Пуш идёт под аккаунтом Веры через `gh`
(задано в git-настройках репозитория).

## Команды

```bash
scripts/preview.sh              # собрать с локальными адресами в dist-dev/ и открыть на http://127.0.0.1:8089/
scripts/preview.sh --build-only # то же без сервера — проверка перед коммитом
scripts/build.sh                # собрать dist/ с адресами из config.yaml; ничего не публикует
```

Нужен только Notepub: сборка берёт `../site/.bin/notepub`, если он есть, иначе ставит закреплённую версию
(`NOTEPUB_REF` в `scripts/build.sh` и `.github/workflows/pages.yml` — та же, что у `site/`).

## Где что

| что | где |
|---|---|
| первый экран и текст главной | `content/home.md` |
| страница оффера (цена, формат, запись) | `content/rasklad.md` |
| статья блога | новый файл в `content/blog/`, с `published_at` и `date_label`; в ленту и на главную встаёт сама |
| цена, ник для записи, канал, закрытость от поиска | `settings` в `config.yaml` и то же в `config.dev.yaml` |
| вёрстка | `theme/templates/`, блок записи — `partials/cta.html`; три шага на главной — прямо в `home.html` |
| рисунки | `partials/orbits.html` (орбиты за заголовком), `partials/tension.html` (точка напряжения), значки — `partials/icons.html` |
| картинки для соцсетей (og:image) | `scripts/og/make.py` → `theme/assets/og/<slug>.jpg`, сам из `scripts/preview.sh`: новой странице выводит тексты из title/description и пишет во frontmatter (`og_title`, `og_em` — курсив, `og_sub`, `og_image`), рисует только изменившееся. Правила — `../vera-life/projects/opengraph.md`. Нужен Chrome; картинки коммитятся |
| поиск и модели | `seo_title` во frontmatter — короткий `<title>`; разметка schema.org — `seo.jsonld: auto` в конфиге (WebSite, WebPage, Article у статей); `llms.txt` — блок `llms` в конфиге. Оба блока — в `config.yaml` и `config.dev.yaml` |
| цвета и шрифты | `theme/assets/site.css`: холодный серый, белая рамка, тёмные круглые значки; акцент — ультрамарин только в точках; только светлая тема. Анимации выключаются при «уменьшить движение» |

Ссылки между страницами — вики-ссылкой `[[адрес|текст]]`.

Статьи — генератором `lifeos articles` из хранилища `../vera-life/` (каждая команда там —
`LIFEOS_CONF=~/.config/lifeos-vera lifeos …`). Воронка, в которой стоит сайт, — `../vera-life/projects/funnel.md`.
