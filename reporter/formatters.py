from reporter.config import FREQ_GREEN, FREQ_YELLOW


def fmt_money(v: float) -> str:
    return f"{v:,.2f}"


def fmt_int(v: float) -> str:
    n = int(round(v))
    if n >= 1_000_000:
        return f"{n/1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n/1_000:.1f}K"
    return str(n)


def fmt_pct(v: float, decimals: int = 2) -> str:
    return f"{v:.{decimals}f}%"


def fmt_freq(v: float) -> str:
    flag = freq_flag(v)
    return f"{v:.1f}× {flag}"


def freq_flag(v: float) -> str:
    if v < FREQ_GREEN:
        return "✅"
    if v < FREQ_YELLOW:
        return "🟡"
    return "🔴"


def fmt_wow(v1: float, v2: float, pp: bool = False) -> str:
    """Week-over-week change. pp=True for percentage-point diff (ER)."""
    if v2 == 0:
        return "new" if v1 > 0 else "—"
    if pp:
        diff = v1 - v2
        sign = "+" if diff >= 0 else ""
        return f"{sign}{diff:.2f}pp"
    pct = (v1 - v2) / v2 * 100
    sign = "+" if pct >= 0 else ""
    return f"{sign}{pct:.1f}%"
