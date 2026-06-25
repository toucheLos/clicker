# Clicker Aim Trainer

Clicker is a lightweight CS2-inspired aim trainer overlay. It drops a target on your screen so you can practice fast, accurate clicks in a familiar FPS-style rhythm.

The app includes:

- Free play mode for open-ended warmups.
- Challenge mode with 10, 25, 50, and 100 hit goals.
- Local high scores saved by target count.
- Configurable target size, color, outline, texture, and overlay dimming.

## Getting Started

Create and activate a virtual environment from the project directory:

```bash
cd ~/clicker
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Run the app:

```bash
python clicker.py
```

Press `Esc` while the overlay is active to return to the settings window.

## Shell Alias

This repo includes `clicker_aliases.sh`, a snippet intended for `~/.bash_aliases`. After it is loaded, you can start the trainer from anywhere with:

```bash
clicker
```

Reload your shell aliases after updating `~/.bash_aliases`:

```bash
source ~/.bash_aliases
```