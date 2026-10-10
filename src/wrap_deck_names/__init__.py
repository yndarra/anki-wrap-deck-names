"""Wrap Long Deck Names — длинные названия колод переносятся на новые строки.

Как в мобильной Anki, но без троеточия: столбец названий получает
фиксированную ширину, а название, которое в неё не влезает, переносится
на следующие строки. Таблица больше не растягивается на весь экран.
Продолжение встаёт под начало названия, а не под отступ подколоды.

Две настройки:
  • name_width — ширина столбца названий (20em, 300px, 30vw…);
  • table_scale — ширина всей таблицы (блока со списком колод) в процентах
    от того, что получилось: 100 — как есть, 120 — на 20 % шире.
    Добавленная ширина целиком уходит столбцу названий (числа не растягиваются),
    но таблица не вылезает за пределы окна.

Как устроено: перед отрисовкой списка (хук deck_browser_will_render_content)
в блок под таблицей добавляются стиль и скрипт. Скрипт трогает только ячейки
td.decktd: кладёт отступ, значок свёртки и ссылку в flex-строку div.wdn-name,
а для table_scale меряет готовую таблицу после загрузки страницы (когда другие
дополнения уже добавили свои столбцы) и расширяет столбец названий.
Другие столбцы и заголовки не меняются, поэтому дополнение не конфликтует
с Deck Size Column, Deck List Column Headers и подобными.
"""

from __future__ import annotations

import json
import re

import anki.lang
from aqt import gui_hooks, mw
from aqt.deckbrowser import DeckBrowser, DeckBrowserContent
from aqt.qt import QDialog, QDialogButtonBox, QFormLayout, QLabel, QLineEdit, QSpinBox, QWidget

ADDON = __name__.split(".")[0]
DEFAULT_WIDTH = "20em"
DEFAULT_SCALE = 100

_TEXTS = {
    "ru": {
        "dlg_title": "Перенос названий колод",
        "width": "Ширина столбца названий",
        "hint": "Например 20em, 300px или 30vw. Длиннее — переносится на новые строки.",
        "scale": "Ширина всей таблицы, %",
        "scale_hint": "100 — как получилось, 120 — на 20 % шире. Добавленное место "
        "получает столбец названий; за край окна таблица не выйдет.",
        "defaults": "По умолчанию",
    },
    "en": {
        "dlg_title": "Wrap Long Deck Names",
        "width": "Name column width",
        "hint": "E.g. 20em, 300px or 30vw. Longer names wrap onto new lines.",
        "scale": "Whole table width, %",
        "scale_hint": "100 — as is, 120 — 20% wider. The extra space goes to the name "
        "column; the table never gets wider than the window.",
        "defaults": "Defaults",
    },
}

# Разрешаем только «число + единица CSS» — чтобы в стиль не попало ничего лишнего.
_WIDTH_RE = re.compile(r"^\d+(\.\d+)?(px|em|rem|vw|%|ch)$")

_SCRIPT = """
(function () {
    "use strict";
    // 1) Перенос: отступ, значок свёртки и название — в одну flex-строку.
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

    // 2) Ширина всей таблицы в процентах — добавку получает столбец названий.
    const scale = window.WDN_SCALE || 100;
    if (scale === 100) return;
    function widen() {
        const old = document.getElementById("wdn-scale");
        if (old) old.remove(); // меряем заново от исходной ширины
        const table = document.querySelector("table");
        const td = document.querySelector("td.decktd");
        if (!table || !td) return;
        const base = table.offsetWidth;
        let extra = base * (scale - 100) / 100;
        // Не шире окна (с запасом на поля страницы).
        const room = document.documentElement.clientWidth - 40 - base;
        if (extra > room) extra = Math.max(room, Math.min(extra, 0));
        const cur = parseFloat(getComputedStyle(td).width);
        const width = Math.max(cur + extra, 80);
        const style = document.createElement("style");
        style.id = "wdn-scale";
        style.textContent = `td.decktd { width: ${width}px !important;` +
            ` min-width: ${width}px !important; max-width: ${width}px !important; }`;
        document.head.appendChild(style);
    }
    // После загрузки страницы — когда все дополнения уже добавили свои столбцы.
    if (document.readyState === "complete") widen();
    else window.addEventListener("load", widen);
    let timer;
    window.addEventListener("resize", () => {
        clearTimeout(timer);
        timer = setTimeout(widen, 150);
    });
})();
"""


