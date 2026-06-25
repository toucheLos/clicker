#!/usr/bin/env bash
# Aim trainer — click the dot

for cmd in wish wish8.6 wish8.5; do
    command -v "$cmd" &>/dev/null && WISH="$cmd" && break
done
if [[ -z "${WISH:-}" ]]; then
    echo "Requires Tcl/Tk. Install: sudo apt install tk" >&2
    exit 1
fi

export CLICKER_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

"$WISH" <<'TCLEOF'
package require Tk

set config_file [file join $env(CLICKER_DIR) clicker.conf]
set ss_file "/tmp/.aim_trainer_bg.png"

set dot_color "#ff3333"
set dot_size 30
set hits 0
set active 0

# ── Config ──────────────────────────────────────────────

proc load_config {} {
    global config_file dot_color dot_size
    if {![file exists $config_file]} return
    set f [open $config_file r]
    while {[gets $f line] >= 0} {
        if {[regexp {^(\w+)=(.+)$} $line -> k v]} {
            switch $k {
                color { set dot_color $v }
                size  { set dot_size [expr {int($v)}] }
            }
        }
    }
    close $f
}

proc save_config {} {
    global config_file dot_color dot_size
    set f [open $config_file w]
    puts $f "color=$dot_color"
    puts $f "size=$dot_size"
    close $f
}

# ── Screenshot ──────────────────────────────────────────

proc take_screenshot {} {
    global ss_file
    catch {file delete $ss_file}
    if {![catch {exec scrot $ss_file 2>/dev/null}] && [file exists $ss_file]} return
    if {![catch {exec import -window root $ss_file 2>/dev/null}] && [file exists $ss_file]} return
    if {![catch {exec maim $ss_file 2>/dev/null}] && [file exists $ss_file]} return
    if {![catch {exec gnome-screenshot -f $ss_file 2>/dev/null}] && [file exists $ss_file]} return
}

# ── Dot ─────────────────────────────────────────────────

proc respawn_dot {} {
    global dot_color dot_size
    set sw [winfo screenwidth .]
    set sh [winfo screenheight .]
    set margin [expr {$dot_size + 50}]
    set x [expr {int($margin + rand() * ($sw - 2 * $margin))}]
    set y [expr {int($margin + rand() * ($sh - 2 * $margin))}]
    set r [expr {$dot_size / 2}]

    .c delete dot
    .c create oval \
        [expr {$x - $r}] [expr {$y - $r}] \
        [expr {$x + $r}] [expr {$y + $r}] \
        -fill $dot_color -outline $dot_color -tag dot

    .c raise hud
}

proc update_hud {} {
    global hits
    .c delete hud
    .c create text 22 27 -anchor w -text "Hits: $hits" \
        -fill black -font {{Courier} 14 bold} -tag hud
    .c create text 20 25 -anchor w -text "Hits: $hits" \
        -fill white -font {{Courier} 14 bold} -tag hud
    .c create text 22 49 -anchor w \
        -text "Esc = pause    F1 = settings" \
        -fill black -font {{Courier} 10} -tag hud
    .c create text 20 47 -anchor w \
        -text "Esc = pause    F1 = settings" \
        -fill "#999999" -font {{Courier} 10} -tag hud
}

proc on_dot_click {} {
    global hits
    incr hits
    update_hud
    respawn_dot
    catch { .ctrl.stats configure -text "Hits: $hits" }
}

# ── Overlay ─────────────────────────────────────────────

proc show_overlay {} {
    global active ss_file

    catch { wm withdraw .ctrl }
    catch { destroy .settings_win }
    update
    after 200

    take_screenshot

    .c delete bg
    if {[file exists $ss_file]} {
        catch { image delete bg_img }
        if {![catch {image create photo bg_img -file $ss_file}]} {
            .c create image 0 0 -anchor nw -image bg_img -tag bg
        }
    }
    .c lower bg

    set active 1
    wm deiconify .
    wm attributes . -fullscreen 1 -topmost 1
    focus -force .c

    respawn_dot
    update_hud
}

proc hide_overlay {} {
    global active
    set active 0
    wm attributes . -fullscreen 0 -topmost 0
    wm withdraw .

    catch { wm deiconify .ctrl }
    catch { raise .ctrl }
    catch { focus .ctrl }
}

# ── Control panel ───────────────────────────────────────

