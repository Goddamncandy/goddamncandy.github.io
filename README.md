# veralozhkina.ru

Сайт Веры Ложкиной: аналитические расклады на таро в духе Юнга и блог. Собирается движком Notepub из текстовых
файлов, публикуется GitHub Pages из репозитория `Goddamncandy/goddamncandy.github.io`: **push в `main` выкладывает
сайт.** Пока Вера не утвердила тексты, сайт закрыт от поиска и с плашкой «черновик» (`settings.closed` и `robots`
в `config.yaml`).

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
| вёрстка | `theme/templates/`, блок записи — `partials/cta.html` |
| цвета и шрифты | `theme/assets/site.css`: холодный серый, акцент — ультрамарин, только светлая тема |

Ссылки между страницами — вики-ссылкой `[[адрес|текст]]`.

Статьи — генератором `lifeos articles` из хранилища `../vera-life/` (каждая команда там —
`LIFEOS_CONF=~/.config/lifeos-vera lifeos …`). Воронка, в которой стоит сайт, — `../vera-life/projects/funnel.md`.
