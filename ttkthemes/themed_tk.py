"""
Author: RedFantom
License: GNU GPLv3
Copyright (c) 2017-2018 RedFantom
"""
# Standard Library
import os
# Project Modules
from ._tkinter import tk, ttk
from ._utils import get_fonts_directory
from ._widget import ThemedWidget


class ThemedTk(tk.Tk, ThemedWidget):
    """
    Tk child class that supports the themes supplied in this package

    A theme can be set upon initialization or during runtime. Can be
    used as a drop-in replacement for the normal Tk class. Additional
    options:

    - Toplevel background color
      Hooks into the Toplevel.__init__ function to set a default window
      background color in the options passed. The hook is not removed
      after the window is destroyed, which is by design because creating
      multiple Tk instances should not be done in the first place.

    - Tk background color
      Simply sets the background color of the Tkinter window to the
      default TFrame background color specified by the theme.
    """

    FONTS = {
        "adapta": "roboto"
    }

    def __init__(self, *args, **kwargs):
        """
        :param theme: Theme to set upon initialization. If theme is not
            available, fails silently.
        :param toplevel: Control Toplevel background color option
        :param background: Control Tk background color option
        :param fonts: Whether to enable the automatic change of default
            font selected for a theme
        """
        theme = kwargs.pop("theme", None)
        toplevel = kwargs.pop("toplevel", False)
        background = kwargs.pop("background", False)
        fonts = kwargs.pop("fonts", False)
        # Initialize as tk.Tk
        tk.Tk.__init__(self, *args, **kwargs)
        # Initialize as ThemedWidget
        ThemedWidget.__init__(self, self.tk)
        # Attempt to load extrafont and fonts in ./fonts
        try:
            self._load_fonts()
            self.font_support = True and fonts
        except (tk.TclError, ImportError):
            self.font_support = False
        # Set initial theme
        if theme is not None and theme in self.get_themes():
            self.set_theme(theme, toplevel, background)
        self.__init__toplevel = tk.Toplevel.__init__

    def set_theme(self, theme_name, toplevel=False, background=False):
        """Redirect the set_theme call to also set Tk background color"""
        ThemedWidget.set_theme(self, theme_name)
        style = ttk.Style(self)
        color = style.lookup("TFrame", "background", default="white")
        if background is True:
            self.config(background=color)
        if toplevel is True:
            self._setup_toplevel_hook(color)
        if theme_name in self.FONTS and self.font_support:
            style.configure(".", font=self.FONTS[theme_name])

    def _setup_toplevel_hook(self, color):
        """Setup Toplevel.__init__ hook for background color"""
        def __toplevel__(*args, **kwargs):
            kwargs.setdefault("background", color)
            self.__init__toplevel(*args, **kwargs)

        tk.Toplevel.__init__ = __toplevel__

    def _load_fonts(self):
        """Load the custom fonts using tkextrafonts if it is available"""
        import tkextrafont
        tkextrafont.load_extrafont(self)
        fonts_path = get_fonts_directory()
        for folder in os.listdir(fonts_path):
            font_path = os.path.join(fonts_path, folder)
            for file in os.listdir(font_path):
                if not file.endswith(".ttf"):
                    continue
                font = os.path.join(font_path, file)
                if not self.font_info(font):
                    print("Font not available: {}".format(file))
                    continue
                try:
                    self.load_font(font)
                except tk.TclError as e:
                    continue
