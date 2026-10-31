# -*- coding: utf-8 -*-
"""部品見本の図"""
from figkit import *  # noqa: F401,F403

def line_split():
    b = arrow_defs("ls")
    b += '<line x1="20" y1="150" x2="300" y2="20" class="s-main"/>'
    for x, y in [(60, 40), (90, 70), (120, 45)]:
        b += f'<circle cx="{x}" cy="{y}" r="6" class="f-ou"/>'
    for x, y in [(200, 130), (240, 110), (260, 140)]:
        b += f'<circle cx="{x}" cy="{y}" r="6" class="f-link"/>'
    b += text(250, 30, "g(x)=0", "t-m f-ink2")
    return svg(320, 170, b, "直線で2つのクラスを分ける")
