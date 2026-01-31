import streamlit as st
import math
import random
import colorsys
from PIL import Image, ImageDraw
import io

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Based Checks | Studio", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. LUXURY CSS STYLING ---
st.markdown("""
<style>
    /* FONTS */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&family=Space+Grotesk:wght@300;500;700&display=swap');

    /* GLOBAL THEME */
    .stApp {
        background-color: #050505; 
        color: #EAEAEA;
        font-family: 'Inter', sans-serif;
    }

    /* TYPOGRAPHY */
    h1, h2, h3, h4 {
        font-family: 'Space Grotesk', sans-serif !important;
        font-weight: 700 !important;
        letter-spacing: -0.5px !important;
        color: #FFFFFF !important;
    }
    
    p, label, .stMarkdown, .stCaption, div {
        font-family: 'Inter', sans-serif !important;
        color: #CCCCCC;
    }

    /* SIDEBAR */
    [data-testid="stSidebar"] {
        background-color: #000000;
        border-right: 1px solid #1A1A1A;
    }

    /* WIDGETS */
    .stSlider [data-baseweb="slider"] { margin-top: 15px; }
    .stSelectbox div[data-baseweb="select"] > div {
        background-color: #0F0F0F;
        border: 1px solid #333;
        color: #FFF;
    }
    [data-testid="stFileUploader"] {
        background-color: #0A0A0A;
        border: 1px dashed #333;
        border-radius: 12px;
        padding: 30px;
    }

    /* LUXURY WHITE BUTTON */
    div.stButton > button {
        background: #FFFFFF !important;
        border: none;
        border-radius: 6px;
        padding: 0.75rem 1.5rem;
        width: 100%;
        box-shadow: 0 4px 20px rgba(255,255,255,0.05);
        transition: all 0.3s ease;
    }
    div.stButton > button p, div.stButton > button div {
        color: #000000 !important;
        font-family: 'Space Grotesk', sans-serif !important;
        font-weight: 800 !important;
        font-size: 15px !important;
        letter-spacing: 1px;
        text-transform: uppercase;
    }
    div.stButton > button:hover {
        background-color: #E0E0E0 !important;
        transform: translateY(-2px);
        box-shadow: 0 8px 30px rgba(255,255,255,0.2);
    }
    
    /* DOWNLOAD BUTTON */
    [data-testid="stDownloadButton"] > button {
        background: #111111 !important;
        border: 1px solid #333 !important;
    }
    [data-testid="stDownloadButton"] > button p {
        color: #FFFFFF !important;
    }
    [data-testid="stDownloadButton"] > button:hover {
        border-color: #FFF !important;
        background: #000 !important;
    }

    /* FOOTER ANIMATION */
    @keyframes neonCycle {
        0% { background-color: #FF3B30; box-shadow: 0 0 10px #FF3B30; }
        25% { background-color: #FFCC00; box-shadow: 0 0 10px #FFCC00; }
        50% { background-color: #32ADE6; box-shadow: 0 0 10px #32ADE6; }
        75% { background-color: #AF52DE; box-shadow: 0 0 10px #AF52DE; }
        100% { background-color: #FF2D55; box-shadow: 0 0 10px #FF2D55; }
    }
    .footer-container { display: flex; flex-direction: column; align-items: center; margin-top: 60px; margin-bottom: 40px; }
    .footer-checks { display: flex; gap: 12px; }
    .mini-check-box { width: 32px; height: 32px; border-radius: 6px; display: flex; align-items: center; justify-content: center; animation: neonCycle 4s infinite alternate; }
    .mini-check-icon { width: 18px; height: 18px; fill: #000000 !important; opacity: 0.9; }
    .d1 { animation-delay: 0.0s; } .d2 { animation-delay: 0.5s; } .d3 { animation-delay: 1.0s; } .d4 { animation-delay: 1.5s; } .d5 { animation-delay: 2.0s; }
    .footer-text { margin-top: 20px; font-size: 10px; letter-spacing: 2px; color: #444; text-transform: uppercase; }
</style>
""", unsafe_allow_html=True)

# --- HELPER FUNCTIONS ---
def hex_to_rgb(hex_color):
    h = hex_color.lstrip('#')
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def draw_manual_checkmark(draw_obj, cx, cy, size, color_rgb, thickness):
    scale = size * 0.4
    p1 = (cx - scale * 0.5, cy + scale * 0.1)
    p2 = (cx - scale * 0.1, cy + scale * 0.5)
    p3 = (cx + scale * 0.6, cy - scale * 0.6)
    draw_obj.line([p1, p2, p3], fill=color_rgb, width=int(thickness), joint="curve")

