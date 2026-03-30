import streamlit as st
import numpy as np
from PIL import Image, ImageFilter
import io

# =========================
# CONFIG
# =========================
st.set_page_config(page_title="AI Image Studio", layout="wide")

st.markdown("<h1 style='text-align:center;'>✨ AI Image Studio</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;color:gray;'>Background • Erase • Enhance</p>", unsafe_allow_html=True)

# =========================
# SIDEBAR
# =========================
st.sidebar.title("⚙️ Controls")

uploaded_file = st.sidebar.file_uploader("📤 Upload Image", type=["png", "jpg", "jpeg"])

feature = st.sidebar.radio(
    "Choose Tool",
    ["🎨 Background", "🎯 Erase", "✨ Enhance"]
)

# =========================
# MAIN
# =========================
col1, col2 = st.columns(2)

if uploaded_file:
    image = Image.open(uploaded_file).convert("RGBA")
    image.thumbnail((600, 600))

    with col1:
        st.subheader("📸 Original")
        st.image(image, use_column_width=True)

    # =========================
    # 🎨 BACKGROUND CHANGE
    # =========================
    if feature == "🎨 Background":
        st.sidebar.subheader("🎨 Background Settings")
        color = st.sidebar.color_picker("Pick Color", "#00ffaa")

        if st.sidebar.button("🚀 Apply Background"):
            with st.spinner("Removing background..."):
                from rembg import remove  # Lazy load (fix 503)

                cutout = remove(image)
                bg = Image.new("RGBA", cutout.size, color)
                result = Image.alpha_composite(bg, cutout)

            with col2:
                st.subheader("✅ Result")
                st.image(result, use_column_width=True)

            buf = io.BytesIO()
            result.save(buf, format="PNG")

            st.download_button("📥 Download", buf.getvalue(), "bg.png")

    # =========================
    # 🎯 ERASE OBJECT
    # =========================
    elif feature == "🎯 Erase":
        from streamlit_drawable_canvas import st_canvas  # Lazy load

        st.sidebar.subheader("🎯 Erase Settings")
        brush = st.sidebar.slider("Brush Size", 5, 30, 10)

        st.write("✍️ Draw on object to remove")

        canvas = st_canvas(
            fill_color="rgba(255,0,0,0.3)",
            stroke_width=brush,
            stroke_color="white",
            background_color="rgba(0,0,0,0)",
            height=image.height,
            width=image.width,
            drawing_mode="freedraw",
            key="canvas",
        )

        if canvas.image_data is not None:
            with st.spinner("Erasing..."):
                mask = canvas.image_data[:, :, 3] > 0
                img_array = np.array(image)

                img_array[mask] = [255, 255, 255, 0]

                result = Image.fromarray(img_array)

            with col2:
                st.subheader("✅ Result")
                st.image(result, use_column_width=True)

            buf = io.BytesIO()
            result.save(buf, format="PNG")

            st.download_button("📥 Download", buf.getvalue(), "erase.png")

    # =========================
    # ✨ BLUR REMOVAL
    # =========================
    elif feature == "✨ Enhance":
        st.sidebar.subheader("✨ Enhance Settings")
        strength = st.sidebar.slider("Sharpness", 1, 5, 2)

        if st.sidebar.button("🚀 Enhance"):
            with st.spinner("Enhancing image..."):
                result = image

                for _ in range(strength):
                    result = result.filter(ImageFilter.SHARPEN)

            with col2:
                st.subheader("✅ Result")
                st.image(result, use_column_width=True)

            buf = io.BytesIO()
            result.save(buf, format="PNG")

            st.download_button("📥 Download", buf.getvalue(), "sharp.png")

else:
    st.info("👈 Upload an image from the sidebar to start")

# =========================
# FOOTER
# =========================
st.markdown("<hr><p style='text-align:center;color:gray;'>Built with ❤️ using Streamlit</p>", unsafe_allow_html=True)
