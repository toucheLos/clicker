# Clicker aim trainer alias for ~/.bash_aliases.
#
# Usage:
#   source ~/.bash_aliases
#   clicker

clicker() {
    local app_dir="$HOME/clicker"
    local venv_dir="$app_dir/.venv"

    if [ ! -d "$venv_dir" ]; then
        python3 -m venv "$venv_dir" || return
        "$venv_dir/bin/python" -m pip install --upgrade pip || return
        "$venv_dir/bin/python" -m pip install -r "$app_dir/requirements.txt" || return
    fi

    (
        cd "$app_dir" || exit
        "$venv_dir/bin/python" clicker.py
    )
}
