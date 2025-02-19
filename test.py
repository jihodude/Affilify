#!/usr/bin/env python3

import moviepy as mpe
import inspect

print("MoviePy path:", mpe.__file__)
print("TextClip signature:", inspect.signature(mpe.TextClip))

clip = mpe.TextClip(
    text="Hello",
    font="/System/Library/Fonts/Supplemental/Arial.ttf",
    fontsize=50,
    color="white"
)
clip.write_videofile("test_textclip.mp4", fps=1)
