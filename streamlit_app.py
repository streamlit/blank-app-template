import streamlit as st
import hashlib
import json
import os
from PIL import Image
import cv2
import numpy as np
import fitz  # PyMuPDF
import pytesseract
import easyocr
from mistralai import Mistral
import io
import re
from rapidfuzz import process, fuzz
import spacy
import pandas as pd
import tempfile
from datetime import datetime
import traceback
import folium
from streamlit_folium import st_folium
from folium import plugins
from folium.plugins import HeatMap
import geopy
import statistics

# Required imports that might be missing
try:
    from geopy.geocoders import Nominatim
    from geopy.distance import geodesic
    GEOPY_AVAILABLE = True
except ImportError:
    GEOPY_AVAILABLE = False
    st.warning("⚠️ Module geopy non disponible. Installez avec: pip install geopy")

try:
    from shapely.geometry import Polygon
    SHAPELY_AVAILABLE = True
except ImportError:
    SHAPELY_AVAILABLE = False
    st.warning("⚠️ Module shapely non disponible. Installez avec: pip install shapely")

try:
    from sklearn.cluster import KMeans
    from sklearn.preprocessing import StandardScaler
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    st.warning("⚠️ Module scikit-learn non disponible. Installez avec: pip install scikit-learn")

# ========== Configuration ==========
CONFIG = {
    "logo_path": "logo.png",
    "users_file": "users.json",
    "ocr_output_file": "ocr_output.txt",
    "history_file": "history.csv",
    "tesseract_path": r"C:\Tesseract-OCR\tesseract.exe",  # Adjust as needed
    "default_mistral_api_key": "DTDhYIYWihXhDEatW4qNBJ0swCiDW9w5"
}

# ========== Utility Functions ==========
def safe_file_operation(func, *args, **kwargs):
    """Safely execute file operations with error handling"""
    try:
        return func(*args, **kwargs)
    except Exception as e:
        st.error(f"File operation error: {str(e)}")
        return None

def log_activity(username, action, details=""):
    """Log user activities for audit trail"""
    try:
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "username": username,
            "action": action,
            "details": details
        }
        
        log_file = "activity_log.json"
        logs = []
        if os.path.exists(log_file):
            with open(log_file, "r") as f:
                logs = json.load(f)
        
        logs.append(log_entry)
        
        # Keep only last 1000 entries
        logs = logs[-1000:]
        
        with open(log_file, "w") as f:
            json.dump(logs, f, indent=2)
    except Exception:
        pass  # Silent fail for logging

# ========== Password Hashing ==========
def hash_password(password):
    """Hash password with salt for better security"""
    salt = "catastrophic_events_salt"  # In production, use random salt per user
    return hashlib.sha256((password + salt).encode()).hexdigest()

# ========== User Management ==========
def load_users(file_path=None):
    """Load users with error handling"""
    file_path = file_path or CONFIG["users_file"]
    try:
        if not os.path.exists(file_path):
            with open(file_path, "w") as f:
                json.dump({}, f)
        with open(file_path, "r") as f:
            return json.load(f)
    except Exception as e:
        st.error(f"Error loading users: {e}")
        return {}

def save_users(users, file_path=None):
    """Save users with error handling"""
    file_path = file_path or CONFIG["users_file"]
    try:
        with open(file_path, "w") as f:
            json.dump(users, f, indent=2)
        return True
    except Exception as e:
        st.error(f"Error saving users: {e}")
        return False

def signup(username, password):
    """User registration with validation"""
    if not username or not password:
        return False, "Username and password are required."
    
    if len(username) < 3:
        return False, "Username must be at least 3 characters long."
    
    if len(password) < 8:
        return False, "Password must be at least 8 characters long."
    
    users = load_users()
    if username in users:
        return False, "User already exists."
    
    users[username] = {
        "password_hash": hash_password(password),
        "created_at": datetime.now().isoformat(),
        "last_login": None
    }
    
    if save_users(users):
        log_activity(username, "signup")
        return True, "User registered successfully."
    else:
        return False, "Error creating user account."

def login(username, password):
    
    """User authentication with enhanced logging"""
    if not username or not password:
        return False, "Username and password are required."
    
    users = load_users()
    user_data = users.get(username)
    
    if user_data and user_data.get("password_hash") == hash_password(password):
        # Update last login
        users[username]["last_login"] = datetime.now().isoformat()
        save_users(users)
        log_activity(username, "login")
        return True, "Login successful."
    
    log_activity(username, "failed_login")
    return False, "Invalid username or password."

# ========== Enhanced CSS ==========
def add_custom_css():
    st.markdown("""
        <style>
            .stApp { 
                background-color: #ffffff; 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            }
            section[data-testid="stSidebar"] {
                background: linear-gradient(135deg, #e6f9f0 0%, #d4f4dd 100%) !important;
                border-right: 2px solid #58d68d;
                box-shadow: 2px 0 10px rgba(0,0,0,0.1);
            }
            h1, h2, h3, .stMarkdown { 
                color: #2a6a2a; 
                font-weight: 600;
            }
            .main-title {
                text-align: center;
                color: #1e5631;
                font-size: 2.5rem;
                margin-bottom: 2rem;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
            }
            div.stButton > button {
                background: linear-gradient(135deg, #58d68d 0%, #45b76b 100%) !important;
                color: white !important;
                border: none !important;
                border-radius: 15px !important;
                height: 3.2em !important;
                width: 100% !important;
                font-weight: bold !important;
                font-size: 1rem !important;
                box-shadow: 0 4px 15px rgba(88, 214, 141, 0.3);
                transition: all 0.3s ease;
            }
            div.stButton > button:hover {
                background: linear-gradient(135deg, #45b76b 0%, #2e8b57 100%) !important;
                transform: translateY(-2px);
                box-shadow: 0 6px 20px rgba(88, 214, 141, 0.4);
            }
            .stTextInput>div>div>input, .stSelectbox>div>div>select {
                background: linear-gradient(135deg, #f8fffe 0%, #e6f7ec 100%);
                border: 2px solid #b3d9b3;
                border-radius: 12px;
                padding: 0.8em;
                font-size: 1rem;
            }
            .stRadio > div {
                background: linear-gradient(135deg, #f4f9f4 0%, #e8f5e8 100%);
                padding: 15px;
                border-radius: 15px;
                border: 1px solid #d4edda;
            }
            .success-message {
                background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
                border-left: 5px solid #28a745;
                padding: 1rem;
                border-radius: 8px;
                margin: 1rem 0;
            }
            .error-message {
                background: linear-gradient(135deg, #f8d7da 0%, #f1aeb5 100%);
                border-left: 5px solid #dc3545;
                padding: 1rem;
                border-radius: 8px;
                margin: 1rem 0;
            }
            .info-card {
                background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
                border-radius: 15px;
                padding: 20px;
                margin: 10px 0;
                box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            }
        </style>
    """, unsafe_allow_html=True)

# ========== Navigation Helpers ==========
def go_next(pages):
    current = st.session_state.current_page
    idx = pages.index(current)
    if idx < len(pages) - 1:
        st.session_state.current_page = pages[idx + 1]
        st.rerun()

def go_previous(pages):
    current = st.session_state.current_page
    idx = pages.index(current)
    if idx > 0:
        st.session_state.current_page = pages[idx - 1]
        st.rerun()

# ========== Enhanced PDF Processing ==========
def preprocess_image_enhanced(img_color):
    """Enhanced image preprocessing with noise reduction"""
    # Convert to grayscale for processing
    gray = cv2.cvtColor(img_color, cv2.COLOR_BGR2GRAY)
    
    # Noise reduction
    denoised = cv2.fastNlMeansDenoising(gray)
    
    # Enhance contrast
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    enhanced = clahe.apply(denoised)
    
    # Convert back to color
    enhanced_color = cv2.cvtColor(enhanced, cv2.COLOR_GRAY2BGR)
    
    # Slight blur to smooth artifacts
    final = cv2.GaussianBlur(enhanced_color, (1, 1), 0)
    
    return final