def _t(text_id: str) -> str:
    lang = "ru" if (anki.lang.current_lang or "").lower().startswith("ru") else "en"
    return _TEXTS[lang][text_id]


def get_config() -> dict:
    cfg = mw.addonManager.getConfig(ADDON) or {}
    width = str(cfg.get("name_width", DEFAULT_WIDTH)).strip()
    try:
        scale = int(cfg.get("table_scale", DEFAULT_SCALE))
    except (TypeError, ValueError):
        scale = DEFAULT_SCALE
    return {
        "name_width": width if _WIDTH_RE.match(width) else DEFAULT_WIDTH,
        "table_scale": min(max(scale, 50), 300),
    }


def _css(width: str) -> str:
    return (
        "<style>"
        # Фиксированная ширина столбца названий: таблица больше не растягивается.
        f"td.decktd {{ white-space: normal; width: {width}; min-width: {width}; max-width: {width}; }}"
        ".wdn-name { display: flex; align-items: baseline; }"
        ".wdn-indent { white-space: pre; flex: none; }"
        ".wdn-name .collapse { flex: none; }"
        # Ссылка шириной ровно с текст названия (flex: 0 1 auto): короткое название
        # не растягивается на всю ячейку, и справа от него остаётся пустое место —
        # туда, как и без дополнения, можно щёлкнуть с Shift, чтобы выделить строку.
        # Длинное название сжимается до ширины столбца и переносится внутри неё.
        ".wdn-name a.deck { display: block; flex: 0 1 auto; min-width: 0;"
        " white-space: normal; overflow-wrap: break-word; }"
        "</style>"
    )


def on_will_render(deck_browser: DeckBrowser, content: DeckBrowserContent) -> None:
    cfg = get_config()
    content.stats += (
        _css(cfg["name_width"])
        + f"<script>window.WDN_SCALE = {json.dumps(cfg['table_scale'])};"
        + _SCRIPT
        + "</script>"
    )


class SettingsDialog(QDialog):
    def __init__(self, parent: QWidget | None) -> None:
        super().__init__(parent)
        self.setWindowTitle(_t("dlg_title"))
        self.setMinimumWidth(420)
        form = QFormLayout(self)
        cfg = get_config()

        self.width = QLineEdit(cfg["name_width"])
        self.width.setPlaceholderText(DEFAULT_WIDTH)
        form.addRow(_t("width"), self.width)
        hint = QLabel(_t("hint"))
        hint.setWordWrap(True)
        form.addRow(hint)

        self.scale = QSpinBox()
        self.scale.setRange(50, 300)
        self.scale.setSingleStep(5)
        self.scale.setSuffix(" %")
        self.scale.setValue(cfg["table_scale"])
        form.addRow(_t("scale"), self.scale)
        scale_hint = QLabel(_t("scale_hint"))
        scale_hint.setWordWrap(True)
        form.addRow(scale_hint)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        reset = buttons.addButton(_t("defaults"), QDialogButtonBox.ButtonRole.ResetRole)
        reset.clicked.connect(self._reset)
        buttons.accepted.connect(self._save)
        buttons.rejected.connect(self.reject)
        form.addRow(buttons)

    def _reset(self) -> None:
        self.width.setText(DEFAULT_WIDTH)
        self.scale.setValue(DEFAULT_SCALE)

    def _save(self) -> None:
        width = self.width.text().strip().replace(" ", "")
        if not _WIDTH_RE.match(width):
            width = DEFAULT_WIDTH
        mw.addonManager.writeConfig(
            ADDON, {"name_width": width, "table_scale": self.scale.value()}
        )
        if mw.state == "deckBrowser":
            mw.deckBrowser.refresh()
        self.accept()


def open_settings() -> None:
    SettingsDialog(mw).exec()


gui_hooks.deck_browser_will_render_content.append(on_will_render)
mw.addonManager.setConfigAction(ADDON, open_settings)
