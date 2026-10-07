<b>Long deck names wrap onto new lines instead of stretching the deck list across the screen.</b>

<ul>
<li>The deck name column gets a fixed width (default 20em). Longer names wrap inside it, like on mobile but without "…". The full name stays visible.</li>
<li>Wrapped lines start under the beginning of the name, not under the subdeck indent.</li>
<li>Settings window (Config button): the name column width (20em, 300px, 30vw…) and the whole table width in % (e.g. 120 = 20% wider; the extra space goes to the names, never wider than the window). Changes apply immediately.</li>
<li>It only touches the deck name cells, so it works with other deck-list add-ons.</li>
</ul>

Companion add-ons: <a href="https://github.com/yndarra/anki-deck-size-column">Deck Size Column</a> and <a href="https://github.com/yndarra/anki-deck-list-headers">Deck List Column Headers</a>.

Source code: <a href="https://github.com/yndarra/anki-wrap-deck-names">github.com/yndarra/anki-wrap-deck-names</a>

<i>RU: длинные названия колод переносятся на новые строки, а не растягивают таблицу.</i>
