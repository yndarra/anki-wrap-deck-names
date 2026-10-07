# Wrap Long Deck Names

A small Anki add-on: long deck names in the deck list **wrap onto new lines** instead of stretching the whole table across the screen. It works like AnkiMobile/AnkiDroid, but without "…". The full name is always visible.

- The deck name column gets a fixed width (default `20em`). Longer names wrap inside it.
- Wrapped lines start under the beginning of the name, not under the subdeck indent.
- Settings (Tools → Add-ons → Config): column width (`20em`, `300px`, `30vw`, …). Changes apply immediately.
- It only touches the deck name cells, so it works with other deck-list add-ons such as [Deck Size Column](https://github.com/yndarra/anki-deck-size-column) and [Deck List Column Headers](https://github.com/yndarra/anki-deck-list-headers).

Build: `build.bat` → `dist/wrap_deck_names.ankiaddon`. Requires Anki 23.10+. Tested with 26.09.

---

# Перенос длинных названий колод (RU)

Длинное название колоды переносится на следующие строки внутри столбца фиксированной ширины, без троеточия, и больше не растягивает таблицу. Продолжение встаёт под начало названия. Ширина меняется в настройках: Инструменты → Дополнения → Config.

## License
MIT