def process_pdf_to_clean_colored_pdf(pdf_path, output_pdf_path, output_folder):
    """Enhanced PDF processing with progress tracking"""
    try:
        doc = fitz.open(pdf_path)
        os.makedirs(output_folder, exist_ok=True)
        processed_pil_images = []
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        total_pages = len(doc)
        
        for i in range(total_pages):
            status_text.text(f"Processing page {i+1} of {total_pages}...")
            progress_bar.progress((i + 1) / total_pages)
            
            page = doc.load_page(i)
            zoom = 300 / 72  # 300 dpi for high quality
            mat = fitz.Matrix(zoom, zoom)
            pix = page.get_pixmap(matrix=mat, alpha=False)

            img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)
            img_cv = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

            processed = preprocess_image_enhanced(img_cv)

            processed_path = os.path.join(output_folder, f"page_{i+1}.png")
            cv2.imwrite(processed_path, processed)

            pil_img = Image.open(processed_path).convert("RGB")
            processed_pil_images.append(pil_img)

        if processed_pil_images:
            processed_pil_images[0].save(output_pdf_path, save_all=True, append_images=processed_pil_images[1:])
            
        progress_bar.progress(1.0)
        status_text.text("✅ Processing complete!")
        
        doc.close()
        return output_pdf_path
        
    except Exception as e:
        st.error(f"Error processing PDF: {str(e)}")
        return None

# ========== Enhanced OCR Engines ==========
def run_easyocr_on_pdf(pdf_path, lang_code):
    """Enhanced EasyOCR with progress tracking"""
    try:
        reader = easyocr.Reader([lang_code])
        doc = fitz.open(pdf_path)
        extracted_text = ""
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        total_pages = len(doc)

        for i, page in enumerate(doc):
            status_text.text(f"Running OCR on page {i+1} of {total_pages}...")
            progress_bar.progress((i + 1) / total_pages)
            
            pix = page.get_pixmap(dpi=300)
            img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)
            img_bgr = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
            
            result = reader.readtext(img_bgr, detail=0, paragraph=True)
            page_text = "\n".join(result)
            extracted_text += f"\n--- PAGE {i+1} ---\n{page_text}\n"
        
        doc.close()
        status_text.text("✅ OCR complete!")
        return extracted_text
        
    except Exception as e:
        st.error(f"EasyOCR error: {str(e)}")
        return f"❌ Error during EasyOCR processing: {e}"

def run_tesseract_on_pdf(pdf_path, lang_code):
    """Enhanced Tesseract OCR with better error handling"""
    try:
        # Set Tesseract path if configured
        if CONFIG["tesseract_path"] and os.path.exists(CONFIG["tesseract_path"]):
            pytesseract.pytesseract.tesseract_cmd = CONFIG["tesseract_path"]
        
        doc = fitz.open(pdf_path)
        all_text = []
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        total_pages = len(doc)
        
        for i, page in enumerate(doc):
            status_text.text(f"Running Tesseract OCR on page {i+1} of {total_pages}...")
            progress_bar.progress((i + 1) / total_pages)
            
            pix = page.get_pixmap(dpi=300)
            img = Image.open(io.BytesIO(pix.tobytes("png")))
            
            # Use custom config for better OCR results
            custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789àáâäèéêëìíîïòóôöùúûüçñ.,;:!?()-"\'%$€ '
            
            text = pytesseract.image_to_string(img, lang=lang_code, config=custom_config)
            all_text.append(f"\n--- PAGE {i+1} ---\n{text}")
        
        doc.close()
        status_text.text("✅ Tesseract OCR complete!")
        return "\n".join(all_text)
        
    except Exception as e:
        st.error(f"Tesseract error: {str(e)}")
        return f"❌ Error during Tesseract OCR processing: {e}"

def run_mistral_ocr(pdf_path):
    """Enhanced Mistral OCR with better error handling"""
    try:
        api_key = os.getenv("MISTRAL_API_KEY", CONFIG["default_mistral_api_key"])
        
        if not api_key:
            return "❌ Mistral API key not configured"
        
        client = Mistral(api_key=api_key)
        
        with st.spinner("Uploading file to Mistral..."):
            with open(pdf_path, "rb") as f:
                uploaded = client.files.upload(
                    file={"file_name": os.path.basename(pdf_path), "content": f}, 
                    purpose="ocr"
                )
        
        with st.spinner("Getting signed URL..."):
            signed = client.files.get_signed_url(file_id=uploaded.id)
        
        with st.spinner("Processing OCR with Mistral..."):
            ocr_response = client.ocr.process(
                model="mistral-ocr-latest", 
                document={"type": "document_url", "document_url": signed.url}
            )
        
        result = "\n\n".join(page.markdown for page in ocr_response.pages)
        st.success("✅ Mistral OCR complete!")
        return result
        
    except Exception as e:
        st.error(f"Mistral OCR error: {str(e)}")
        return f"❌ Error during Mistral OCR processing: {e}"

# ========== Enhanced TOC Functions ==========
def enhanced_toc_extraction(text):
    """Robuste extraction de table des matières avec hiérarchisation"""
    toc = []
    section_contents = {}
    current_section = None
    current_content = []

    patterns = {
        'level_1': [
            r'^#{1}\s+(.+)$',  # Markdown H1
            r'^([A-Z][A-Z\s]{10,})$',  # Titres tout en majuscules
            r'^(CHAPITRE|CHAPTER|PARTIE|PART)\s+([IVXLC]+|\d+)[:\s-]+(.+)$',
            r'^(TITRE|TITLE)\s+([IVXLC]+|\d+)[:\s-]+(.+)$'
        ],
        'level_2': [
            r'^#{2}\s+(.+)$',  # Markdown H2
            r'^(Article|ARTICLE)\s+(\d+)[:\s-]+(.+)$',
            r'^(Section|SECTION)\s+(\d+)[:\s-]+(.+)$',
            r'^(\d+)\.\s+(.+)$',
            r'^(ANNEXE|ANNEX)\s+([A-Z]|\d+)[:\s-]+(.+)$'
        ]
    }

    lines = text.split('\n')

    for line in lines:
        line = line.strip()
        if not line:
            continue

        matched = False

        # Vérification niveau 1
        for pattern in patterns['level_1']:
            match = re.match(pattern, line, re.IGNORECASE)
            if match:
                if current_section and current_content:
                    section_contents[current_section] = "\n".join(current_content).strip()

                # Choix du bon groupe en fonction du pattern
                if match.lastindex:
                    title = match.group(match.lastindex).strip()
                else:
                    title = match.group(0).strip()

                current_section = title
                current_content = []
                toc.append({"level": 1, "title": title, "line": line})
                matched = True
                break

        if not matched:
            for pattern in patterns['level_2']:
                match = re.match(pattern, line, re.IGNORECASE)
                if match:
                    if current_section and current_content:
                        section_contents[current_section] = "\n".join(current_content).strip()

                    if match.lastindex:
                        title = match.group(match.lastindex).strip()
                    else:
                        title = match.group(0).strip()

                    current_section = title
                    current_content = []
                    toc.append({"level": 2, "title": title, "line": line})
                    matched = True
                    break

        if not matched and current_section:
            current_content.append(line)

    if current_section and current_content:
        section_contents[current_section] = "\n".join(current_content).strip()

    return toc, section_contents
# ========== Enhanced Search Functionality ==========
from rapidfuzz import fuzz

