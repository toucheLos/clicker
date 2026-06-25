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

## Controls

- `Esc` — return to the settings window while the overlay is active.
