import streamlit as st
import numpy as np
import pandas as pd
from PIL import Image
import matplotlib.pyplot as plt
from streamlit_drawable_canvas import st_canvas

# Optional: true responsive width
try:
    from streamlit_js_eval import streamlit_js_eval
    HAS_JS_EVAL = True
except Exception:
    HAS_JS_EVAL = False

st.set_page_config(page_title="Imaging Window/Level + ROI Playground", layout="wide")

st.title("V's Imaging Window/Level + ROI Measurement Playground")
st.caption("Upload a PNG/JPG slice. Adjust Window/Level. Zoom/Pan like PACS. Draw ROI and get stats + mm² area (pixel spacing simulated).")

# -----------------------------
# Clinical terminology (Quick help)
# -----------------------------
with st.expander("📘 Quick clinical terminology (simple explanations)", expanded=False):
    st.markdown(
        """
**Window / Level (W/L)**  
- **Level** = center brightness you focus on  
- **Window** = intensity range shown around that level  
- Smaller window → higher contrast; Larger window → lower contrast

**ROI (Region of Interest)**  
- A selected area used to measure intensity values (e.g., lesion density / texture proxy)

**Pixel spacing (mm/pixel)**  
- In real DICOM CT/MR, each pixel corresponds to a real-world size (e.g., 0.7 mm).  
- Here we simulate it so ROI area can be computed in **mm²**.
        """
    )

# -----------------------------
# Helpers
# -----------------------------
def to_grayscale_np(pil_img: Image.Image) -> np.ndarray:
    gray = pil_img.convert("L")
    return np.array(gray).astype(np.float32)

def apply_window_level(img: np.ndarray, window: float, level: float) -> np.ndarray:
    window = max(float(window), 1.0)
    low = level - (window / 2.0)
    high = level + (window / 2.0)
    clipped = np.clip(img, low, high)
    scaled = (clipped - low) / (high - low) * 255.0
    return scaled.astype(np.uint8)

def make_demo_image(h=512, w=512) -> np.ndarray:
    y = np.linspace(-1, 1, h)[:, None]
    x = np.linspace(-1, 1, w)[None, :]
    base = 120 + 40 * (1 - (x**2 + y**2))
    blob1 = 60 * np.exp(-((x + 0.35) ** 2 + (y + 0.1) ** 2) / 0.02)
    blob2 = 80 * np.exp(-((x - 0.15) ** 2 + (y - 0.2) ** 2) / 0.01)
    noise = np.random.normal(0, 6, (h, w))
    return (base + blob1 + blob2 + noise).clip(0, 255).astype(np.float32)

def clamp(v, lo, hi):
    return max(lo, min(int(v), hi))

def get_responsive_width(default=900):
    """
    True responsive width if streamlit-js-eval is installed.
    Falls back to a slider otherwise.
    """
    if HAS_JS_EVAL:
        w = streamlit_js_eval(js_expressions="window.innerWidth", key="WIN_WIDTH", want_output=True)
        if isinstance(w, (int, float)) and w > 0:
            # Use ~55% of viewport width for viewer column
            return int(min(max(480, w * 0.55), 1100))
    # Fallback manual control
    return st.sidebar.slider("Viewer width (fallback)", 480, 1100, default, 10)

# -----------------------------
# Sidebar controls
# -----------------------------
st.sidebar.header("Controls")
uploaded = st.sidebar.file_uploader("Upload an image (PNG/JPG)", type=["png", "jpg", "jpeg"])
use_demo = st.sidebar.checkbox("Use demo image", value=(uploaded is None))

# Pixel spacing simulation (mm / pixel)
st.sidebar.subheader("Pixel spacing (simulate DICOM mm/pixel)")
px_x_mm = st.sidebar.number_input("Pixel spacing X (mm/px)", min_value=0.1, max_value=5.0, value=0.70, step=0.05)
px_y_mm = st.sidebar.number_input("Pixel spacing Y (mm/px)", min_value=0.1, max_value=5.0, value=0.70, step=0.05)

if use_demo:
    img_np = make_demo_image()
    source_name = "Demo synthetic slice"
else:
    if uploaded is None:
        st.info("Upload an image or enable demo image.")
        st.stop()
    pil = Image.open(uploaded)
    img_np = to_grayscale_np(pil)
    source_name = uploaded.name

# Window/Level defaults based on image stats
default_level = float(np.mean(img_np))
default_window = float(np.std(img_np) * 4 + 1)

st.sidebar.subheader("Window / Level")
window = st.sidebar.slider("Window (width)", 1.0, 512.0, float(min(512.0, default_window)), 1.0)
level = st.sidebar.slider("Level (center)", 0.0, 255.0, float(np.clip(default_level, 0, 255)), 1.0)

wl_img = apply_window_level(img_np, window=window, level=level)
H, W = wl_img.shape

# -----------------------------
# Zoom / Pan controls (crop-based viewport)
# -----------------------------
st.sidebar.subheader("Zoom / Pan (PACS-like viewport)")
zoom = st.sidebar.slider("Zoom", 1.0, 5.0, 1.0, 0.1)

