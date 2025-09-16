import argparse, os, glob, json
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt

EXTS = ("*.jpg","*.jpeg","*.png","*.bmp","*.tif","*.tiff")

def find_images(root):
    imgs=[]
    for e in EXTS:
        imgs+=glob.glob(os.path.join(root, "**", e), recursive=True)
    return sorted(imgs)

class Annotator:
    def __init__(self, img_path):
        self.img_path = img_path
        self.im = Image.open(img_path).convert("RGB")
        self.arr = np.array(self.im)
        self.points = []  # [x,y,label]
        self.fig, self.ax = plt.subplots(figsize=(10,10))
        self.ax.imshow(self.arr)
        self.ax.set_title(os.path.basename(img_path))
        self.ax.axis("on")
        self._pos_scatter = None
        self._neg_scatter = None
        self.cid_click = self.fig.canvas.mpl_connect("button_press_event", self.on_click)
        self.cid_key   = self.fig.canvas.mpl_connect("key_press_event", self.on_key)
        self.redraw()

    def redraw(self):
        pos = np.array([[x,y] for x,y,l in self.points if l==1], dtype=float) if any(l==1 for *_,l in self.points) else np.empty((0,2))
        neg = np.array([[x,y] for x,y,l in self.points if l==0], dtype=float) if any(l==0 for *_,l in self.points) else np.empty((0,2))
        self.ax.collections.clear()
        if len(pos): self.ax.scatter(pos[:,0], pos[:,1], marker="+", s=100, linewidths=2)
        if len(neg): self.ax.scatter(neg[:,0], neg[:,1], marker="x", s=100, linewidths=2)
        self.ax.figure.canvas.draw_idle()

    def on_click(self, event):
        if event.inaxes != self.ax: return
        if event.button==1: label=1   # left click = positive
        elif event.button==3: label=0 # right click = negative
        else: return
        x,y = float(event.xdata), float(event.ydata)
        self.points.append([x,y,label])
        self.redraw()

    def on_key(self, event):
        if event.key == "u":          # undo
            if self.points: self.points.pop(); self.redraw()
        elif event.key == "r":        # reset
            self.points.clear(); self.redraw()
        elif event.key == "s":        # save
            self.save()
        elif event.key in ("q","escape"):  # quit window
            plt.close(self.fig)
        elif event.key == "h":
            print("[h] βοήθεια: left=+  right=-  u=undo  r=reset  s=save  q=quit")

    def save(self):
        base = os.path.splitext(self.img_path)[0]
        out_path = base + ".points.json"
        data = {"points": [[float(x),float(y),int(l)] for x,y,l in self.points]}
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"[saved] {out_path}  ({len(self.points)} points)")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dataset_dir", help="π.χ. /data/myset")
    ap.add_argument("--first-only", action="store_true", help="άνοιξε μόνο την πρώτη εικόνα")
    args = ap.parse_args()

    imgs = find_images(args.dataset_dir)
    if not imgs:
        print(f"No images under {args.dataset_dir}")
        return

    if args.first_only:
        Annotator(imgs[0]); plt.show()
    else:
        for p in imgs:
            print(f"Annotating: {p}")
            ann = Annotator(p)
            plt.show()  # μπλοκάρει μέχρι να κλείσεις το παράθυρο
            # αν δεν έκανες save με [s], σώσε αυτόματα:
            if ann.points:
                ann.save()

if __name__ == "__main__":
    main()
