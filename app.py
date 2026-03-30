import streamlit as st
import numpy as np
from PIL import Image, ImageFilter
import io

# =========================
# 🔧 PATCH (FIX CANVAS CRASH)
# =========================
if not hasattr(st.image, "image_to_url"):
    def image_to_url(img, width=None):
        import base64
        from io import BytesIO

        buffer = BytesIO()
        img.save(buffer, format="PNG")
        return "data:image/png;base64," + base64.b64encode(buffer.getvalue()).decode()

    st.image.image_to_url = image_to_url


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
# MAIN UI
# =========================
col1, col2 = st.columns(2)

if uploaded_file:
    image = Image.open(uploaded_file).convert("RGBA")
    image.thumbnail((600, 600))

    with col1:
        st.subheader("📸 Original")
        st.image(image, use_column_width=True)

    # =========================
    # 🎨 BACKGROUND REMOVE
    # =========================
    if feature == "🎨 Background":
        st.sidebar.subheader("🎨 Background Settings")
        color = st.sidebar.color_picker("Pick Color", "#00ffaa")

        if st.sidebar.button("🚀 Apply Background"):
            with st.spinner("Removing background..."):
                from rembg import remove

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
        from streamlit_drawable_canvas import st_canvas

        st.sidebar.subheader("🎯 Erase Settings")
        brush = st.sidebar.slider("Brush Size", 5, 25, 10)

        st.write("✍️ Draw on the image to mark area for erase")

        canvas = st_canvas(
            fill_color="rgba(255, 0, 0, 0.3)",
            stroke_width=brush,
            background_image=image,
            update_streamlit=True,
            height=image.height,
            width=image.width,
            drawing_mode="freedraw",
            key="canvas",
        )

        if canvas.image_data is not None:
            with st.spinner("Processing erase..."):
                img_array = np.array(image)

                # alpha channel mask
                mask = canvas.image_data[:, :, 3] > 0

                # ✨ simple erase (transparent)
                img_array[mask] = [255, 255, 255, 0]

                result = Image.fromarray(img_array)

            with col2:
                st.subheader("✅ Result")
                st.image(result, use_column_width=True)

            buf = io.BytesIO()
            result.save(buf, format="PNG")
            st.download_button("📥 Download", buf.getvalue(), "erase.png")

    # =========================
    # ✨ ENHANCE IMAGE
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
   
           
