"""Wrap Long Deck Names — длинные названия колод переносятся на новые строки.

Как в мобильной Anki, но без троеточия: столбец названий получает
фиксированную ширину, а название, которое в неё не влезает, переносится
на следующие строки. Таблица больше не растягивается на весь экран.
Продолжение встаёт под начало названия, а не под отступ подколоды.

Как устроено: перед отрисовкой списка (хук deck_browser_will_render_content)
в блок под таблицей добавляются стиль и скрипт. Скрипт трогает только ячейки
td.decktd: кладёт отступ, значок свёртки и ссылку в flex-строку div.wdn-name.
Другие столбцы и заголовки не меняются, поэтому дополнение не конфликтует
с Deck Size Column, Deck List Column Headers и подобными.
"""

from __future__ import annotations

import re

import anki.lang
from aqt import gui_hooks, mw
from aqt.deckbrowser import DeckBrowser, DeckBrowserContent
from aqt.qt import QDialog, QDialogButtonBox, QFormLayout, QLabel, QLineEdit, QWidget

ADDON = __name__.split(".")[0]
DEFAULT_WIDTH = "20em"

_TEXTS = {
    "ru": {
        "dlg_title": "Перенос названий колод",
        "width": "Ширина столбца названий",
        "hint": "Например 20em, 300px или 30vw. Длиннее — переносится на новые строки.",
        "defaults": "По умолчанию",
    },
    "en": {
        "dlg_title": "Wrap Long Deck Names",
        "width": "Name column width",
        "hint": "E.g. 20em, 300px or 30vw. Longer names wrap onto new lines.",
        "defaults": "Defaults",
    },
}

# Разрешаем только «число + единица CSS» — чтобы в стиль не попало ничего лишнего.
_WIDTH_RE = re.compile(r"^\d+(\.\d+)?(px|em|rem|vw|%|ch)$")

_SCRIPT = """
(function () {
    "use strict";
    document.querySelectorAll("td.decktd").forEach((td) => {
        if (td.querySelector(".wdn-name")) return; // уже обработано
        const box = document.createElement("div");
        box.className = "wdn-name";
        // Отступ подколоды у Anki — текст из &nbsp; в начале ячейки.
        const indent = document.createElement("span");
        indent.className = "wdn-indent";
        while (td.firstChild && td.firstChild.nodeType === Node.TEXT_NODE) {
            indent.appendChild(td.firstChild);
        }
        box.appendChild(indent);
        while (td.firstChild) box.appendChild(td.firstChild);
        td.appendChild(box);
    });
})();
"""


def _t(text_id: str) -> str:
    lang = "ru" if (anki.lang.current_lang or "").lower().startswith("ru") else "en"
    return _TEXTS[lang][text_id]


def get_width() -> str:
    cfg = mw.addonManager.getConfig(ADDON) or {}
    width = str(cfg.get("name_width", DEFAULT_WIDTH)).strip()
    return width if _WIDTH_RE.match(width) else DEFAULT_WIDTH


def _css(width: str) -> str:
    return (
        "<style>"
        # Фиксированная ширина столбца названий: таблица больше не растягивается.
        f"td.decktd {{ white-space: normal; width: {width}; min-width: {width}; max-width: {width}; }}"
        ".wdn-name { display: flex; align-items: baseline; }"
        ".wdn-indent { white-space: pre; flex: none; }"
        ".wdn-name .collapse { flex: none; }"
        # Название занимает остаток строки и переносится внутри него.
        ".wdn-name a.deck { display: block; flex: 1 1 auto; min-width: 0;"
        " white-space: normal; overflow-wrap: break-word; }"
        "</style>"
    )


def on_will_render(deck_browser: DeckBrowser, content: DeckBrowserContent) -> None:
    content.stats += _css(get_width()) + "<script>" + _SCRIPT + "</script>"


class SettingsDialog(QDialog):
    def __init__(self, parent: QWidget | None) -> None:
        super().__init__(parent)
        self.setWindowTitle(_t("dlg_title"))
        self.setMinimumWidth(380)
        form = QFormLayout(self)
        self.width = QLineEdit(get_width())
        self.width.setPlaceholderText(DEFAULT_WIDTH)
        form.addRow(_t("width"), self.width)
        hint = QLabel(_t("hint"))
        hint.setWordWrap(True)
        form.addRow(hint)
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        reset = buttons.addButton(_t("defaults"), QDialogButtonBox.ButtonRole.ResetRole)
        reset.clicked.connect(lambda: self.width.setText(DEFAULT_WIDTH))
        buttons.accepted.connect(self._save)
        buttons.rejected.connect(self.reject)
        form.addRow(buttons)

    def _save(self) -> None:
        width = self.width.text().strip().replace(" ", "")
        if not _WIDTH_RE.match(width):
            width = DEFAULT_WIDTH
        mw.addonManager.writeConfig(ADDON, {"name_width": width})
        if mw.state == "deckBrowser":
            mw.deckBrowser.refresh()
        self.accept()


def open_settings() -> None:
    SettingsDialog(mw).exec()


gui_hooks.deck_browser_will_render_content.append(on_will_render)
mw.addonManager.setConfigAction(ADDON, open_settings)
