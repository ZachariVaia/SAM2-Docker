# 👀 Segment Anything 2 + Docker — Point GUIs 🐳

![image](https://github.com/user-attachments/assets/7911d7b8-72a7-4c90-9da6-7a867b0136f8)

Segment Anything 2 in Docker, with **interactive point selection** (POS/NEG) via **Web GUI (Gradio)** or **native matplotlib GUI**.
Built on top of Meta’s SAM2: [https://github.com/facebookresearch/segment-anything-2](https://github.com/facebookresearch/segment-anything-2)

**🆕 New:** Web GUI for clicking points in your browser — no X11 needed.

---

## Quickstart

These steps assume an NVIDIA GPU with drivers installed and Docker available.

Install the NVIDIA Container Toolkit:

```bash
distribution=$(. /etc/os-release;echo $ID$VERSION_ID) \
  && curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add - \
  && curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | \
     sudo tee /etc/apt/sources.list.d/nvidia-docker.list
sudo apt-get update
sudo apt-get install -y nvidia-docker2
sudo systemctl restart docker
```

Clone this repo, build the image, and run:

```bash
# from the repo root
docker build -t sam2:local .
```

### Run with Web GUI (recommended)

Put your images under `data/<dataset_name>/` (you can use a subfolder like `images/`), then:

```bash
# first image only
WEB_GUI=1 ./run_sam2.sh <dataset_name>

# all images
WEB_GUI=1 WEB_GUI_MODE=all ./run_sam2.sh <dataset_name>

# custom port (default 7860)
GRADIO_PORT=7870 WEB_GUI=1 ./run_sam2.sh <dataset_name>
```

Open `http://localhost:<port>` (e.g., `http://localhost:7860`), click points, **Finish & Run**, and the predictor will generate masks.

### Native GUI (optional; needs X11)

If you prefer a native window:

```bash
# first image only
GUI=1 ./run_sam2.sh <dataset_name>

# all images
GUI=1 GUI_MODE=all ./run_sam2.sh <dataset_name>
```

> For native GUI, we mount `/tmp/.X11-unix` and pass `DISPLAY` automatically in the script.

---

## Running the Example

Minimal end-to-end test:

```bash
# 1) Prepare data
mkdir -p data/human_test3/images
# copy a few .jpg/.png images into data/human_test3/images

# 2) Build the docker image
docker build -t sam2:local .

# 3) Pick points in the browser for the first image and run predictor
WEB_GUI=1 ./run_sam2.sh human_test3
# -> open http://localhost:7860, click POS/NEG, press "Finish & Run"
```

Outputs will be written to `outputs/human_test3/...`.

---

## Sidecar Point Formats

The script looks for points in this priority:

1. **Beside the image**: `image_001.points.json|csv|npy`
2. `data/<dataset>/points/<relative_path>.json|csv|npy`
3. `data/<dataset>/points.json` (global map)

**JSON (recommended)**

```json
{
  "points": [[x, y, 1], [x2, y2, 0], [x3, y3, 1]]
}
```

Also supported:

```json
[[x, y, 1], [x2, y2, 0]]
```

or

```json
{"pos": [[x,y], [x2,y2]], "neg": [[x3,y3]]}
```

* Labels: `1` = foreground (POS), `0` = background (NEG)
* Coordinates are `(x, y)` in **image pixel** space.

**CSV**

```
x,y,label
120,340,1
420,360,0
```

---

## What Gets Produced

For each image you’ll find under `outputs/<dataset_name>/...`:

* `*_mask.png` — binary mask (255 = object)
* `*_overlay.png` — image + green mask overlay + POS/NEG markers
* `*_meta.json` — metadata (checkpoint, config, points used, etc.)

Example:

```
outputs/<dataset_name>/
└─ images/
   ├─ 00000000_mask.png
   ├─ 00000000_overlay.png
   └─ 00000000_meta.json
```

---

## How the Predictor Works (multi-point like the Colab)

* With **one** point → `multimask_output=True`, keep the highest-scoring mask.
* With **multiple** points → 2 stages:

  1. Seed with one positive point to obtain `logits`
  2. Refine with **all** points + `mask_input`, `multimask_output=False`

If no points are found, it **falls back** to a POS point at the image center.

---

## Project Layout

```
repo/
├─ Dockerfile
├─ run_sam2.sh
├─ data/
│  └─ <dataset_name>/
│     ├─ images/...
│     ├─ points/                # optional mirrors of image paths (JSON/CSV/NPY)
│     └─ points.json            # optional global map
└─ outputs/
```

---

## Troubleshooting

* **Web GUI doesn’t open** → use another port: `GRADIO_PORT=7870 WEB_GUI=1 ./run_sam2.sh <dataset>`
* **Headless / remote machines** → prefer the **Web GUI** (no X11 needed).
* **Native GUI errors (X11/backends)** → use Web GUI or install a proper Tk/Qt backend in the image.
* **Matplotlib cache warning** (`/.config/matplotlib not writable`) → harmless for Web GUI; for native GUI set `MPLCONFIGDIR=/tmp/mplconfig`.
* **No images found** → ensure your files are under `data/<dataset_name>/` (optionally in `images/`).

---

## Credits

* Meta AI — [Segment Anything 2](https://github.com/facebookresearch/segment-anything-2)
* This repo wraps SAM2 in a convenient Docker + GUI workflow for fast point-prompted segmentation.
