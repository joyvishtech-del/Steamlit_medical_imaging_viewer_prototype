#Imaging Viewer Prototype

Window/Level • Zoom/Pan • ROI Quantification • Pixel Spacing Simulation

An interactive medical imaging viewer prototype built with Streamlit, simulating core PACS functionality including window/level adjustment, viewport navigation, ROI measurement, and real-world area calculation (mm²).

This project demonstrates foundational imaging platform concepts commonly used in radiology workstations and AI-enabled clinical workflows.

🎯 Project Overview

This application replicates essential imaging viewer capabilities using standard image formats (PNG/JPG) to simulate DICOM-style workflows:

• Intensity windowing (contrast control)
• Zoom and pan (viewport-based rendering)
• ROI drawing and quantification
• Pixel spacing simulation
• Real-world area computation (mm²)
• Intensity histogram analysis

The goal is to bridge clinical imaging concepts with interactive software design, demonstrating how imaging platforms process, display, and quantify pixel data.

🧠 Clinical Concepts Demonstrated

| Concept                  | Description                                                          |
| ------------------------ | -------------------------------------------------------------------- |
| Window / Level           | Adjusts visible intensity range for improved contrast interpretation |
| ROI (Region of Interest) | Enables localized quantitative analysis of selected tissue           |
| Pixel Spacing            | Converts pixel measurements into real-world units (mm)               |
| Viewport Rendering       | Simulates PACS-style zoom and pan behavior                           |
| Quantitative Imaging     | Computes intensity statistics and area metrics                       |

🚀 Key Features

🔎 Window / Level Control
• Adjustable window width and level center
• Real-time intensity remapping
• Contrast enhancement simulation

🔍 Zoom & Pan (PACS-like Viewport)
• 1x–5x zoom
• Viewport cropping for smooth navigation
• ROI coordinates accurately mapped back to original image space

📐 ROI Drawing & Quantification
• Draw rectangular ROI directly on the image
• Automatically computes:
• Mean intensity
• Standard deviation
• Min / Max intensity
• ROI width & height (pixels + mm)
• ROI area in mm²

📏 Pixel Spacing Simulation
• User-defined mm per pixel (X & Y)
• Enables real-world measurement calculation
• Mimics DICOM PixelSpacing behavior

📊 Intensity Histogram
• Visualizes distribution of intensities within ROI
• Useful for contrast and heterogeneity assessment

🛠 Tech Stack

Streamlit
NumPy
Pandas
Pillow
Matplotlib
streamlit-drawable-canvas
streamlit-js-eval (optional)

📦 Requirements

Python 3.11 (recommended)
pip
Virtual environment (venv)

All dependencies are listed in : 
    requirements.txt