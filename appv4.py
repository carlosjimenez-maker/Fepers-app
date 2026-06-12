import streamlit as st
import pandas as pd
import unicodedata

# --- 1. CONFIGURACIÓN Y PWA ---
st.set_page_config(page_title="FEPER'S APP", layout="wide", page_icon="🟢", initial_sidebar_state="collapsed")

st.markdown("""
<style>
    /* 1. OCULTAR ELEMENTOS NATIVOS DE STREAMLIT (Nube) */
    [data-testid="stHeader"] {display: none !important;} /* Oculta la barra superior entera */
    [data-testid="stToolbar"] {display: none !important;} /* Oculta el menú derecho */
    [data-testid="stAppDeployButton"] {display: none !important;} /* Oculta el botón de perfil/deploy */
    [data-testid="stFooter"] {display: none !important;} /* Oculta el footer "Made with Streamlit" */
    footer {display: none !important;}
    #MainMenu {display: none !important;}

    /* 2. ESPACIADO GENERAL DE LA APP */
    .block-container {
        padding-top: 2rem !important;
        padding: 1rem !important;
    }

    /* 3. AUTO-AJUSTE DE LOGOS */
    div[data-testid="stImage"] {
        display: flex;
        justify-content: center; 
        align-items: center;
    }
    div[data-testid="stImage"] img {
        max-height: 40px !important; 
        width: auto !important;
        object-fit: contain; 
    }

    /* 4. ESTILO DE BOTONES PRINCIPALES */
    div.stButton > button, div.stLinkButton > a {
        width: 100%;
        min-height: 4rem; 
        font-size: 1.1rem !important; 
        font-weight: 800 !important;
        background-color: #007A33; 
        color: #FFFFFF !important;
        border-radius: 12px; 
        border: 2px solid transparent;
        box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.15); 
        text-decoration: none;
        text-align: center;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: all 0.2s ease-in-out; 
    }
    div.stButton > button:focus, div.stLinkButton > a:focus {
        outline: 4px solid #000000 !important; 
        outline-offset: 3px;
        background-color: #005A22;
    }
    div.stButton > button:active, div.stLinkButton > a:active {
        transform: translateY(2px);
    }

    /* 5. ESTILO BOTÓN "VOLVER" */
    .btn-volver > div > button {
        min-height: 3.5rem !important;
        background-color: #E0E0E0 !important;
        color: #000000 !important;
        font-size: 1.1rem !important;
        font-weight: bold !important;
        border: 2px solid #555555 !important;
    }

    /* 6. ESTILO DEL TÍTULO APP */
    .titulo-app {
        text-align: center;
        font-weight: 900; 
        font-size: 3.5rem; 
        margin-top: 10px;
        margin-bottom: 5px;
        background: linear-gradient(135deg, #004d20 0%, #00A84D 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        filter: drop-shadow(2px 4px 6px rgba(0, 0, 0, 0.15));
        letter-spacing: -1.5px; 
    }
    .titulo-adorno {
        width: 80px;
        height: 6px;
        background: linear-gradient(90deg, #007A33, #00A84D);
        margin: 0 auto 30px auto; 
        border-radius: 10px;
        box-shadow: 0px 2px 4px rgba(0, 0, 0, 0.1);
    }

    /* 7. ESTILO DEL FOOTER LEGAL (El tuyo propio) */
    .footer-legal {
        text-align: center;
        font-size: 0.8rem;
        color: #666666;
        margin-top: 30px;
        padding: 15px;
        border-top: 1px solid #DDDDDD;
    }
    /* 8. LA GUERRA FINAL CONTRA LA INSIGNIA FLOTANTE */
    /* Usamos *= (contiene) para atraparlo sin importar qué basura pongan delante */
    [class*="viewerBadge"] {
        display: none !important;
    }
    [class*="ViewerBadge"] {
        display: none !important;
    }
    
    /* Bloqueo a la fuerza bruta: cualquier enlace que vaya a streamlit se oculta */
    a[href*="streamlit.io"] {
        display: none !important;
    }
    a[href*="streamlit.app"] {
        display: none !important;
    }

</style>
""", unsafe_allow_html=True)


# --- 2. FUNCIONES DE AYUDA (Buscador Anti-tildes) ---
def quitar_tildes(texto):
    """Elimina tildes y caracteres especiales para búsquedas más flexibles"""
    if pd.isna(texto):
        return ""
    return ''.join(c for c in unicodedata.normalize('NFD', str(texto)) if unicodedata.category(c) != 'Mn').lower()

LISTA_MUNICIPIOS = [
    "Todas", "Algeciras", "La Línea de la Concepción", "San Roque", 
    "Los Barrios", "Tarifa", "Jimena de la Frontera", 
    "Castellar de la Frontera", "San Martín del Tesorillo"
]