def smart_search(query, section_contents):
    """
    Recherche intelligente avec correspondance exacte, floue, et dans le contenu.
    Retourne une liste de résultats triés par pertinence (score).
    """
    results = []
    query_lower = query.strip().lower()
    
    for title, content in section_contents.items():
        # Nettoyer le titre et le contenu
        title_clean = title.strip().lower()
        content_text = content if isinstance(content, str) else " ".join(content).strip()
        content_lower = content_text.lower()

        # 1. Correspondance exacte dans le titre
        if query_lower in title_clean:
            results.append({
                'type': 'title_exact',
                'title': title,
                'content': content_text,
                'score': 100
            })
            continue

        # 2. Correspondance floue dans le titre
        title_score = fuzz.partial_ratio(query_lower, title_clean)
        if title_score > 70:
            results.append({
                'type': 'title_fuzzy',
                'title': title,
                'content': content_text,
                'score': title_score
            })
            continue

        # 3. Recherche dans le contenu
        if query_lower in content_lower:
            results.append({
                'type': 'content',
                'title': title,
                'content': content_text,
                'score': 80
            })

    # Tri décroissant par score de pertinence
    results.sort(key=lambda x: x['score'], reverse=True)
    return results

def update_section_content(section_contents, title, new_content):
    """
    Met à jour le contenu d'une section spécifiée par son titre exact.
    """
    if title in section_contents:
        section_contents[title] = new_content.strip()
        return True
    else:
        return False


# ========== Enhanced Main Application ==========
def create_logo_placeholder():
    """Create a placeholder logo if none exists"""
    try:
        if not os.path.exists(CONFIG["logo_path"]):
            # Create a nice gradient logo placeholder
            img = Image.new('RGB', (400, 200), color='white')
            # You could add text or shapes here
            img.save(CONFIG["logo_path"])
        return True
    except Exception:
        return False
def geocoding_tab():
    """Géocodage d'adresses"""
    st.write("**🔍 Géocodage d'Adresses**")

    address_input = st.text_input(
        "Adresse à géocoder", 
        placeholder="ex: 123 Boulevard Hassan II, Casablanca"
    )

    if st.button("🎯 Localiser"):
        if address_input and GEOPY_AVAILABLE:
            try:
                # Using Nominatim geocoder (free OpenStreetMap service)
                geolocator = Nominatim(user_agent="streamlit_geo_app")
                location = geolocator.geocode(address_input)

                if location:
                    st.success("✅ Adresse localisée avec succès!")

                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("🌐 Latitude", f"{location.latitude:.6f}")
                    with col2:
                        st.metric("🌐 Longitude", f"{location.longitude:.6f}")

                    st.info(f"📍 **Adresse complète :** {location.address}")

                    # Create map
                    geocoded_map = folium.Map(
                        location=[location.latitude, location.longitude],
                        zoom_start=15
                    )

                    # Add marker
                    folium.Marker(
                        [location.latitude, location.longitude],
                        popup=f"<b>{address_input}</b><br>{location.address}",
                        tooltip="Localisation géocodée",
                        icon=folium.Icon(color='red', icon='info-sign')
                    ).add_to(geocoded_map)

                    # Display map
                    st_folium(geocoded_map, width=700, height=400)

                    # Export data
                    export_data = {
                        'adresse_saisie': address_input,
                        'adresse_complete': location.address,
                        'latitude': location.latitude,
                        'longitude': location.longitude
                    }

                    st.download_button(
                        "📥 Télécharger les coordonnées (JSON)",
                        data=json.dumps(export_data, indent=2, ensure_ascii=False),
                        file_name=f"geocodage_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                        mime="application/json"
                    )

                else:
                    st.error("❌ Impossible de localiser cette adresse. Vérifiez l'orthographe.")

            except Exception as e:
                st.error(f"❌ Erreur lors du géocodage : {str(e)}")

        elif address_input and not GEOPY_AVAILABLE:
            st.error("❌ Le module geopy est requis pour le géocodage.")
        else:
            st.warning("⚠️ Veuillez saisir une adresse.")

def distance_measurement():
    """Distance measurement functionality"""
    st.write("**📍 Définir les points**")
    
    col1, col2 = st.columns(2)
    with col1:
        st.write("**Point A**")
        lat_a = st.number_input("Latitude A", format="%.6f", value=33.5731)
        lon_a = st.number_input("Longitude A", format="%.6f", value=-7.5898)
        
    with col2:
        st.write("**Point B**")
        lat_b = st.number_input("Latitude B", format="%.6f", value=33.5831)
        lon_b = st.number_input("Longitude B", format="%.6f", value=-7.5798)
    
    if st.button("📐 Calculer la distance") and GEOPY_AVAILABLE:
        # Calculate distance using geopy
        point_a = (lat_a, lon_a)
        point_b = (lat_b, lon_b)
        
        distance_km = geodesic(point_a, point_b).kilometers
        distance_m = distance_km * 1000
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("🛣️ Distance (km)", f"{distance_km:.3f} km")
        with col2:
            st.metric("🛣️ Distance (m)", f"{distance_m:.1f} m")
        
        # Create map showing the two points and line
        center_lat = (lat_a + lat_b) / 2
        center_lon = (lon_a + lon_b) / 2
        
        distance_map = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=12
        )
        
        # Add markers
        folium.Marker(
            [lat_a, lon_a],
            popup="Point A",
            icon=folium.Icon(color='green', icon='play')
        ).add_to(distance_map)
        
        folium.Marker(
            [lat_b, lon_b],
            popup="Point B",
            icon=folium.Icon(color='red', icon='stop')
        ).add_to(distance_map)
        
        # Add line
        folium.PolyLine(
            locations=[[lat_a, lon_a], [lat_b, lon_b]],
            color='blue',
            weight=3,
            popup=f"Distance: {distance_km:.3f} km"
        ).add_to(distance_map)
        
        st_folium(distance_map, width=700, height=400)

def polygon_measurement():
    """Polygon area measurement functionality"""
    st.write("**🔷 Dessinez un polygone sur la carte**")
    st.info("💡 Cliquez sur la carte pour créer les points du polygone, puis cliquez sur le premier point pour fermer.")
    
    # Create an interactive map for polygon drawing
    polygon_map = folium.Map(location=[33.5731, -7.5898], zoom_start=10)
    
    # Add drawing tools
    draw = plugins.Draw(
        export=True,
        position='topleft',
        draw_options={
            'polyline': False,
            'polygon': True,
            'circle': False,
            'rectangle': True,
            'marker': False,
            'circlemarker': False,
        }
    )
    draw.add_to(polygon_map)
    
    map_data = st_folium(polygon_map, width=700, height=400)
    
    if map_data['all_drawings'] and SHAPELY_AVAILABLE:
        for drawing in map_data['all_drawings']:
            if drawing['geometry']['type'] == 'Polygon':
                coords = drawing['geometry']['coordinates'][0]
                
                # Calculate area using Shapely
                polygon = Polygon(coords)
                # Rough conversion for lat/lon to meters (approximate)
                area_deg2 = abs(polygon.area)
                area_m2 = area_deg2 * (111319.9 ** 2) * np.cos(np.radians(coords[0][1]))
                area_km2 = area_m2 / 1_000_000
                area_ha = area_m2 / 10_000
                
                st.success("✅ Surface calculée!")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("🏞️ Surface (km²)", f"{area_km2:.3f}")
                with col2:
                    st.metric("🏞️ Surface (ha)", f"{area_ha:.2f}")
                with col3:
                    st.metric("🏞️ Surface (m²)", f"{area_m2:.0f}")
    elif map_data['all_drawings'] and not SHAPELY_AVAILABLE:
        st.error("❌ Module shapely requis pour le calcul de surface.")


def measurement_tab():
    """Measurement tools tab"""
    st.write("**📏 Outils de Mesure**")
    
    measure_type = st.selectbox(
        "Type de mesure",
        ["Distance entre deux points", "Surface d'un polygone", "Périmètre"]
    )
    
    if measure_type == "Distance entre deux points":
        distance_measurement()
    elif measure_type == "Surface d'un polygone":
        polygon_measurement()
    else:
        st.info("🚧 Fonctionnalité de calcul de périmètre en cours de développement.")