# Viewport size in original pixels
view_w = int(W / zoom)
view_h = int(H / zoom)

# Pan center (in original pixel coordinates)
cx = st.sidebar.slider("Pan X (center)", 0, W - 1, W // 2, 1)
cy = st.sidebar.slider("Pan Y (center)", 0, H - 1, H // 2, 1)

# Compute crop bounds (top-left x0,y0)
x0 = clamp(cx - view_w // 2, 0, max(0, W - view_w))
y0 = clamp(cy - view_h // 2, 0, max(0, H - view_h))
x1 = x0 + view_w
y1 = y0 + view_h

# Crop the WL image to create the current view
view_img = wl_img[y0:y1, x0:x1]
view_rgb = np.stack([view_img, view_img, view_img], axis=-1)

# -----------------------------
# Responsive display sizing (no distortion)
# -----------------------------
display_width = get_responsive_width(default=900)
scale = display_width / view_w  # scale from original-view pixels to display pixels
display_height = int(view_h * scale)

# -----------------------------
# Layout
# -----------------------------
col1, col2 = st.columns([1.3, 1])

with col1:
    st.subheader("Viewer (Zoom/Pan + Draw ROI)")
    st.write(f"**Source:** {source_name} | **Original:** {W}×{H} | **View:** {view_w}×{view_h} | **Zoom:** {zoom:.1f}×")

    st.markdown("**How to use:** zoom/pan using sidebar → draw a rectangle ROI on the current view.")

    canvas_result = st_canvas(
        fill_color="rgba(255, 0, 0, 0.15)",
        stroke_width=2,
        stroke_color="#FF0000",
        background_image=Image.fromarray(view_rgb),
        update_streamlit=True,
        height=display_height,
        width=display_width,
        drawing_mode="rect",
        key="canvas",
    )

with col2:
    st.subheader("ROI Measurements")
    roi_stats_shown = False

    if canvas_result.json_data is not None:
        objects = canvas_result.json_data.get("objects", [])
        if len(objects) > 0:
            rect = objects[-1]
            if rect.get("type") == "rect":
                # Rectangle in DISPLAY coordinates
                left = float(rect.get("left", 0))
                top = float(rect.get("top", 0))
                rw = float(rect.get("width", 0))
                rh = float(rect.get("height", 0))

                # Convert DISPLAY -> VIEW pixels
                vx1 = int(left / scale)
                vy1 = int(top / scale)
                vx2 = int((left + rw) / scale)
                vy2 = int((top + rh) / scale)

                # Clamp within VIEW bounds
                vx1 = clamp(vx1, 0, view_w - 1)
                vy1 = clamp(vy1, 0, view_h - 1)
                vx2 = clamp(vx2, 0, view_w)
                vy2 = clamp(vy2, 0, view_h)

                if vx2 > vx1 and vy2 > vy1:
                    # Map VIEW -> ORIGINAL pixel coordinates by adding crop offset
                    ox1 = x0 + vx1
                    oy1 = y0 + vy1
                    ox2 = x0 + vx2
                    oy2 = y0 + vy2

                    roi = wl_img[oy1:oy2, ox1:ox2]

                    roi_w_px = ox2 - ox1
                    roi_h_px = oy2 - oy1

                    # Real-world measurements (mm) using simulated pixel spacing
                    roi_w_mm = roi_w_px * px_x_mm
                    roi_h_mm = roi_h_px * px_y_mm
                    roi_area_mm2 = roi_w_mm * roi_h_mm  # rectangle area

                    stats = {
                        "Mean": float(np.mean(roi)),
                        "Std": float(np.std(roi)),
                        "Min": float(np.min(roi)),
                        "Max": float(np.max(roi)),
                        "Pixels": int(roi.size),
                        "ROI Width (px)": int(roi_w_px),
                        "ROI Height (px)": int(roi_h_px),
                        "ROI Width (mm)": float(roi_w_mm),
                        "ROI Height (mm)": float(roi_h_mm),
                        "ROI Area (mm²)": float(roi_area_mm2),
                        "Top-left (orig x,y)": f"({ox1}, {oy1})",
                        "Bottom-right (orig x,y)": f"({ox2}, {oy2})",
                        "Pixel spacing (mm/px)": f"{px_x_mm:.2f} × {px_y_mm:.2f}",
                    }

                    st.metric("ROI Area (mm²)", f"{stats['ROI Area (mm²)']:.2f}")
                    st.metric("Mean Intensity", f"{stats['Mean']:.1f}")

                    st.write("**Detailed stats**")
                    st.dataframe(pd.DataFrame([stats]))

                    st.subheader("Histogram (ROI)")
                    fig = plt.figure()
                    plt.hist(roi.flatten(), bins=40)
                    plt.xlabel("Intensity (0–255 after W/L)")
                    plt.ylabel("Pixel count")
                    st.pyplot(fig, clear_figure=True)

                    roi_stats_shown = True

    if not roi_stats_shown:
        st.info("Draw a rectangle ROI on the image to see measurements here.")