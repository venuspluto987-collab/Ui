import streamlit as st
import numpy as np
import cv2
from PIL import Image
import io

# =========================
# CONFIG
# =========================
st.set_page_config(page_title="PRO AI Image Studio", layout="wide")

st.markdown("<h1 style='text-align:center;'>🧠 PRO AI Image Studio</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;color:gray;'>AI Erase • Background • Enhance (No Canvas Version)</p>", unsafe_allow_html=True)

# =========================
# UPLOAD
# =========================
uploaded_file = st.file_uploader("📤 Upload Image", type=["png", "jpg", "jpeg"])

# =========================
# SIDEBAR CONTROLS
# =========================
st.sidebar.title("⚙️ Controls")

feature = st.sidebar.radio(
    "Choose Tool",
    ["🎯 AI Erase", "🎨 Background Remove", "✨ Enhance"]
)

# =========================
# MAIN LOGIC
# =========================
if uploaded_file:

    image = Image.open(uploaded_file).convert("RGB")
    img_np = np.array(image)
    h, w = img_np.shape[:2]

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📸 Original Image")
        st.image(image, use_column_width=True)

    # =========================
    # GLOBAL MASK STATE
    # =========================
    if "mask" not in st.session_state:
        st.session_state.mask = np.zeros((h, w), dtype=np.uint8)

    # =========================
    # 🎯 AI ERASE (NO CANVAS)
    # =========================
    if feature == "🎯 AI Erase":

        st.sidebar.subheader("🎯 Brush Controls")
        brush = st.sidebar.slider("Brush Size", 5, 80, 20)

        st.sidebar.write("👉 Add points to erase area")

        x = st.sidebar.number_input("X coordinate", 0, w - 1, w // 2)
        y = st.sidebar.number_input("Y coordinate", 0, h - 1, h // 2)

        if st.sidebar.button("➕ Add Erase Point"):
            cv2.circle(st.session_state.mask, (x, y), brush, 255, -1)

        if st.sidebar.button("🧹 Reset Mask"):
            st.session_state.mask = np.zeros((h, w), dtype=np.uint8)

        st.image(st.session_state.mask, caption="Mask Preview (White = Remove Area)", clamp=True)

        if st.button("🚀 Apply AI Erase"):
            with st.spinner("Applying AI inpainting..."):

                result = cv2.inpaint(
                    img_np,
                    st.session_state.mask,
                    3,
                    cv2.INPAINT_TELEA
                )

            with col2:
                st.subheader("✨ Result")
                st.image(result, use_column_width=True)

            out = Image.fromarray(result)
            buf = io.BytesIO()
            out.save(buf, format="PNG")

            st.download_button(
                "📥 Download Result",
                buf.getvalue(),
                "ai_erased.png"
            )

    # =========================
    # 🎨 BACKGROUND REMOVAL
    # =========================
    elif feature == "🎨 Background Remove":

        color = st.sidebar.color_picker("Background Color", "#00ffaa")

        if st.sidebar.button("🚀 Remove Background"):
            with st.spinner("Processing..."):
                from rembg import remove

                cutout = remove(image)
                bg = Image.new("RGB", cutout.size, color)
                result = Image.alpha_composite(bg.convert("RGBA"), cutout.convert("RGBA"))

            with col2:
                st.subheader("✨ Result")
                st.image(result, use_column_width=True)

            buf = io.BytesIO()
            result.save(buf, format="PNG")

            st.download_button(
                "📥 Download",
                buf.getvalue(),
                "background_removed.png"
            )

    # =========================
    # ✨ ENHANCE IMAGE
    # =========================
    elif feature == "✨ Enhance":

        strength = st.sidebar.slider("Sharpness Level", 1, 5, 2)

        if st.sidebar.button("🚀 Enhance Image"):
            result = image

            for _ in range(strength):
                result = result.filter(Image.ImageFilter.SHARPEN)

            with col2:
                st.subheader("✨ Result")
                st.image(result, use_column_width=True)

            buf = io.BytesIO()
            result.save(buf, format="PNG")

            st.download_button(
                "📥 Download",
                buf.getvalue(),
                "enhanced.png"
            )

else:
    st.info("👈 Upload an image to start editing")

# =========================
# FOOTER
# =========================
st.markdown("<hr><p style='text-align:center;color:gray;'>Built with ❤️ using Streamlit + OpenCV AI</p>", unsafe_allow_html=True)

       
