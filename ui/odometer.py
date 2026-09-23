"""CSS-only rolling-digit counters — no JS, animates via generated @keyframes."""

from __future__ import annotations

_DIGITS = "".join(f'<span>{d}</span>' for d in range(10))


def _digit_keyframes(name: str, digit: int, hold_steps: int) -> str:
    """Step through 0..digit, holding briefly on each, landing on `digit`."""
    if digit == 0:
        return f"@keyframes {name} {{ from, to {{ transform: translateY(0); }} }}"
    stops = []
    settle_at = 72
    for step in range(digit + 1):
        pct = round((step / digit) * settle_at, 2)
        stops.append(f"{pct}% {{ transform: translateY(-{step * 10}%); }}")
    stops.append(f"100% {{ transform: translateY(-{digit * 10}%); }}")
    return f"@keyframes {name} {{ {' '.join(stops)} }}"


def counter(value: int, *, key: str, duration: float = 1.0, delay: float = 0.0) -> str:
    """Render `value` as a rolling-digit counter. `key` must be unique on the page."""
    digits = str(value)
    columns = []
    keyframes = []
    for i, ch in enumerate(digits):
        d = int(ch)
        name = f"odo_{key}_{i}"
        keyframes.append(_digit_keyframes(name, d, hold_steps=d))
        columns.append(
            f'<span class="odo-col">'
            f'<span class="odo-strip" style="animation-name:{name};'
            f'animation-duration:{duration}s;animation-delay:{delay + i * 0.05:.2f}s">'
            f"{_DIGITS}</span></span>"
        )
    return (
        f"<style>{''.join(keyframes)}</style>"
        f'<span class="odo">{"".join(columns)}</span>'
    )