proc create_control {} {
    global hits

    toplevel .ctrl
    wm title .ctrl "Aim Trainer"
    wm geometry .ctrl 300x180
    wm protocol .ctrl WM_DELETE_WINDOW exit
    wm resizable .ctrl 0 0
    .ctrl configure -bg "#1e1e2e"

    label .ctrl.title -text "Aim Trainer" \
        -bg "#1e1e2e" -fg "#cdd6f4" -font {{Helvetica} 18 bold}
    pack .ctrl.title -pady {20 5}

    label .ctrl.stats -text "Hits: $hits" \
        -bg "#1e1e2e" -fg "#89b4fa" -font {{Courier} 13}
    pack .ctrl.stats -pady 8

    frame .ctrl.btns -bg "#1e1e2e"
    pack .ctrl.btns -pady 15

    button .ctrl.btns.resume -text " Resume " -command show_overlay \
        -bg "#a6e3a1" -fg "#1e1e2e" -relief flat \
        -activebackground "#94e2d5" -font {{Helvetica} 11 bold}
    button .ctrl.btns.settings -text " Settings " -command open_settings \
        -bg "#45475a" -fg "#cdd6f4" -relief flat \
        -activebackground "#585b70" -font {{Helvetica} 11}
    button .ctrl.btns.quit -text " Quit " -command exit \
        -bg "#f38ba8" -fg "#1e1e2e" -relief flat \
        -activebackground "#eba0ac" -font {{Helvetica} 11}

    pack .ctrl.btns.resume .ctrl.btns.settings .ctrl.btns.quit \
        -side left -padx 4

    bind .ctrl <Return> show_overlay
    wm withdraw .ctrl
}

# ── Settings ────────────────────────────────────────────

proc open_settings {} {
    global dot_color dot_size

    if {[winfo exists .settings_win]} {
        raise .settings_win
        focus .settings_win
        return
    }

    toplevel .settings_win
    wm title .settings_win "Settings"
    wm geometry .settings_win 320x220
    wm resizable .settings_win 0 0
    .settings_win configure -bg "#1e1e2e"

    label .settings_win.title -text "Settings" \
        -bg "#1e1e2e" -fg "#cdd6f4" -font {{Helvetica} 16 bold}
    pack .settings_win.title -pady {15 10}

    # Size
    frame .settings_win.sf -bg "#1e1e2e"
    pack .settings_win.sf -fill x -padx 20 -pady 5
    label .settings_win.sf.l -text "Dot size:" \
        -bg "#1e1e2e" -fg "#cdd6f4" -font {{Helvetica} 11}
    label .settings_win.sf.v -text "$dot_size" \
        -bg "#1e1e2e" -fg "#cba6f7" -font {{Courier} 11 bold} -width 4
    pack .settings_win.sf.l -side left
    pack .settings_win.sf.v -side right

    scale .settings_win.slider -from 10 -to 100 -orient horizontal \
        -variable dot_size -showvalue 0 \
        -bg "#1e1e2e" -fg "#cdd6f4" -troughcolor "#45475a" \
        -activebackground "#cba6f7" -highlightthickness 0 \
        -command on_size_change
    pack .settings_win.slider -fill x -padx 20

    # Color
    frame .settings_win.cf -bg "#1e1e2e"
    pack .settings_win.cf -fill x -padx 20 -pady {15 5}
    label .settings_win.cf.l -text "Dot color:" \
        -bg "#1e1e2e" -fg "#cdd6f4" -font {{Helvetica} 11}
    frame .settings_win.cf.preview -width 28 -height 28 -bg $dot_color
    button .settings_win.cf.pick -text "Pick color" -command pick_color \
        -bg "#45475a" -fg "#cdd6f4" -relief flat \
        -activebackground "#585b70" -font {{Helvetica} 10}
    pack .settings_win.cf.l -side left
    pack .settings_win.cf.pick -side right
    pack .settings_win.cf.preview -side right -padx 8

    button .settings_win.close -text "Close" \
        -command {destroy .settings_win} \
        -bg "#45475a" -fg "#cdd6f4" -relief flat -padx 10 \
        -activebackground "#585b70" -font {{Helvetica} 10}
    pack .settings_win.close -pady 15
}

proc on_size_change {val} {
    global dot_size
    set dot_size [expr {int($val)}]
    catch { .settings_win.sf.v configure -text $dot_size }
    save_config
}

proc pick_color {} {
    global dot_color
    set c [tk_chooseColor -initialcolor $dot_color -title "Dot Color"]
    if {$c ne ""} {
        set dot_color $c
        catch { .settings_win.cf.preview configure -bg $dot_color }
        save_config
    }
}

# ── Main window ─────────────────────────────────────────

wm withdraw .
wm title . "Aim Trainer"
wm protocol . WM_DELETE_WINDOW hide_overlay

canvas .c -highlightthickness 0 -cursor crosshair -bg "#1a1a2e"
pack .c -fill both -expand 1

.c bind dot <Button-1> {on_dot_click}
bind . <Escape> hide_overlay
bind . <F1> { hide_overlay; open_settings }

# ── Start ───────────────────────────────────────────────

expr {srand([clock clicks])}
load_config
create_control
show_overlay
TCLEOF
