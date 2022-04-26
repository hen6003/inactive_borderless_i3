#!/usr/bin/python

# This script requires i3ipc-python package (install it from a system package manager
# or pip).
# It makes inactive windows borderless. Use `border_size_val` variable to control
# or use the command line argument -s.

import argparse
import i3ipc
import signal
import sys
from functools import partial

def on_window_focus(active_border_size, ipc, event):
    global prev_focused
    global prev_workspace

    focused_workspace = ipc.get_tree().find_focused()

    if focused_workspace == None:
        return

    focused = event.container
    workspace = focused_workspace.workspace().num

    if focused.id != prev_focused.id:  # https://github.com/swaywm/sway/issues/2859
        focused.command("border pixel " + active_border_size)
        if workspace == prev_workspace:
            prev_focused.command("border pixel 0")
        prev_focused = focused
        prev_workspace = workspace


def remove_border_size(ipc, active_border_size):
    for workspace in ipc.get_tree().workspaces():
        for w in workspace:
            w.command("border pixel " + active_border_size)
    ipc.main_quit()
    sys.exit(0)


if __name__ == "__main__":
    border_size_val = "1"

    parser = argparse.ArgumentParser(
        description="This script allows you to hide the border of focused windows in sway."
    )
    parser.add_argument(
        "--border_size",
        "-s",
        type=str,
        default=border_size_val,
        help="set border size value",
    )
    args = parser.parse_args()

    ipc = i3ipc.Connection()
    prev_focused = None
    prev_workspace = ipc.get_tree().find_focused().workspace().num

    for window in ipc.get_tree():
        if window.focused:
            prev_focused = window
        else:
            window.command("border pixel 0")
    for sig in [signal.SIGINT, signal.SIGTERM]:
        signal.signal(sig, lambda signal, frame: remove_border_size(ipc, args.border_size))
    ipc.on("window::focus", partial(on_window_focus, args.border_size))
    ipc.main()