# --- 3. GESTIÓN DE SESIÓN Y VÍDEO INICIAL ---
if 'pantalla' not in st.session_state:
    st.session_state.pantalla = 'inicio'
if 'video_visto' not in st.session_state:
    st.session_state.video_visto = False

def cambiar_pantalla(nueva_pantalla):
    st.session_state.pantalla = nueva_pantalla

@st.dialog("Mensaje Institucional Inicial")
def video_intro():
    st.markdown("### 🏛️ Junta de Andalucía")
    st.video("assets/Video_tutorial_1.mp4") # O el enlace de YouTube si lo dejaste así
    
    # Botón único que cierra el diálogo y no vuelve a salir en esta sesión
    if st.button("Entrar a la aplicación", width="stretch"): 
        st.session_state.video_visto = True
        st.rerun()

if not st.session_state.video_visto:
    video_intro()
    
# --- 4. CONEXIÓN A GOOGLE SHEETS ---
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRTxWEONnnOJS5KS-VpMzZtLp5Q62AGqOP4kX2PgmBf3VwO_EClG-BXPKuLOog3i2RX19GrPykLk2Nn/pub?output=csv"

@st.cache_data(ttl=10)
def cargar_datos(url):
    try:
        url_final = f"{url}&nocache={pd.Timestamp.now().timestamp()}"
        df = pd.read_csv(url_final)
        df.columns = df.columns.str.strip()
        # Añadida la columna 'Centro_Busqueda' para el filtro inteligente
        df['Curso_Norm'] = df['Curso'].apply(quitar_tildes)
        return df.dropna(subset=['Curso'])
    except:
        # Añadido 'Centro' a la lista por defecto para que no de error si está vacío
        return pd.DataFrame(columns=['Curso', 'Categoria', 'Requisitos', 'Localidad', 'Enlace', 'Centro', 'Curso_Norm'])

df = cargar_datos(SHEET_URL)

# --- 5. CABECERA ---
st.markdown("<h1 class='titulo-app' aria-label='Fépers App'>FEPER'S APP</h1>", unsafe_allow_html=True)
st.markdown("<div class='titulo-adorno'></div>", unsafe_allow_html=True)

# --- 6. NAVEGACIÓN ---

# 📍 MENÚ PRINCIPAL
if st.session_state.pantalla == 'inicio':
    st.subheader("Menú Principal")
    st.button("🎓 Formación Reglada", on_click=cambiar_pantalla, args=('reglada',))
    st.write("") 
    st.button("💼 Empleabilidad", on_click=cambiar_pantalla, args=('empleabilidad',))
    st.write("")
    st.button("📺 Tutoriales", on_click=cambiar_pantalla, args=('videos',))


# 📍 FORMACIÓN REGLADA (Submenú)
elif st.session_state.pantalla == 'reglada':
    st.markdown("<div class='btn-volver'>", unsafe_allow_html=True)
    st.button("⬅️ Volver al Inicio", on_click=cambiar_pantalla, args=('inicio',))
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.subheader("🎓 Formación Reglada")
    st.button("📋 Con Requisitos previos", on_click=cambiar_pantalla, args=('reglada_con',))
    st.write("")
    st.button("🟢 Sin Requisitos previos", on_click=cambiar_pantalla, args=('reglada_sin',))


