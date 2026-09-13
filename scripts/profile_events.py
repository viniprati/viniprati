from __future__ import annotations

import argparse
import os
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Iterable
from urllib.parse import quote
from zoneinfo import ZoneInfo


ROOT = Path(__file__).resolve().parents[1]
BASE_README = ROOT / "README.base.md"
OUTPUT_README = ROOT / "README.md"
TIMEZONE = ZoneInfo("America/Sao_Paulo")
PRIMARY_COLOR = "06BB12"
BACKGROUND_COLOR = "000000"


@dataclass(frozen=True)
class EventTheme:
    name: str
    accent_color: str = PRIMARY_COLOR
    label_color: str = BACKGROUND_COLOR


@dataclass(frozen=True)
class ProfileEvent:
    slug: str
    dates: tuple[tuple[int, int], ...]
    title: str
    subtitle: str
    emojis: tuple[str, ...]
    footer: str
    theme: EventTheme
    image_url: str | None = None


EVENTS: tuple[ProfileEvent, ...] = (
    ProfileEvent(
        slug="birthday",
        dates=((6, 4),),
        title="Vinicius +1.0",
        subtitle="Version upgraded successfully.",
        emojis=("🎂", "🚀", "🟢"),
        footer="Novo ciclo, mesmo foco: aprender, criar e entregar código melhor.",
        theme=EventTheme("release-day"),
    ),
    ProfileEvent(
        slug="pi-day",
        dates=((3, 14),),
        title="Pi Day",
        subtitle="Código, lógica e uma pitada infinita de curiosidade.",
        emojis=("π", "🥧", "🧮"),
        footer="Hoje o algoritmo também aceita aproximações elegantes.",
        theme=EventTheme("math-mode"),
    ),
    ProfileEvent(
        slug="star-wars-day",
        dates=((5, 4),),
        title="May the Source be with you",
        subtitle="Que a força do código limpo esteja com o deploy.",
        emojis=("⭐", "💻", "🟢"),
        footer="Commits pequenos, testes passando e sabedoria no terminal.",
        theme=EventTheme("source-force"),
    ),
    ProfileEvent(
        slug="brazil-independence",
        dates=((9, 7),),
        title="Independência do Brasil",
        subtitle="Um dia para lembrar raízes, autonomia e construção coletiva.",
        emojis=("🇧🇷", "🟢", "⚙️"),
        footer="Tecnologia também é sobre criar caminhos próprios.",
        theme=EventTheme("brasil-dev"),
    ),
    ProfileEvent(
        slug="programmers-day",
        dates=((9, 13),),
        title="Dia do Programador",
        subtitle="256 possibilidades para transformar ideias em software.",
        emojis=("💻", "⌨️", "🟢"),
        footer="Hoje o README roda em modo celebração para quem vive entre lógica, bugs e café.",
        theme=EventTheme("terminal-green"),
    ),
    ProfileEvent(
        slug="halloween",
        dates=((10, 31),),
        title="Halloween",
        subtitle="Nenhum bug fantasma passou pelo lint hoje.",
        emojis=("🎃", "🕸️", "💻"),
        footer="Logs claros, sustos pequenos e deploy sem assombração.",
        theme=EventTheme("dark-terminal"),
    ),
    ProfileEvent(
        slug="christmas",
        dates=((12, 24), (12, 25)),
        title="Natal",
        subtitle="Que os builds venham verdes e os commits tragam boas entregas.",
        emojis=("🎄", "✨", "🟢"),
        footer="Boas festas, bons estudos e código com propósito.",
        theme=EventTheme("holiday-green"),
    ),
    ProfileEvent(
        slug="new-year",
        dates=((12, 31), (1, 1)),
        title="Ano Novo",
        subtitle="Novo ciclo inicializado com energia de projeto bem estruturado.",
        emojis=("🎆", "🚀", "🟢"),
        footer="Que venham novas versões, novos aprendizados e bons deploys.",
        theme=EventTheme("next-version"),
    ),
)


def today_in_profile_timezone() -> date:
    return datetime.now(TIMEZONE).date()


def parse_date(value: str | None) -> date:
    if not value:
        return today_in_profile_timezone()

    return date.fromisoformat(value)


def find_event(current_date: date) -> ProfileEvent | None:
    current_key = (current_date.month, current_date.day)
    return next((event for event in EVENTS if current_key in event.dates), None)


def shield_url(label: str, message: str, theme: EventTheme) -> str:
    encoded_label = quote(label.replace("-", "--"), safe="")
    encoded_message = quote(message.replace("-", "--"), safe="")
    return (
        "https://img.shields.io/badge/"
        f"{encoded_label}-{encoded_message}-{theme.accent_color}"
        f"?style=for-the-badge&labelColor={theme.label_color}"
    )


def render_event_block(event: ProfileEvent, current_date: date) -> str:
    badge = shield_url(event.title, event.theme.name, event.theme)
    emoji_line = " ".join(event.emojis)
    image = render_optional_image(event)

    return f"""<!-- profile-event:start -->
<div align="center">

### `{emoji_line} {event.title}`

<img src="{badge}" alt="{event.title}" />

**{event.subtitle}**

<br />

<sub>{event.footer}</sub>

<br />
<sub>Evento ativo em {current_date.strftime("%d/%m")} · America/Sao_Paulo</sub>

{image}</div>

---

<!-- profile-event:end -->
"""


def render_optional_image(event: ProfileEvent) -> str:
    if not event.image_url:
        return ""

    return f"""
<p align="center">
  <img src="{event.image_url}" alt="{event.title}" width="520" />
</p>

"""


def build_readme(base_content: str, event: ProfileEvent | None, current_date: date) -> str:
    if event is None:
        return ensure_trailing_newline(base_content)

    return render_event_block(event, current_date) + ensure_trailing_newline(base_content)


def ensure_trailing_newline(content: str) -> str:
    return content if content.endswith("\n") else f"{content}\n"


def write_if_changed(path: Path, content: str) -> bool:
    existing = path.read_text(encoding="utf-8") if path.exists() else ""
    if existing == content:
        return False

    path.write_text(content, encoding="utf-8")
    return True


def event_summary(event: ProfileEvent | None) -> str:
    return event.slug if event else "base"


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate the profile README for seasonal events.")
    parser.add_argument(
        "--date",
        default=os.getenv("PROFILE_EVENTS_DATE"),
        help="Optional ISO date override for local checks, for example 2026-09-13.",
    )
    args = parser.parse_args(argv)

    current_date = parse_date(args.date)
    base_content = BASE_README.read_text(encoding="utf-8")
    event = find_event(current_date)
    generated = build_readme(base_content, event, current_date)
    changed = write_if_changed(OUTPUT_README, generated)

    print(f"README profile mode: {event_summary(event)}")
    print(f"README.md changed: {'yes' if changed else 'no'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
