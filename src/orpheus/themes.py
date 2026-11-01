"""Built-in color presets. Theme objects are loaded only when the TUI starts."""

DEFAULT_THEME = "github-light-contrast"
PRESET_LABELS = (
    ("blackmetal", "BlackMetal"),
    ("sequoia-light-monochrome", "Sequoia Light Monochrome"),
    ("catppuccin-latte", "Catppuccin Latte"),
    ("github-dark-contrast", "GitHub Dark Contrast"),
    ("github-light-contrast", "GitHub Light Contrast"),
)


def get_themes():
    from textual.theme import Theme

    return (
        Theme(
            name="blackmetal",
            primary="#b7b7b7",
            secondary="#8f8f8f",
            accent="#d0d0d0",
            foreground="#c1c1c1",
            background="#000000",
            surface="#111111",
            panel="#222222",
            dark=True,
        ),
        Theme(
            name="sequoia-light-monochrome",
            primary="#454752",
            secondary="#5f6370",
            accent="#525666",
            foreground="#25262d",
            background="#e2e4ed",
            surface="#f3f4f8",
            panel="#d6d9e4",
            dark=False,
        ),
        Theme(
            name="catppuccin-latte",
            primary="#1e66f5",
            secondary="#8839ef",
            accent="#fe640b",
            foreground="#4c4f69",
            background="#eff1f5",
            surface="#ccd0da",
            panel="#e6e9ef",
            success="#40a02b",
            warning="#df8e1d",
            error="#d20f39",
            dark=False,
        ),
        Theme(
            name="github-dark-contrast",
            primary="#74b9ff",
            secondary="#a371f7",
            accent="#f8e3a1",
            foreground="#ffffff",
            background="#010409",
            surface="#0d1117",
            panel="#151b23",
            success="#3fb950",
            warning="#d29922",
            error="#f85149",
            dark=True,
        ),
        Theme(
            name="github-light-contrast",
            primary="#0349b4",
            secondary="#6639ba",
            accent="#023b95",
            foreground="#010409",
            background="#ffffff",
            surface="#f6f8fa",
            panel="#eaeef2",
            success="#116329",
            warning="#7d4e00",
            error="#a40e26",
            dark=False,
        ),
    )