# 📍 RESULTADOS REGLADA
elif st.session_state.pantalla in ['reglada_con', 'reglada_sin']:
    st.markdown("<div class='btn-volver'>", unsafe_allow_html=True)
    st.button("⬅️ Volver atrás", on_click=cambiar_pantalla, args=('reglada',))
    st.markdown("</div>", unsafe_allow_html=True)
    
    requisito = "Con" if st.session_state.pantalla == 'reglada_con' else "Sin"
    st.subheader(f"🎓 Formación Reglada ({requisito} Requisitos)")
    
    df_f = df[(df['Categoria'].str.lower() == 'reglada') & (df['Requisitos'].str.contains(requisito, case=False, na=False))]
    
    col1, col2 = st.columns(2)
    with col1:
        filtro_mun = st.selectbox("📍 Localidad:", LISTA_MUNICIPIOS)
    with col2:
        filtro_txt = st.text_input("🔍 Buscar curso (ej. informatica)...")
        
    if filtro_mun != "Todas":
        df_f = df_f[df_f['Localidad'] == filtro_mun]
        
    if filtro_txt:
        txt_norm = quitar_tildes(filtro_txt).strip()
        palabras_busqueda = txt_norm.split()
        for palabra in palabras_busqueda:
            df_f = df_f[df_f['Curso_Norm'].str.contains(palabra, case=False, na=False)]
        
    st.write("---")
    
    if df_f.empty:
        st.warning(f"Actualmente no hay cursos disponibles con estos filtros.", icon="⚠️")
    else:
        # --- 🪄 MAGIA DE AGRUPACIÓN ---
        # 1. Rellenamos las celdas vacías temporalmente para que Python no borre filas por error
        df_f = df_f.fillna({"Grado": "", "Enlace": "", "Centro": "Centro por determinar"})
        
        # 2. Agrupamos por Curso y Localidad
        df_agrupado = df_f.groupby(['Curso', 'Localidad', 'Grado', 'Enlace'], dropna=False).agg({
            # Juntamos todos los centros distintos, separados por un salto de línea y el icono
            'Centro': lambda x: '<br>🏫 '.join(sorted(set(x)))
        }).reset_index()

        # 3. Pintamos la información ya agrupada
        for _, fila in df_agrupado.iterrows():
            with st.container():
                
                # Etiqueta del Grado
                grado_txt = ""
                if fila['Grado'] != "":
                    grado_txt = f" <span style='color: #007A33; font-weight: bold;'>[{str(fila['Grado']).upper()}]</span>"
                
                # Nombre del curso, TODOS los centros agrupados y la localidad abajo
                centros_combinados = fila['Centro']
                st.markdown(f"**{fila['Curso']}**{grado_txt}<br>🏫 {centros_combinados}<br>📍 {fila['Localidad']}", unsafe_allow_html=True)
                
                # Enlaces de Requisitos Inteligentes
                enlaces_requisitos = {
                    "basico": "https://www.juntadeandalucia.es/educacion/portals/web/formacion-profesional-andaluza/fp-grado-basico/requisitos",
                    "medio": "https://www.juntadeandalucia.es/educacion/portals/web/formacion-profesional-andaluza/fp-grado-medio/requisitos",
                    "superior": "https://www.juntadeandalucia.es/educacion/portals/web/formacion-profesional-andaluza/fp-grado-superior/requisitos"
                }
                
                grado_celda = str(fila['Grado']).lower().strip() if fila['Grado'] != "" else "medio"
                enlace_requisitos_final = enlaces_requisitos.get(grado_celda, enlaces_requisitos["medio"])
                
                enlace_curso = str(fila['Enlace']) if str(fila['Enlace']).startswith('http') else "https://www.juntadeandalucia.es"
                enlace_matricula_final = "https://www.juntadeandalucia.es/temas/estudiar/fp/matriculacion.html"
                
                # Botones Dinámicos
                if st.session_state.pantalla == 'reglada_con':
                    b1, b2, b3 = st.columns(3)
                    with b1:
                        st.link_button("ℹ️ Info", enlace_curso)
                    with b2:
                        st.link_button("📋 Requisitos", enlace_requisitos_final)
                    with b3:
                        st.link_button("✍️ Matrícula", enlace_matricula_final)
                else:
                    b1, b2 = st.columns(2)
                    with b1:
                        st.link_button("ℹ️ Info", enlace_curso)
                    with b2:
                        st.link_button("✍️ Matrícula", enlace_matricula_final)
                
                st.divider()


# 📍 EMPLEABILIDAD
elif st.session_state.pantalla == 'empleabilidad':
    st.markdown("<div class='btn-volver'>", unsafe_allow_html=True)
    st.button("⬅️ Volver al Inicio", on_click=cambiar_pantalla, args=('inicio',))
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.subheader("💼 Empleabilidad")
    
    df_emp = df[df['Categoria'].str.lower() == 'empleabilidad']
    
    col1, col2 = st.columns(2)
    with col1:
        filtro_mun = st.selectbox("📍 Localidad:", LISTA_MUNICIPIOS)
    with col2:
        filtro_txt = st.text_input("🔍 Buscar...")
        
    if filtro_mun != "Todas":
        df_emp = df_emp[df_emp['Localidad'] == filtro_mun]
    if filtro_txt:
        txt_norm = quitar_tildes(filtro_txt)
        df_emp = df_emp[df_emp['Curso_Norm'].str.contains(txt_norm, case=False, na=False)]
        
    st.write("---")
    
    if df_emp.empty:
        st.warning(f"No hay ofertas de empleabilidad disponibles en este momento.", icon="⚠️")
    else:
        for _, fila in df_emp.iterrows():
            with st.container():
                centro_txt = fila['Centro'] if 'Centro' in fila and pd.notna(fila['Centro']) else "Entidad colaboradora"
                st.markdown(f"**{fila['Curso']}**<br>🏫 {centro_txt} | 📍 {fila['Localidad']}", unsafe_allow_html=True)
                
                # 2 Botones para Empleabilidad
                b1, b2 = st.columns(2)
                enlace_curso = str(fila['Enlace']) if pd.notna(fila['Enlace']) and str(fila['Enlace']).startswith('http') else "https://www.juntadeandalucia.es"
                with b1:
                    st.link_button("ℹ️ Info", enlace_curso)
                with b2:
                    st.link_button("✍️ Matrícula", "https://ENLACE_MATRICULA_AQUI")
                    
                st.divider()


