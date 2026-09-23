#!/usr/bin/env python3
"""
Arvutab, mitmes õppenädal käib, ja kirjutab tulemuse README.md-sse
markerite <!--WEEK:START--> ja <!--WEEK:END--> vahele.

Käivitatakse GitHub Actionsiga kord ööpäevas.
"""

from datetime import date, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo
import datetime as dt

# ---------------------------------------------------------------------------
# SEADED — lisa siia uued semestrid, kui õppeaasta vahetub
# ---------------------------------------------------------------------------

WEEKS = 16                      # õppenädalate arv semestris
TZ = ZoneInfo("Europe/Tallinn")
README = Path("README.md")

SEMESTERS = [
    ("sügissemester 2026/27", date(2026, 8, 31)),
    ("kevadsemester 2026/27", date(2027, 2, 1)),
    # ("sügissemester 2027/28", date(2027, 8, 30)),
    # ("kevadsemester 2027/28", date(2028, 1, 31)),
]

BAR_FULL = "▰"
BAR_EMPTY = "▱"

# ---------------------------------------------------------------------------


def semester_end(start: date) -> date:
    """Viimane õppepäev — algusest 16 nädalat, pühapäevaga lõpetades."""
    return start + timedelta(days=WEEKS * 7 - 1)


def status(today: date) -> str:
    # Kas mõni semester on parasjagu käimas?
    for name, start in SEMESTERS:
        end = semester_end(start)
        if start <= today <= end:
            week = (today - start).days // 7 + 1
            bar = BAR_FULL * week + BAR_EMPTY * (WEEKS - week)
            left = (end - today).days + 1
            return (
                f"**Õppenädal {week}/{WEEKS}** · {name}\n\n"
                f"`{bar}`\n\n"
                f"<sub>Semestri lõpuni {left} päeva.</sub>"
            )

    # Ei ole — leia järgmine algus
    upcoming = [(n, s) for n, s in SEMESTERS if s > today]
    if upcoming:
        name, start = min(upcoming, key=lambda x: x[1])
        days = (start - today).days
        bar = BAR_EMPTY * WEEKS
        return (
            f"**Vaheaeg** · järgmisena {name}\n\n"
            f"`{bar}`\n\n"
            f"<sub>Algab {start.strftime('%d.%m.%Y')} — {days} päeva pärast.</sub>"
        )

    return (
        "**Semestrid otsas** — lisa uued kuupäevad `week.py` faili "
        "`SEMESTERS` nimekirja."
    )


def main() -> None:
    today = dt.datetime.now(TZ).date()
    block = status(today)

    text = README.read_text(encoding="utf-8")
    start_tag, end_tag = "<!--WEEK:START-->", "<!--WEEK:END-->"

    if start_tag not in text or end_tag not in text:
        raise SystemExit(
            f"README.md-s puuduvad markerid {start_tag} ja {end_tag}"
        )

    before = text.split(start_tag)[0]
    after = text.split(end_tag)[1]
    new = f"{before}{start_tag}\n{block}\n{end_tag}{after}"

    if new != text:
        README.write_text(new, encoding="utf-8")
        print("README uuendatud:\n" + block)
    else:
        print("Muudatusi ei ole.")


if __name__ == "__main__":
    main()
