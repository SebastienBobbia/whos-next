#!/usr/bin/env python3
"""
Who's Next? — Daily Meeting Speaker Tracker

Application de bureau pour suivre qui a parlé et qui reste
pendant les daily meetings / stand-ups.

Usage:
    python main.py
"""

from ui.main_window import MainWindow


def main():
    app = MainWindow()
    app.mainloop()


if __name__ == "__main__":
    main()
