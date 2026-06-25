# Clicker Aim Trainer

Clicker is a lightweight CS2-inspired aim trainer overlay. It drops a target on your screen so you can practice fast, accurate clicks in a familiar FPS-style rhythm.

The app includes:

- Free play mode for open-ended warmups.
- Challenge mode with 10, 25, 50, and 100 hit goals.
- Local high scores saved by target count.
- Configurable target size, color, outline, texture, and overlay dimming.

## Setup

```bash
cd ~/clicker
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python clicker.py
```

## Shell Alias (optional)

Add the following to `~/.bash_aliases` so you can launch the trainer from anywhere by typing `clicker`:

```bash
source ~/clicker/clicker_aliases.sh
```

Then reload your shell:

```bash
source ~/.bash_aliases
```
And start the application with:

```
clicker
```


## Controls

- **Left click** — shoot the dot. Hits score a point; misses are tracked separately.
- **Esc** — return to the settings window while the overlay is active.
- **Enter** — start a round from the settings window.

## Settings

### Circle
- **Size** (10–120) — diameter of the target dot in pixels.
- **Style** — dot texture: `solid`, `gradient`, `bullseye`, `crosshair`, or `glow` (animated pulse).
- **Color** — fill color of the dot.

### Outline
- **Show outline** — toggle a ring around the dot.
- **Width** (1–8) — outline thickness in pixels.
- **Color** — outline color.

### Overlay
- **Dim** (0–120) — fills the entire screen with a semi-transparent black layer behind the dot. This dims whatever is on your screen (desktop, game, browser, etc.) so the dot is easier to see. At 0 the background is fully transparent (no dimming); higher values apply a darker tint.

### Game Mode
- **Free Play** — open-ended practice with no target count.
- **Challenge** — race to hit 10, 25, 50, or 100 targets as fast as possible. Times and accuracy are saved to the local scoreboard.

<img width="425" height="703" alt="image" src="https://github.com/user-attachments/assets/e3ed73c5-46be-4c69-8ad3-565d818e1a5b" />
<img width="1656" height="1525" alt="image" src="https://github.com/user-attachments/assets/88056ad9-eada-492c-be41-f4cf12062b19" />

"credit the idea of adding a screenshot to @focusederror" - PapaJuans