def hotspots_tab():
    """Hotspots analysis tab"""
    st.write("**🎯 Analyse des Points Chauds (Hotspots)**")

    # Create sample data if none exists
    if st.session_state.uploaded_data is None or st.session_state.uploaded_data.empty:
        if st.button("🎲 Générer des données d'exemple"):
            # Generate sample geospatial data
            np.random.seed(42)
            n_points = 100

            # Center around Casablanca
            base_lat, base_lon = 33.5731, -7.5898

            sample_data = pd.DataFrame({
                'latitude': np.random.normal(base_lat, 0.1, n_points),
                'longitude': np.random.normal(base_lon, 0.1, n_points),
                'contract_value': np.random.exponential(50000, n_points),
                'risk_score': np.random.uniform(0, 100, n_points),
                'claims_count': np.random.poisson(2, n_points)
            })

            st.session_state.uploaded_data = sample_data
            st.success("✅ Données d'exemple générées!")
            st.rerun()

    if st.session_state.uploaded_data is not None and not st.session_state.uploaded_data.empty:
        # Get numeric columns for analysis
        numeric_cols = st.session_state.uploaded_data.select_dtypes(include=[np.number]).columns.tolist()

        if len(numeric_cols) > 0:
            analysis_col = st.selectbox("Colonne à analyser", numeric_cols)

            # Hotspot analysis method
            method = st.selectbox(
                "Méthode d'analyse",
                ["Densité par kernel", "Points chauds statistiques", "Clustering K-means"]
            )

            if st.button("🔥 Analyser les hotspots"):
                if method == "Densité par kernel":
                    density_analysis(analysis_col)
                elif method == "Clustering K-means" and SKLEARN_AVAILABLE:
                    kmeans_analysis(analysis_col)
                elif method == "Clustering K-means" and not SKLEARN_AVAILABLE:
                    st.error("❌ Module scikit-learn requis pour le clustering.")
                else:
                    st.info("📊 Analyse des points chauds statistiques en cours de développement.")
        else:
            st.warning("⚠️ Aucune colonne numérique disponible pour l'analyse des hotspots.")
    else:
        st.info("📂 Veuillez d'abord charger des données géospatiales ou générer des données d'exemple pour analyser les hotspots.")

def density_analysis(analysis_col):
    """Kernel density analysis"""
    st.info("📊 Analyse de densité par noyau (Kernel Density)")

    # Create heatmap
    center_lat = st.session_state.uploaded_data['latitude'].mean()
    center_lon = st.session_state.uploaded_data['longitude'].mean()

    hotspot_map = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=10
    )

    # Prepare data for heatmap
    heat_data = []
    for idx, row in st.session_state.uploaded_data.iterrows():
        if pd.notna(row['latitude']) and pd.notna(row['longitude']) and pd.notna(row[analysis_col]):
            heat_data.append([row['latitude'], row['longitude'], float(row[analysis_col])])

    # Add heatmap
    if heat_data:
        HeatMap(
            heat_data, 
            radius=15, 
            blur=10, 
            gradient={
                0.0: 'blue', 
                0.3: 'cyan', 
                0.5: 'lime', 
                0.7: 'yellow', 
                1.0: 'red'
            }
        ).add_to(hotspot_map)

        st_folium(hotspot_map, width=700, height=500)

        # Statistics
        st.write("**📈 Statistiques de la densité:**")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Points analysés", len(heat_data))
        with col2:
            st.metric("Valeur moyenne", f"{np.mean([point[2] for point in heat_data]):.2f}")
        with col3:
            st.metric("Valeur max", f"{np.max([point[2] for point in heat_data]):.2f}")
    else:
        st.error("❌ Données insuffisantes pour l'analyse de densité.")


def kmeans_analysis(analysis_col):
    """K-means clustering analysis"""
    st.info("🎯 Analyse par clustering K-means")

    n_clusters = st.slider("Nombre de clusters", 2, 10, 5)

    # Prepare data for clustering
    cluster_data = st.session_state.uploaded_data[
        ['latitude', 'longitude', analysis_col]
    ].dropna()

    if len(cluster_data) >= n_clusters:
        # Standardize data
        scaler = StandardScaler()
        scaled_data = scaler.fit_transform(cluster_data)

        # Perform clustering
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        clusters = kmeans.fit_predict(scaled_data)

        # Add cluster labels to data
        cluster_data = cluster_data.copy()
        cluster_data['cluster'] = clusters

        # Create map with clusters
        cluster_map = folium.Map(
            location=[cluster_data['latitude'].mean(), cluster_data['longitude'].mean()],
            zoom_start=10
        )

        # Color palette for clusters
        colors = ['red', 'blue', 'green', 'purple', 'orange',
                  'darkred', 'lightred', 'beige', 'darkblue', 'darkgreen']

        # Add points with cluster colors
        for idx, row in cluster_data.iterrows():
            folium.CircleMarker(
                location=[row['latitude'], row['longitude']],
                radius=8,
                popup=f"Cluster: {row['cluster']}<br>Valeur: {row[analysis_col]:.2f}",
                color=colors[row['cluster'] % len(colors)],
                fill=True,
                fillColor=colors[row['cluster'] % len(colors)]
            ).add_to(cluster_map)

        # Add cluster centers
        centers = scaler.inverse_transform(kmeans.cluster_centers_)
        for i, center in enumerate(centers):
            folium.Marker(
                location=[center[0], center[1]],
                popup=f"Centre du Cluster {i}",
                icon=folium.Icon(color='black', icon='star')
            ).add_to(cluster_map)

        st_folium(cluster_map, width=700, height=500)

        # Cluster statistics
        st.write("**📊 Statistiques des clusters:**")
        cluster_stats = cluster_data.groupby('cluster')[analysis_col].agg(['count', 'mean', 'std']).round(2)
        st.dataframe(cluster_stats)
    else:
        st.error(f"❌ Données insuffisantes. Il faut au moins {n_clusters} points valides.")