# 📍 GALERÍA DE VÍDEOS
elif st.session_state.pantalla == 'videos':
    st.markdown("<div class='btn-volver'>", unsafe_allow_html=True)
    st.button("⬅️ Volver al Inicio", on_click=cambiar_pantalla, args=('inicio',))
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.subheader("📺 Galería Audiovisual") 
    st.video("assets/video_tutorial_1.mp4")
    st.divider()
# --- SECCIÓN PDF ---
    st.markdown("#### 📄 Documentación Escrita")
    
    # El bloque "try" intenta leer el PDF de tu carpeta assets. 
    # Si no lo encuentra, no rompe la app, solo avisa.
    try:
        with open("assets/guia.pdf", "rb") as pdf_file:
            pdf_bytes = pdf_file.read()
            
        st.download_button(
            label="⬇️ Descargar Guía en PDF",
            data=pdf_bytes,
            file_name="Guia_Fepers.pdf",
            mime="application/pdf"
        )
    except FileNotFoundError:
        st.info("El manual en PDF estará disponible próximamente.")
        
    st.divider()

# --- 7. PIE DE PÁGINA: LOGOS INSTITUCIONALES Y AVISO LEGAL ---
# st.write("")
#st.write("")
#st.markdown("<h4 style='text-align: center; color: #007A33; font-size: 1.2rem;'>Entidades Promotoras y Colaboradoras</h4>", unsafe_allow_html=True)

# 🎯 ESTE ES EL MARCADOR INVISIBLE
#st.markdown("<div id='marcador-logos'></div>", unsafe_allow_html=True)

#col_l1, col_l2, col_l3, col_l4, col_l5 = st.columns(5)
#with col_l1:
#    st.image("assets/JR.png", width="stretch") 
#with col_l2:
#    st.image("assets/CA.jpg", width="stretch")
#with col_l3:
#    st.image("assets/CP.jpg", width="stretch")
#with col_l4:
#    st.image("assets/KU.jpg", width="stretch")
#with col_l5:
#    st.image("assets/junta.png", width="stretch") */ 
    
    # --- 7. PIE DE PÁGINA: LOGOS INSTITUCIONALES ---
st.write("")
st.write("")
st.markdown("<h4 style='text-align: center; color: #007A33; font-size: 1.2rem;'>Entidades Promotoras y Colaboradoras</h4>", unsafe_allow_html=True)

# 1. Función para leer las imágenes sin depender de Streamlit
import base64
def cargar_logo(ruta):
    try:
        with open(ruta, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except:
        return "" # Si algún logo no existe aún, no rompe la app

# 2. Cargamos los 5 logos
l_jr = cargar_logo("assets/JR.png")
l_ca = cargar_logo("assets/CA.png")
l_cp = cargar_logo("assets/CP.png")
l_ku = cargar_logo("assets/KU.png") # Pon el nombre de tu archivo 4
l_junta = cargar_logo("assets/junta.png") # Pon el nombre de tu archivo 5

# 3. Construimos la fila en HTML Puro (100% Inmune a móviles)
html_logos = f"""
<div style="display: flex; justify-content: center; align-items: center; flex-wrap: wrap; gap: 15px;">
    <img src="data:image/png;base64,{l_jr}" style="max-height: 50px; width: auto; object-fit: contain;">
    <img src="data:image/png;base64,{l_ca}" style="max-height: 50px; width: auto; object-fit: contain;">
    <img src="data:image/png;base64,{l_cp}" style="max-height: 50px; width: auto; object-fit: contain;">
    <img src="data:image/png;base64,{l_ku}" style="max-height: 50px; width: auto; object-fit: contain;">
    <img src="data:image/png;base64,{l_junta}" style="max-height: 50px; width: auto; object-fit: contain;">
</div>
"""
st.markdown(html_logos, unsafe_allow_html=True)

st.markdown("""
<div class="footer-legal">
    <p><b>Política de Privacidad y Uso de Cookies:</b> Esta aplicación tiene una finalidad estrictamente informativa y <b>no recopila, almacena ni trata datos personales</b> de los usuarios.<br> 
    Al reproducir contenido multimedia o acceder a enlaces externos, plataformas de terceros podrían utilizar cookies técnicas o de análisis. El uso de esta aplicación implica la aceptación de estas condiciones.</p>
    <p>&copy; 2026 FEPER'S APP - Comarca del Campo de Gibraltar</p>
</div>
""", unsafe_allow_html=True)
