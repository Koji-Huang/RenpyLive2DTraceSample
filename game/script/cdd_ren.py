"""renpy

init python:
"""

import pygame


# 显示 LOG 的 Frame
class LogFrame(renpy.Displayable):
    def __init__(self, target_log):
        super().__init__()
        self.log = target_log
        self.changed = False
        self.index = 0

    def render(self, w, h, st, at):
        rv = renpy.Render(w, h)
        text = Text("", color="ddf", size=30)

        if self.changed:
            self.changed = False
        else:
            self.index = 0
        
        yoffset = 0

        logs = self.log[:-self.index] if self.index else self.log

        for log in logs[::-1]:
            text.set_text(log)
            rend = text.render(w, h, st, at)
            yoffset += rend.get_size()[1]

            if yoffset > h:
                break

            rv.blit(rend, (0, h - yoffset))

        return rv