def main():
    st.set_page_config(
        page_title="Catastrophic Events Platform", 
        layout="wide",
        page_icon="🌊",
        initial_sidebar_state="expanded"
    )
    add_custom_css()

    # Initialize session state
    session_defaults = {
        "logged_in": False,
        "username": "",
        "current_page": "login",
        "contract_legal_section": 1,
        "uploaded_files": [],
        "processing_history": []
    }
    
    for key, default_value in session_defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default_value

    # Create logo placeholder if needed
    create_logo_placeholder()

    if not st.session_state.logged_in:
        # ========== Login/Signup Interface ==========
        with st.sidebar:
            if os.path.exists(CONFIG["logo_path"]):
                st.image(CONFIG["logo_path"], width=200)
            
            st.markdown("""
                <div class="info-card">
                    <h3>🌊 Bienvenue</h3>
                    <p>Plateforme d'analyse des événements catastrophiques</p>
                    <p><small>Veuillez vous connecter pour continuer</small></p>
                </div>
            """, unsafe_allow_html=True)

        # Main login area
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if os.path.exists(CONFIG["logo_path"]):
                st.image(Image.open(CONFIG["logo_path"]), width=400)
            
            st.markdown('<h1 class="main-title">🌊 Catastrophic Events Platform</h1>', unsafe_allow_html=True)
            st.markdown('<div class="info-card"><p>Plateforme intégrée d\'analyse des risques catastrophiques avec OCR avancé, géolocalisation et détection de fraude.</p></div>', unsafe_allow_html=True)

            # Enhanced login/signup tabs
            tab1, tab2 = st.tabs(["🔑 Connexion", "👤 Inscription"])
            
            with tab1:
                st.subheader("Connexion à votre compte")
                username = st.text_input("Nom d'utilisateur", placeholder="Votre nom d'utilisateur", key="login_user")
                password = st.text_input("Mot de passe", type="password", placeholder="Votre mot de passe", key="login_pass")
                
                col_a, col_b = st.columns(2)
                with col_a:
                    if st.button("🚀 Se connecter", key="login_btn"):
                        if username and password:
                            success, msg = login(username, password)
                            if success:
                                st.success(msg)
                                st.session_state.logged_in = True
                                st.session_state.username = username
                                st.session_state.current_page = "Home"
                                st.rerun()
                            else:
                                st.error(msg)
                        else:
                            st.warning("Veuillez remplir tous les champs")
                
                with col_b:
                    if st.button("🔍 Mot de passe oublié?", key="forgot_btn"):
                        st.info("Contactez l'administrateur pour réinitialiser votre mot de passe")

            with tab2:
                st.subheader("Créer un nouveau compte")
                new_user = st.text_input("Nom d'utilisateur", placeholder="Choisissez un nom d'utilisateur", key="signup_user")
                new_pass = st.text_input("Mot de passe", type="password", placeholder="Créez un mot de passe sécurisé", key="signup_pass")
                confirm_pass = st.text_input("Confirmer mot de passe", type="password", placeholder="Confirmez votre mot de passe", key="confirm_pass")
                
                if st.button("✨ Créer le compte", key="signup_btn"):
                    if not all([new_user, new_pass, confirm_pass]):
                        st.warning("Veuillez remplir tous les champs")
                    elif new_pass != confirm_pass:
                        st.error("Les mots de passe ne correspondent pas")
                    else:
                        success, msg = signup(new_user, new_pass)
                        if success:
                            st.success(msg)
                        else:
                            st.error(msg)

    else:
        # ========== Main Application Interface ==========
        pages = [
            "Home", "Risk Mapping", "Descriptive Statistics", 
            "Contracts & Legal Check", "Geospatial Contract View",
            "Recommendation System", "Reporting System", "Fraud Detection System"
        ]

        with st.sidebar:
            if os.path.exists(CONFIG["logo_path"]):
                st.image(CONFIG["logo_path"], width=200)
            
            st.markdown(f"""
                <div class="info-card">
                    <h3>👋 Bienvenue</h3>
                    <p><strong>{st.session_state.username}</strong></p>
                    <p><small>Dernière connexion: {datetime.now().strftime('%d/%m/%Y %H:%M')}</small></p>
                </div>
            """, unsafe_allow_html=True)
            
            st.markdown("### 🧭 Navigation")
            selected = st.radio("Choisir une section", pages, index=pages.index(st.session_state.current_page))
            st.session_state.current_page = selected

            st.markdown("---")
            col_prev, col_next = st.columns(2)
            with col_prev:
                if st.button("⬅️ Précédent", key="nav_prev"):
                    go_previous(pages)
            with col_next:
                if st.button("➡️ Suivant", key="nav_next"):
                    go_next(pages)
            
            st.markdown("---")
            if st.button("🚪 Déconnexion", key="logout_btn"):
                log_activity(st.session_state.username, "logout")
                st.session_state.logged_in = False
                st.session_state.username = ""
                st.session_state.current_page = "login"
                st.rerun()

        # ========== Page Content ==========
        if st.session_state.current_page == "Home":
            st.markdown('<h1 class="main-title">🏠 Tableau de Bord Principal</h1>', unsafe_allow_html=True)
            
            # Welcome section
            st.markdown("""
                <div class="info-card">
                    <h3>🌊 Plateforme Catastrophic Events</h3>
                    <p>Solution intégrée pour la gestion, l'analyse géospatiale, la souscription et le monitoring des contrats de réassurance, 
                    avec modules avancés de cartographie des risques, conformité légale, détection de fraude et reporting.</p>
                </div>
            """, unsafe_allow_html=True)
            
            # File upload section
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.subheader("📄 Gestion des Documents")
                
                uploaded_contracts = st.file_uploader(
                    "Contrats de réassurance", 
                    type=["pdf", "docx"], 
                    accept_multiple_files=True,
                    help="Glissez-déposez ou sélectionnez vos fichiers de contrats"
                )
                
                legal_ref = st.file_uploader(
                    "Référentiel juridique marocain", 
                    type=["pdf", "docx"], 
                    help="Fichier de référence juridique unique"
                )
                
                contract_id = st.text_input(
                    "Identifiant du contrat",
                    placeholder="ex: REA-2024-001",
                    help="Identifiant unique pour traçabilité"
                )

                # Processing status
                if uploaded_contracts:
                    st.success(f"✅ {len(uploaded_contracts)} contrat(s) téléchargé(s)")
                    st.session_state.uploaded_files = uploaded_contracts
                    
                if legal_ref:
                    st.info("✅ Référentiel juridique enregistré")
                    
                if contract_id:
                    st.markdown(f"**📌 ID Contrat:** `{contract_id}`")

            with col2:
                st.subheader("📊 Statistiques Rapides")

                # Quick stats (placeholder data)
                st.metric("Contrats traités", "7", "↗️ +12%")
                st.metric("Conformité moyenne", "94.2%", "↗️ +2.1%")
                st.metric("Détections fraude", "2", "↘️ -1")
                st.metric("Risques identifiés", "15", "↗️ +5")
                st.metric("Temps moyen de traitement", "3.5 min", "↘️ -0.5 min")
                
                st.markdown("---")

                st.subheader("📈 Graphiques et Tendances")
                
                # System status
                st.markdown("**🔥 État du Système**")

                st.success("🟢 OCR Engines: Actifs")
                st.success("🟢 Géolocalisation: Active")
                st.success("🟢 Mistral API: Robuste ")
                st.warning("🟡 Tesseract OCR: En maintenance")
                st.error("🔴 EasyOCR: Problème de performance")

                # Recent activity
                st.markdown("**📈 Activité Récente**")
                st.markdown("""
                - ✅ Contrat REA-2024-046 traité
                - 🔍 Analyse fraude terminée  
                - 📊 Rapport mensuel généré
                """)

        elif st.session_state.current_page == "Risk Mapping":
            st.markdown('<h1 class="main-title">🗺️ Cartographie des Risques</h1>', unsafe_allow_html=True)
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.subheader("🌍 Analyse Géospatiale Interactive")
                
                # Map configuration options
                map_type = st.selectbox("Type de carte", [
                    "🌊 Risques d'inondation", 
                    "🔥 Risques d'incendie",
                    "🌪️ Risques sismiques",
                    "🌨️ Risques climatiques"
                ])
                
                region_filter = st.multiselect("Régions d'intérêt", [
                    "Casablanca-Settat", "Rabat-Salé-Kénitra", "Marrakech-Safi",
                    "Fès-Meknès", "Tanger-Tétouan-Al Hoceïma", "Oriental"
                ], default=["Casablanca-Settat"])
                
                time_period = st.slider("Période d'analyse (années)", 1, 50, 5)
                
                # Placeholder for map visualization
                st.markdown("""
                <div class="info-card">
                    <h4>📍 Carte Interactive</h4>
                    <p>La carte géospatiale s'afficherait ici avec :</p>
                    <ul>
                        <li>🎯 Zones à risque identifiées</li>
                        <li>📊 Intensité des risques par couleur</li>
                        <li>📈 Données historiques superposées</li>
                        <li>🏢 Localisation des assurés</li>
                    </ul>
                    <p><em>Intégration avec les APIs de cartographie en cours...</em></p>
                </div>
                """, unsafe_allow_html=True)
                
                # Risk analysis results
                if st.button("🔍 Lancer l'analyse"):
                    with st.spinner("Analyse des risques en cours..."):
                        st.success("✅ Analyse terminée!")
                        
                        # Mock results
                        st.subheader("📊 Résultats de l'analyse")
                        
                        risk_data = {
                            "Zone": ["Casablanca Centre", "Mohammedia", "Berrechid", "Settat"],
                            "Niveau Risque": ["Élevé", "Moyen", "Faible", "Moyen"],
                            "Probabilité (%)": [87, 65, 32, 58],
                            "Impact Estimé (MAD)": ["2.5M", "1.2M", "450K", "890K"]
                        }
                        
                        df_risk = pd.DataFrame(risk_data)
                        st.dataframe(df_risk, use_container_width=True)

            with col2:
                st.subheader("⚠️ Alertes Risques")
                
                st.error("🚨 **ALERTE ÉLEVÉE**\nInondations prévues - Casablanca\n*Probabilité: 85%*")
                st.warning("⚠️ **Surveillance**\nActivité sismique - Agadir\n*Magnitude: 3.2*")
                st.info("ℹ️ **Information**\nVents forts - Tanger\n*Vitesse: 45 km/h*")
                
                st.markdown("---")
                st.subheader("📈 Tendances")
                
                # Mock trend data
                trend_data = pd.DataFrame({
                    "Mois": ["Jan", "Fév", "Mar", "Avr", "Mai", "Jun"],
                    "Incidents": [12, 8, 15, 22, 18, 25]
                })
                
                st.line_chart(trend_data.set_index("Mois"))

        elif st.session_state.current_page == "Descriptive Statistics":
            st.markdown('<h1 class="main-title">📊 Statistiques Descriptives</h1>', unsafe_allow_html=True)
            
            # Sample data upload section
            st.subheader("📁 Chargement des Données")
            
            data_source = st.radio("Source des données", [
                "📄 Analyser les contrats uploadés",
                "📊 Utiliser les données d'exemple",
                "🔗 Importer depuis base de données"
            ])
            
            if data_source == "📊 Utiliser les données d'exemple":
                with st.spinner("Chargement des données d'exemple..."):
                    # Generate mock insurance data
                    np.random.seed(42)
                    n_contracts = 80
                    
                    sample_data = {
                        "ID_Contrat": [f"REA-2024-{i:04d}" for i in range(1, n_contracts+1)],
                        "Prime_Annuelle": np.random.lognormal(10, 0.5, n_contracts),
                        "Capital_Assure": np.random.lognormal(15, 0.7, n_contracts),
                        "Type_Risque": np.random.choice(["Inondation", "Incendie", "Séisme", "Tempête"], n_contracts),
                        "Region": np.random.choice(["Casablanca", "Rabat", "Marrakech", "Fès", "Tanger"], n_contracts),
                        "Nb_Sinistres": np.random.poisson(2, n_contracts),
                        "Montant_Sinistres": np.random.exponential(50000, n_contracts),
                        "Date_Souscription": pd.date_range("2020-01-01", periods=n_contracts, freq="D")
                    }
                    
                    df = pd.DataFrame(sample_data)
                    df["Ratio_Sinistres"] = df["Montant_Sinistres"] / df["Prime_Annuelle"]
                    
                st.success(f"✅ {len(df)} contrats chargés avec succès!")
                
                # Display data overview
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Total Contrats", f"{len(df):,}")
                with col2:
                    st.metric("Prime Moyenne", f"{df['Prime_Annuelle'].mean():,.0f} MAD")
                with col3:
                    st.metric("Capital Total", f"{df['Capital_Assure'].sum()/1e9:.1f}B MAD")
                with col4:
                    st.metric("Ratio S/P Moyen", f"{df['Ratio_Sinistres'].mean():.2f}")
                
                # Data exploration tabs
                tab1, tab2, tab3, tab4 = st.tabs(["📈 Distributions", "🔍 Corrélations", "📋 Résumé", "📊 Visualisations"])
                
                with tab1:
                    st.subheader("Distribution des Variables Clés")
                    
                    col_a, col_b = st.columns(2)
                    
                    with col_a:
                        fig_prime = pd.DataFrame({
                            "Prime_Annuelle": df["Prime_Annuelle"]
                        })
                        st.subheader("Distribution des Primes")
                        import matplotlib.pyplot as plt
                        fig, ax = plt.subplots()
                        ax.hist(fig_prime["Prime_Annuelle"], bins=20)
                        st.pyplot(fig)
                        
                        # Basic stats
                        st.markdown("**Statistiques des Primes:**")
                        st.write(f"- Moyenne: {df['Prime_Annuelle'].mean():,.0f} MAD")
                        st.write(f"- Médiane: {df['Prime_Annuelle'].median():,.0f} MAD")
                        st.write(f"- Écart-type: {df['Prime_Annuelle'].std():,.0f} MAD")
                    
                    with col_b:
                        st.subheader("Répartition par Type de Risque")
                        risk_counts = df["Type_Risque"].value_counts()
                        st.bar_chart(risk_counts)
                        
                        st.subheader("Répartition par Région")
                        region_counts = df["Region"].value_counts()
                        st.bar_chart(region_counts)
                
                with tab2:
                    st.subheader("Matrice de Corrélation")
                    
                    numeric_cols = df.select_dtypes(include=[np.number]).columns
                    corr_matrix = df[numeric_cols].corr()
                    
                    st.write("Corrélations principales:")
                    st.dataframe(corr_matrix, use_container_width=True)
                    
                    # Insights
                    st.markdown("""
                    **🔍 Insights:**
                    - Corrélation positive entre Capital Assuré et Prime Annuelle
                    - Relation inverse entre nombre de sinistres et profitabilité
                    - Variations régionales significatives dans les ratios
                    """)
                
                with tab3:
                    st.subheader("Résumé Statistique Complet")
                    st.dataframe(df.describe(), use_container_width=True)
                    
                    # Additional statistics
                    st.subheader("Analyses Avancées")
                    
                    col_x, col_y = st.columns(2)
                    
                    with col_x:
                        st.markdown("**📊 Quartiles des Primes:**")
                        q1 = df['Prime_Annuelle'].quantile(0.25)
                        q2 = df['Prime_Annuelle'].quantile(0.5)
                        q3 = df['Prime_Annuelle'].quantile(0.75)
                        
                        st.write(f"- Q1 (25%): {q1:,.0f} MAD")
                        st.write(f"- Q2 (50%): {q2:,.0f} MAD") 
                        st.write(f"- Q3 (75%): {q3:,.0f} MAD")
                    
                    with col_y:
                        st.markdown("**⚠️ Valeurs Aberrantes:**")
                        
                        # Detect outliers using IQR method
                        Q1 = df['Prime_Annuelle'].quantile(0.25)
                        Q3 = df['Prime_Annuelle'].quantile(0.75)
                        IQR = Q3 - Q1
                        outliers = df[(df['Prime_Annuelle'] < (Q1 - 1.5 * IQR)) | 
                                    (df['Prime_Annuelle'] > (Q3 + 1.5 * IQR))]
                        
                        st.write(f"- Nombre d'outliers: {len(outliers)}")
                        st.write(f"- % du portefeuille: {len(outliers)/len(df)*100:.1f}%")
                
                with tab4:
                    st.subheader("Visualisations Avancées")
                    
                    # Time series analysis
                    monthly_data = df.groupby(df['Date_Souscription'].dt.to_period('M')).agg({
                        'Prime_Annuelle': 'sum',
                        'ID_Contrat': 'count'
                    }).reset_index()
                    monthly_data['Date_Souscription'] = monthly_data['Date_Souscription'].astype(str)
                    
                    st.subheader("📈 Évolution Temporelle")
                    st.line_chart(monthly_data.set_index('Date_Souscription')['Prime_Annuelle'])
                    
                    # Risk analysis by region
                    st.subheader("🗺️ Analyse par Région")
                    region_analysis = df.groupby('Region').agg({
                        'Prime_Annuelle': ['mean', 'sum'],
                        'Ratio_Sinistres': 'mean',
                        'ID_Contrat': 'count'
                    }).round(2)
                    
                    st.dataframe(region_analysis, use_container_width=True)

        elif st.session_state.current_page == "Contracts & Legal Check":
            st.markdown('<h1 class="main-title">⚖️ Vérification Contractuelle et Légale</h1>', unsafe_allow_html=True)
            
            # Section navigation
            legal_sections = [
                "1️⃣ Upload et OCR",
                "2️⃣ Analyse Légale", 
                "3️⃣ Conformité",
                "4️⃣ Rapport Final"
            ]
            
            current_section = st.selectbox("Étape du processus", legal_sections, 
                                         index=st.session_state.contract_legal_section-1)
            st.session_state.contract_legal_section = legal_sections.index(current_section) + 1
            
            if st.session_state.contract_legal_section == 1:
                # Upload and OCR Section
                st.subheader("📄 Téléchargement et Extraction de Texte")
                
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    contract_file = st.file_uploader(
                        "Contrat à analyser", 
                        type=["pdf"],
                        help="Fichier PDF du contrat de réassurance"
                    )
                    
                    if contract_file:
                        # Save uploaded file temporarily
                        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                            tmp_file.write(contract_file.read())
                            temp_path = tmp_file.name
                        
                        st.success(f"✅ Fichier téléchargé: {contract_file.name}")
                        
                        # OCR Engine Selection
                        st.subheader("🔍 Sélection du Moteur OCR")
                        
                        ocr_engine = st.radio("Choisir le moteur OCR", [
                            "🚀 EasyOCR ",
                            "🔧 Tesseract",
                            "🧠 Mistral OCR "
                        ])
                        
                        # Language selection
                        lang_options = {
                            "Français": "fr",
                            "Anglais": "en", 
                            "Arabe": "ar",
                            "Espagnol": "es",
                            "Allemand": "de",
                            "Italien": "it",
                            "Portugais": "pt",
                            "Chinois": "zh",
                            "Russe": "ru",
                            "Japonais": "ja",
                            "Coréen": "ko",
                            "Hindi": "hi",
                            "Turc": "tr",
                            "Vietnamien": "vi",
                            "Polonais": "pl",
                            "Néerlandais": "nl",
                            "Suédois": "sv",
                            "Danois": "da",
                            "Finnois": "fi",
                            "Norvégien": "no",
                            "Grec": "el",
                            "Hongrois": "hu",
                            "Tchèque": "cs",
                            "Roumain": "ro",
                            "Bulgare": "bg",
                            "Ukrainien": "uk",
                            "Multi-langues": "fr"
                        }
                        
                        selected_lang = st.selectbox("Langue du document", list(lang_options.keys()))
                        lang_code = lang_options[selected_lang]
                        
                        if st.button("🎯 Lancer l'extraction OCR", type="primary"):
                            if "EasyOCR" in ocr_engine:
                                extracted_text = run_easyocr_on_pdf(temp_path, lang_code)
                            elif "Tesseract" in ocr_engine:
                                extracted_text = run_tesseract_on_pdf(temp_path, lang_code)
                            else:  # Mistral OCR
                                extracted_text = run_mistral_ocr(temp_path)
                            
                            # Save extracted text
                            with open(CONFIG["ocr_output_file"], "w", encoding="utf-8") as f:
                                f.write(extracted_text)
                            
                            st.session_state["extracted_text"] = extracted_text
                            st.success("✅ Extraction OCR terminée!")
                            
                            # Show preview
                            st.subheader("📖 Aperçu du texte extrait")
                            st.text_area("Texte extrait complet", extracted_text, height=600)
                            st.session_state.contract_legal_section = 2  # Move to next section
                        else:
                            st.info("ℹ️ Cliquez pour lancer l'extraction OCR")   
                        
                        # Clean up temp file
                        os.unlink(temp_path)
                
                with col2:
                    st.subheader("ℹ️ Guide OCR")
                    
                    st.markdown("""
                    <div class="info-card">
                        <h4>🎯 Moteurs OCR</h4>
                        <ul>
                            <li><strong>EasyOCR:</strong> Meilleur pour textes multilingues</li>
                            <li><strong>Tesseract:</strong> Rapide, bon pour textes nets</li>
                            <li><strong>Mistral:</strong> IA avancée, meilleure précision</li>
                        </ul>
                        
                        <h4>💡 Conseils</h4>
                        <ul>
                            <li>Scans de qualité 300 DPI minimum</li>
                            <li>Éviter les documents trop inclinés</li>
                            <li>Texte noir sur fond blanc idéal</li>
                        </ul>
                    </div>
                    """, unsafe_allow_html=True)

            elif st.session_state.contract_legal_section == 2:
                # Legal Analysis Section
                st.subheader("⚖️ Analyse Légale Automatisée")
                
                if "extracted_text" not in st.session_state:
                    st.warning("⚠️ Veuillez d'abord extraire le texte du contrat dans l'étape 1")
                    if st.button("↩️ Retour à l'étape 1"):
                        st.session_state.contract_legal_section = 1
                        st.rerun()
                else:
                    extracted_text = st.session_state["extracted_text"]
                    
                    # Table of Contents Extraction
                    st.subheader("📑 Structure du Document")
                    
                    if st.button("🔍 Analyser la structure"):
                        with st.spinner("Extraction de la table des matières..."):
                            toc, section_contents = enhanced_toc_extraction(extracted_text)
                            st.session_state["toc"] = toc
                            st.session_state["section_contents"] = section_contents
                        
                            st.success(f"✅ {len(toc)} sections identifiées")
                        
                        # Display TOC
                        for item in toc:
                            indent = "  " * (item["level"] - 1)
                            st.write(f"{indent}• {item['title']}")
                    
                    # Legal Terms Search
                    st.subheader("🔎 Recherche de Termes Juridiques")

                    search_query = st.text_input(
                        "Rechercher un terme ou une clause",
                        placeholder="ex: force majeure, exclusions, franchise"
                    )

                    if search_query and "section_contents" in st.session_state:
                        section_contents = st.session_state["section_contents"]
                        results = smart_search(search_query, section_contents)

                        if results:
                            st.success(f"✅ {len(results)} résultat(s) trouvé(s)")

                            for i, result in enumerate(results[:3]):  # Top 3 résultats
                                with st.expander(f"📄 {result['title']} (Score: {result['score']})"):
                                    # Prévisualisation
                                    st.markdown(f"**Type de correspondance** : `{result['type']}`")
                                    st.markdown("**Contenu trouvé :**")

                                    content = result['content']
                                    content_preview = content[:500] + "..." if len(content) > 500 else content

                                    edited_content = st.text_area(
                                        f"✏️ Modifier le contenu de cette section",
                                        value=content_preview,
                                        height=250,
                                        key=f"edit_{i}"
                                    )

                                    if st.button(f"💾 Enregistrer la modification {i+1}", key=f"save_{i}"):
                                        st.session_state["section_contents"][result['title']] = edited_content.strip()
                                        st.success("✅ Contenu mis à jour.")

                                        # Sauvegarde historique
                                        try:
                                            with open("history.csv", "a", encoding="utf-8") as h:
                                                h.write(f"{search_query},{result['title']}\n")
                                        except Exception as e:
                                            st.warning(f"⚠️ Impossible de sauvegarder l'historique : {e}")

                        else:
                            st.info("ℹ️ Aucun résultat trouvé. Essayez d'autres mots-clés.")

                    
                    # Legal Compliance Check
                    st.subheader("✅ Vérification de Conformité")
                    
                    compliance_areas = [
                        "📋 Clauses obligatoires présentes",
                        "⚖️ Conformité Code des Assurances",
                        "🌍 Réglementation internationale", 
                        "💰 Limites de responsabilité",
                        "⏰ Délais de prescription"
                    ]
                    
                    if st.button("🎯 Lancer l'analyse de conformité"):
                        st.subheader("📊 Résultats de Conformité")
                        
                        # Mock compliance results
                        compliance_results = {
                            "Clauses obligatoires": {"status": "✅", "score": 95, "details": "19/20 clauses présentes"},
                            "Code des Assurances": {"status": "⚠️", "score": 78, "details": "2 articles à réviser"},
                            "Réglementation ACAPS": {"status": "✅", "score": 92, "details": "Conforme aux directives"},
                            "Limites financières": {"status": "✅", "score": 100, "details": "Dans les limites légales"},
                            "Délais légaux": {"status": "❌", "score": 45, "details": "Délais non conformes"}
                        }
                        
                        for area, result in compliance_results.items():
                            col_a, col_b, col_c = st.columns([2, 1, 2])
                            with col_a:
                                st.write(f"{result['status']} **{area}**")
                            with col_b:
                                st.metric("Score", f"{result['score']}%")
                            with col_c:
                                st.write(result['details'])

            elif st.session_state.contract_legal_section == 3:
                # Compliance Review Section
                st.subheader("📋 Révision de Conformité")
                
                st.info("Cette section détaille les problèmes de conformité identifiés et propose des corrections.")
                
                # Issues identified
                st.subheader("⚠️ Problèmes Identifiés")
                
                issues = [
                    {
                        "severity": "🔴 Critique",
                        "category": "Délais de prescription",
                        "description": "Article 15: Délai de 2 ans non conforme (minimum 3 ans requis)",
                        "recommendation": "Modifier l'article 15 pour porter le délai à 3 ans minimum",
                        "legal_ref": "Art. 62 du Code des Assurances"
                    },
                    {
                        "severity": "🟡 Attention", 
                        "category": "Clause de force majeure",
                        "description": "Définition trop restrictive des événements de force majeure",
                        "recommendation": "Élargir la définition selon jurisprudence récente",
                        "legal_ref": "Arrêt Cour de Cassation 2023-456"
                    },
                    {
                        "severity": "🟢 Mineur",
                        "category": "Modalités de paiement",
                        "description": "Clause de paiement peu détaillée",
                        "recommendation": "Préciser les modalités et délais de règlement",
                        "legal_ref": "Circulaire ACAPS 2024-01"
                    }
                ]
                
                for i, issue in enumerate(issues):
                    with st.expander(f"{issue['severity']} - {issue['category']}"):
                        st.markdown(f"**📝 Description:** {issue['description']}")
                        st.markdown(f"**💡 Recommandation:** {issue['recommendation']}")
                        st.markdown(f"**📚 Référence légale:** {issue['legal_ref']}")
                        
                        col_fix1, col_fix2 = st.columns(2)
                        with col_fix1:
                            st.button(f"✏️ Proposer correction", key=f"fix_{i}")
                        with col_fix2:
                            st.button(f"📎 Exporter détail", key=f"export_{i}")

            else:  # Section 4 - Final Report
                st.subheader("📄 Rapport Final de Conformité")
                
                # Generate comprehensive report
                st.markdown("""
                <div class="info-card">
                    <h3>📊 Résumé Exécutif</h3>
                    <p><strong>Score global de conformité: 82/100</strong></p>
                    <p>Le contrat analysé présente un bon niveau de conformité général avec quelques ajustements nécessaires.</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Detailed scoring
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Conformité Légale", "82%", "🔴 -18%")
                with col2:
                    st.metric("Clauses Obligatoires", "95%", "✅ +95%") 
                with col3:
                    st.metric("Risque Juridique", "Moyen", "⚠️")
                
                # Export options
                st.subheader("📤 Export du Rapport")
                
                export_format = st.radio("Format d'export", [
                    "📄 PDF Détaillé",
                    "📊 Excel avec données", 
                    "📧 Email de synthèse",
                    "🔗 Lien de partage sécurisé"
                ])
                
                if st.button("📤 Générer et télécharger", type="primary"):
                    st.success("✅ Rapport généré avec succès!")
                    st.download_button(
                        "⬇️ Télécharger le rapport",
                        data="Rapport de conformité généré...",  # In real app, generate actual report
                        file_name=f"rapport_conformite_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                        mime="application/pdf"
                    )

        elif st.session_state.current_page == "Geospatial Contract View":
            st.markdown('<h1 class="main-title">🗺️ Vue Géospatiale des Contrats</h1>', unsafe_allow_html=True)
                  
            # Mock geospatial features
            st.subheader("🌍 Cartographie Interactive des Contrats")
                
            col1, col2 = st.columns([3, 1])
                
            with col1:
                    # Map controls
                    st.subheader("🎛️ Contrôles de la Carte")
                    
                    col_a, col_b, col_c = st.columns(3)
                    
                    with col_a:
                        map_layer = st.selectbox("Couche de base", [
                            "🗺️ Topographique",
                            "🛰️ Satellite", 
                            "🏙️ Urbaine",
                            "🌊 Risques naturels"
                        ])
                    
                    with col_b:
                        contract_filter = st.multiselect("Types de contrats", [
                            "🏢 Entreprises",
                            "🏠 Habitations", 
                            "🚗 Automobiles",
                            "Catastrophes naturelles",
                            "Traité",
                            "Facultatif"
                        ], default=["Catastrophes naturelles", "Traité"])
                    
                    with col_c:
                        risk_overlay = st.checkbox("🎯 Superposer zones à risque", True)
                    
                    # Mock map placeholder
                    st.markdown("""
                    <div class="info-card" style="height: 400px; background: #f8f9fa; border: 1px solid #dee2e6; border-radius: 10px; padding: 20px;">
                        <h4>🗺️ Carte Interactive Géospatiale</h4>
                        <p>Visualisation intégrée avec :</p>
                        <ul>
                            <li>📍 <strong>125 contrats actifs</strong> localisés</li>
                            <li>🎯 <strong>Zones à risque</strong> colorées par intensité</li>
                            <li>📊 <strong>Clusters de densité</strong> des assurés</li>
                            <li>🛰️ <strong>Imagerie satellite</strong> temps réel</li>
                        </ul>
                        <p><em>🔧 Intégration avec Google Maps / OpenStreetMap en cours...</em></p>
                        
                        <div style="background: #f0f8f0; padding: 15px; border-radius: 10px; margin-top: 20px;">
                            <h5>🎯 Fonctionnalités Avancées</h5>
                            <ul>
                                <li>🔍 Zoom sur coordonnées GPS précises</li>
                                <li>📐 Calcul de distances et surfaces</li>
                                <li>🌡️ Données météo superposées</li>
                                <li>📈 Analyse de concentration des risques</li>
                            </ul>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Geospatial analysis tools
                    st.subheader("🔧 Outils d'Analyse Géospatiale")
                    
                    analysis_tools = st.tabs(["📍 Géocodage", "📏 Mesures", "🎯 Hotspots"])
                    
                    with analysis_tools[0]:
                        geocoding_tab()
                    
                    with analysis_tools[1]:
                        measurement_tab()
                    
                    with analysis_tools[2]:
                        hotspots_tab()
                
            with col2:
                    # Side panel with additional info
                    st.subheader("📊 Statistiques")
                    st.metric("Contrats totaux", "125")
                    st.metric("Zones à risque", "8")
                    st.metric("Couverture (%)", "94.2")
                    
                    st.subheader("🎯 Légende")
                    st.markdown("""
                    - 🔴 **Risque élevé**
                    - 🟡 **Risque moyen** 
                    - 🟢 **Risque faible**
                    - 📍 **Contrats actifs**
                    """)

# Main execution
if __name__ == "__main__":
    main()