def process_image_to_grid(image, target_cols):
    w, h = image.size
    aspect_ratio = h / w
    target_rows = int(target_cols * aspect_ratio)
    img_small = image.resize((target_cols, target_rows), resample=Image.NEAREST)
    return img_small, target_rows

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("### 🎛 STUDIO CONTROLS")
    st.markdown("<br>", unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Upload Image", type=['jpg', 'jpeg', 'png'])
    
    st.markdown("---")
    st.caption("GRID SYSTEM")
    cols = st.slider("Grid Resolution", 10, 64, 24)
    check_ratio = st.slider("Thickness", 0.01, 0.25, 0.10, step=0.01)
    
    st.markdown("---")
    st.caption("ANIMATION ENGINE")
    pattern_type = st.selectbox(
        "Effect Pattern",
        [
            "Static (No Animation)", 
            "Vertical Wave (Moving Down)", 
            "Vertical Wave (Moving Up)", 
            "Diagonal (Top-Left to Bottom-Right)", 
            "Diagonal (Top-Right to Bottom-Left)",
            "Concentric Box (Center Out)"
        ]
    )

    if pattern_type != "Static (No Animation)":
        speed = st.slider("Wave Speed", 1.0, 10.0, 3.0)
        fps = st.slider("FPS", 5, 30, 15)
        total_frames = st.slider("Total Frames", 10, 60, 30)
    else:
        speed, fps, total_frames = 1.0, 1, 1

    st.markdown("---")
    st.caption("BASE PALETTE")
    c1, c2 = st.columns(2)
    with c1: bg_color = st.color_picker("Bg", "#000000")
    with c2: check_color = st.color_picker("Check", "#000000")

# --- MAIN CONTENT ---
st.markdown("<div style='text-align: center; margin-bottom: 40px;'>", unsafe_allow_html=True)
st.title("BASED CHECKS STUDIO")
st.caption("CREATE. ANIMATE. DOMINATE.")
st.markdown("</div>", unsafe_allow_html=True)

if uploaded_file is not None:
    image_source = Image.open(uploaded_file).convert("RGB")
    
    col1, col2 = st.columns([1, 1], gap="large")
    
    with col1:
        st.markdown("#### ORIGINAL SOURCE")
        st.image(image_source, use_container_width=True)
        img_grid, rows = process_image_to_grid(image_source, cols)
        
        st.markdown(f"""
            <div style="background:#0A0A0A; padding:15px; border-radius:8px; margin-top:20px; border:1px solid #222; font-size:12px;">
                <span style="color:#666">GRID:</span> <strong style="color:#FFF">{cols}x{rows}</strong> &nbsp;|&nbsp; 
                <span style="color:#666">MODE:</span> <strong style="color:#FFF">BLACK LOCK + WIDE WAVE</strong>
            </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("#### RENDER OUTPUT")
        
        btn_text = "RENDER STATIC PNG" if pattern_type == "Static (No Animation)" else "RENDER ANIMATION GIF"
        
        if st.button(btn_text):
            status_box = st.empty()
            prog_bar = st.progress(0)
            
            # Canvas
            slot_size = 50 
            canvas_w = cols * slot_size
            canvas_h = rows * slot_size
            padding = 6
            check_thickness = slot_size * check_ratio
            bg_rgb = hex_to_rgb(bg_color)
            
            frames = []
            loop_range = range(1) if pattern_type == "Static (No Animation)" else range(total_frames)
            total_loop = 1 if pattern_type == "Static (No Animation)" else total_frames
            
            for i in loop_range:
                prog_bar.progress((i + 1) / total_loop)
                
                img_frame = Image.new('RGB', (canvas_w, canvas_h), bg_rgb)
                draw = ImageDraw.Draw(img_frame)
                draw.rectangle([(0,0), (canvas_w, canvas_h)], fill=bg_rgb)

                time_phase = (i / total_loop) * (2 * math.pi) if total_loop > 1 else 0

                for r in range(rows):
                    for c in range(cols):
                        original_rgb = img_grid.getpixel((c, r))
                        
                        # === AGGRESSIVE BLACK PROTECTION ===
                        # Hitung kecerahan (0-255)
                        brightness = sum(original_rgb) / 3
                        
                        # THRESHOLD DINAIKKAN JADI 60 (Sekitar 23% Grey)
                        # Ini akan memaksa semua warna gelap menjadi tidak aktif (Static)
                        is_dark_locked = brightness < 60 
                        
                        if is_dark_locked:
                            # KUNCI HITAM: Kembalikan warna asli tanpa sentuh efek sama sekali
                            final_rgb = original_rgb
                        else:
                            # === WIDE DYNAMIC WAVE LOGIC ===
                            # (Multiplier kecil = Gelombang Lebar)
                            wave_val = 0.0
                            if pattern_type != "Static (No Animation)":
                                if pattern_type == "Vertical Wave (Moving Down)": 
                                    wave_val = math.sin(time_phase * speed - r * 0.2) 
                                elif pattern_type == "Vertical Wave (Moving Up)": 
                                    wave_val = math.sin(time_phase * speed + r * 0.2) 
                                elif pattern_type == "Diagonal (Top-Left to Bottom-Right)": 
                                    wave_val = math.sin(time_phase * speed - (c + r) * 0.15) 
                                elif pattern_type == "Diagonal (Top-Right to Bottom-Left)": 
                                    wave_val = math.sin(time_phase * speed - ((cols - c) + r) * 0.15) 
                                elif pattern_type == "Concentric Box (Center Out)":
                                    cx = cols / 2; cy = rows / 2
                                    dist = max(abs(c - cx), abs(r - cy))
                                    wave_val = math.sin(time_phase * speed - dist * 0.2) 
                            
                            # === SHADOW & HIGHLIGHT EFFECT ===
                            r_norm, g_norm, b_norm = original_rgb[0]/255.0, original_rgb[1]/255.0, original_rgb[2]/255.0
                            h, s, v = colorsys.rgb_to_hsv(r_norm, g_norm, b_norm)
                            
                            intensity = 0.4 
                            brightness_change = wave_val * intensity
                            v_new = max(0.0, min(1.0, v + brightness_change))
                            
                            r_new, g_new, b_new = colorsys.hsv_to_rgb(h, s, v_new)
                            final_rgb = (int(r_new*255), int(g_new*255), int(b_new*255))

                        # Draw Pixel
                        x = c * slot_size
                        y = r * slot_size
                        
                        draw.rounded_rectangle([(x + padding, y + padding), (x + slot_size - padding, y + slot_size - padding)], radius=8, fill=final_rgb)
                        
                        # Draw Checkmark
                        brightness_final = sum(final_rgb) / 3
                        curr_check_col = hex_to_rgb(check_color)
                        if brightness_final < 40: curr_check_col = (60, 60, 60)
                        
                        cx_pt = x + slot_size / 2; cy_pt = y + slot_size / 2
                        thickness_pixel = max(1, int(check_thickness))
                        draw_manual_checkmark(draw, cx_pt, cy_pt, slot_size - (padding*2), curr_check_col, thickness_pixel)

                frames.append(img_frame)
            
            # Finalize
            status_box.empty()
            prog_bar.empty()
            
            final_bytes = io.BytesIO()
            if pattern_type == "Static (No Animation)":
                frames[0].save(final_bytes, format="PNG")
                fname, mime = "check_static.png", "image/png"
            else:
                frames[0].save(final_bytes, format="GIF", save_all=True, append_images=frames[1:], optimize=False, duration=int(1000/fps), loop=0)
                fname, mime = "check_anim.gif", "image/gif"
            
            st.image(final_bytes.getvalue(), use_container_width=True)
            st.download_button(label=f"DOWNLOAD {fname.split('.')[-1].upper()}", data=final_bytes.getvalue(), file_name=fname, mime=mime)

        else:
            st.markdown("""
                <div style="border: 1px dashed #333; border-radius: 8px; height: 300px; display: flex; align-items: center; justify-content: center; color: #444; background: #080808;">
                    <p style="font-size: 12px; letter-spacing: 2px;">PREVIEW AREA</p>
                </div>
            """, unsafe_allow_html=True)

else:
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("""
        <div style='text-align: center; color: #333;'>
            <h3>SYSTEM READY</h3>
            <p style="font-size: 12px;">Waiting for source input...</p>
        </div>
    """, unsafe_allow_html=True)

# --- FOOTER ---
svg_icon = """
<svg viewBox="0 0 24 24" class="mini-check-icon">
    <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/>
</svg>
"""

st.markdown(f"""
    <div class="footer-container">
        <div class="footer-checks">
            <div class="mini-check-box d1">{svg_icon}</div>
            <div class="mini-check-box d2">{svg_icon}</div>
            <div class="mini-check-box d3">{svg_icon}</div>
            <div class="mini-check-box d4">{svg_icon}</div>
            <div class="mini-check-box d5">{svg_icon}</div>
        </div>
        <div class="footer-text">
            Based Checks Studio &copy; 2026
        </div>
    </div>
""", unsafe_allow_html=True)