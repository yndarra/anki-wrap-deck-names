# Wrap Long Deck Names

**Install:** in Anki go to Tools → Add-ons → Get Add-ons… and enter the code **`1431591599`** ([AnkiWeb page](https://ankiweb.net/shared/info/1431591599)).
**Установка:** Инструменты → Дополнения → Скачать дополнения… → код **`1431591599`**.

A small Anki add-on: long deck names in the deck list **wrap onto new lines** instead of stretching the whole table across the screen. It works like AnkiMobile/AnkiDroid, but without "…". The full name is always visible.

- The deck name column gets a fixed width (default `20em`). Longer names wrap inside it.
- Wrapped lines start under the beginning of the name, not under the subdeck indent.
- Settings (Tools → Add-ons → Config): name column width (`20em`, `300px`, `30vw`, …) and **whole table width in %** (100 = as is, 120 = 20% wider). The extra space goes to the name column, and the table never gets wider than the window. Changes apply immediately.
- It only touches the deck name cells, so it works with other deck-list add-ons such as [Deck Size Column](https://github.com/yndarra/anki-deck-size-column) and [Deck List Column Headers](https://github.com/yndarra/anki-deck-list-headers).

Build: `build.bat` → `dist/wrap_deck_names.ankiaddon`. Requires Anki 23.10+. Tested with 26.09.

---

# Перенос длинных названий колод (RU)

Длинное название колоды переносится на следующие строки внутри столбца фиксированной ширины, без троеточия, и больше не растягивает таблицу. Продолжение встаёт под начало названия. В настройках (Инструменты → Дополнения → Config) задаются ширина столбца названий и ширина всей таблицы в процентах: 120 — на 20 % шире, добавленное место получает столбец названий.

## License
MIT
