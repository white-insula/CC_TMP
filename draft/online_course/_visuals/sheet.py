# -*- coding: utf-8 -*-
"""把若干节的配图拼成一张总览图,方便人工检查:python _visuals/sheet.py out.jpg 16 17 ..."""
import sys, os, glob, cv2, numpy as np
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
out, nos = sys.argv[1], sys.argv[2:]
tiles = []
for no in nos:
    for f in sorted(glob.glob(os.path.join(HERE, no, "img", "*.png"))):
        im = cv2.imdecode(np.fromfile(f, np.uint8), 1)
        t = np.full((360, 640, 3), 255, np.uint8)
        s = min(630 / im.shape[1], 320 / im.shape[0]); r = cv2.resize(im, None, fx=s, fy=s, interpolation=cv2.INTER_AREA)
        t[:r.shape[0], :r.shape[1]] = r
        cv2.putText(t, os.path.basename(f), (5, 352), 0, 0.7, (0, 0, 255), 2); tiles.append(t)
while len(tiles) % 3: tiles.append(np.full_like(tiles[0], 255))
g = np.vstack([np.hstack(tiles[i:i + 3]) for i in range(0, len(tiles), 3)])
cv2.imwrite(out, g); print(len(tiles), "tiles")
