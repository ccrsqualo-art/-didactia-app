"""
DidactIA — Generador de Material Didáctico con IA
Caso Práctico Unidad 3, materia Generative IA — Maestría en Ciencia de Datos y
Analítica Visual, Instituto Europeo de Posgrado.

Aplicación de elección personal, aplicada al entorno profesional del autor
(formador corporativo), en lugar del escenario de marketing/publicidad
propuesto en el enunciado original.

Funcionalidades:
- Generación de imágenes para material de curso (Pollinations.ai, gratuito)
- Edición de contenido de texto con IA (Groq / Llama 3.3 70B)
- Roles simples: Instructor / Revisor
- Historial de versiones de contenido editado
- Comentarios de revisión
"""

import os
import io
import urllib.parse
from datetime import datetime

import streamlit as st
import requests
from groq import Groq

st.set_page_config(page_title="DidactIA", page_icon="🎨", layout="wide")

# ============================================================================
# CONFIGURACIÓN
# ============================================================================
ESTILOS_IMAGEN = {
    "Diagrama / esquema": "clean minimalist diagram, flat design, white background, vector style",
    "Ilustración": "digital illustration, soft colors, friendly educational style",
    "Realista": "photorealistic, high detail, professional photography style",
    "Acuarela": "watercolor painting style, soft edges, artistic",
}

ACCIONES_TEXTO = {
    "Resumir": "Resume el siguiente texto en un párrafo breve, conservando las ideas clave.",
    "Expandir": "Expande el siguiente texto agregando más detalle y ejemplos, sin cambiar su intención original.",
    "Corregir estilo y gramática": "Corrige la gramática, ortografía y estilo del siguiente texto, manteniendo su significado y tono.",
    "Generar variación": "Redacta una variación alternativa del siguiente texto, con el mismo propósito pero distinta redacción.",
}

# ============================================================================
# ESTADO DE SESIÓN
# ============================================================================
if "galeria" not in st.session_state:
    st.session_state.galeria = []
if "contenido_actual" not in st.session_state:
    st.session_state.contenido_actual = ""
if "historial_versiones" not in st.session_state:
    st.session_state.historial_versiones = []
if "comentarios" not in st.session_state:
    st.session_state.comentarios = []


# ============================================================================
# FUNCIONES
# ============================================================================
def generar_imagen(prompt_usuario: str, estilo: str) -> bytes:
    prompt_completo = f"{prompt_usuario}, {ESTILOS_IMAGEN[estilo]}"
    prompt_codificado = urllib.parse.quote(prompt_completo)
    url = f"https://image.pollinations.ai/prompt/{prompt_codificado}?width=768&height=768&nologo=true"
    respuesta = requests.get(url, timeout=60)
    respuesta.raise_for_status()
    return respuesta.content


def editar_contenido(client: Groq, texto_original: str, accion: str) -> str:
    instruccion = ACCIONES_TEXTO[accion]
    respuesta = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": (
                "Eres un asistente de redacción para material didáctico de cursos "
                "corporativos. Responde únicamente con el texto solicitado, sin "
                "comentarios adicionales, introducciones ni explicaciones de lo que hiciste."
            )},
            {"role": "user", "content": f"{instruccion}\n\nTexto:\n{texto_original}"},
        ],
        temperature=0.5,
    )
    return respuesta.choices[0].message.content.strip()


# ============================================================================
# BARRA LATERAL
# ============================================================================
with st.sidebar:
    st.header("Configuración")

    try:
        groq_api_key_secret = st.secrets.get("GROQ_API_KEY", "")
    except Exception:
        groq_api_key_secret = ""

    if groq_api_key_secret:
        groq_api_key = groq_api_key_secret
        st.success("✅ API key configurada por el propietario de la app.")
    else:
        groq_api_key = st.text_input(
            "API key de Groq", type="password",
            help="Obtén una gratis en console.groq.com/keys. No se guarda en ningún lado.",
        )

    st.divider()
    rol = st.radio("Rol", ["Instructor", "Revisor"], help="El Instructor genera y edita contenido. El Revisor puede ver el contenido y dejar comentarios.")

    st.divider()
    st.caption(
        "Prototipo académico — Caso Práctico Unidad 3, Generative IA, IEP. "
        "No se almacenan datos personales; el contenido generado vive solo "
        "durante esta sesión del navegador."
    )

st.title("🎨 DidactIA")
st.caption("Generador de Material Didáctico con IA — prototipo aplicado a capacitación corporativa")

tab_imagenes, tab_contenido = st.tabs(["🖼️ Generación de imágenes", "✏️ Edición de contenido"])

# ============================================================================
# TAB 1: GENERACIÓN DE IMÁGENES
# ============================================================================
with tab_imagenes:
    st.subheader("Generar una imagen para tu material de curso")

    if rol != "Instructor":
        st.info("Estás en modo Revisor. Puedes ver la galería generada, pero solo el Instructor puede generar nuevas imágenes.")

    col1, col2 = st.columns([2, 1])
    with col1:
        prompt_imagen = st.text_area(
            "Describe la imagen que necesitas",
            placeholder="Ej. diagrama de flujo del proceso de aprobación de gastos en una planta de manufactura",
            disabled=(rol != "Instructor"),
        )
    with col2:
        estilo_sel = st.selectbox("Estilo", list(ESTILOS_IMAGEN.keys()), disabled=(rol != "Instructor"))

    if st.button("Generar imagen", type="primary", disabled=(rol != "Instructor")):
        if not prompt_imagen.strip():
            st.warning("Escribe una descripción antes de generar la imagen.")
        else:
            with st.spinner("Generando imagen..."):
                try:
                    imagen_bytes = generar_imagen(prompt_imagen, estilo_sel)
                    st.session_state.galeria.append({
                        "prompt": prompt_imagen,
                        "estilo": estilo_sel,
                        "imagen": imagen_bytes,
                        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    })
                    st.success("Imagen generada correctamente.")
                except Exception as e:
                    st.error(f"No se pudo generar la imagen: {e}")

    st.divider()
    st.subheader("Galería de esta sesión")
    if not st.session_state.galeria:
        st.caption("Aún no se ha generado ninguna imagen.")
    else:
        cols = st.columns(3)
        for i, item in enumerate(reversed(st.session_state.galeria)):
            with cols[i % 3]:
                st.image(item["imagen"], caption=f"{item['estilo']} — {item['fecha']}")
                st.caption(item["prompt"])
                st.download_button(
                    "Descargar", data=item["imagen"],
                    file_name=f"didactia_imagen_{i}.jpg", mime="image/jpeg",
                    key=f"descarga_{i}",
                )

# ============================================================================
# TAB 2: EDICIÓN DE CONTENIDO
# ============================================================================
with tab_contenido:
    st.subheader("Editar contenido de texto para tu curso")

    contenido_widget = st.text_area(
        "Contenido (editable si eres Instructor)",
        value=st.session_state.contenido_actual,
        height=150,
        disabled=(rol != "Instructor"),
        key="widget_contenido",
    )
    if rol == "Instructor":
        st.session_state.contenido_actual = contenido_widget

    if rol == "Instructor":
        accion_sel = st.selectbox("¿Qué quieres hacer con este contenido?", list(ACCIONES_TEXTO.keys()))

        if st.button("Aplicar con IA", type="primary"):
            if not st.session_state.contenido_actual.strip():
                st.warning("Ingresa un contenido antes de aplicar una acción.")
            elif not groq_api_key:
                st.error("Ingresa tu API key de Groq en la barra lateral para continuar.")
            else:
                with st.spinner("Procesando con IA..."):
                    try:
                        client = Groq(api_key=groq_api_key)
                        resultado = editar_contenido(client, st.session_state.contenido_actual, accion_sel)
                        st.session_state.historial_versiones.append({
                            "version_anterior": st.session_state.contenido_actual,
                            "accion": accion_sel,
                            "fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        })
                        st.session_state.contenido_actual = resultado
                        st.rerun()
                    except Exception as e:
                        st.error(f"No se pudo procesar el contenido: {e}")

    st.divider()
    st.subheader("Historial de versiones")
    if not st.session_state.historial_versiones:
        st.caption("Aún no hay versiones anteriores en esta sesión.")
    else:
        for i, v in enumerate(reversed(st.session_state.historial_versiones)):
            with st.expander(f"Versión anterior a '{v['accion']}' — {v['fecha']}"):
                st.write(v["version_anterior"])
                if rol == "Instructor" and st.button("Revertir a esta versión", key=f"revertir_{i}"):
                    st.session_state.contenido_actual = v["version_anterior"]
                    st.rerun()

    st.divider()
    st.subheader("Comentarios de revisión")
    comentario_nuevo = st.text_input("Dejar un comentario sobre el contenido actual", key="input_comentario")
    if st.button("Agregar comentario"):
        if comentario_nuevo.strip():
            st.session_state.comentarios.append({
                "rol": rol, "texto": comentario_nuevo,
                "fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
            })
            st.rerun()

    for c in reversed(st.session_state.comentarios):
        st.markdown(f"**{c['rol']}** ({c['fecha']}): {c['texto']}")

st.divider()
st.caption(
    "DidactIA — Prototipo académico, Caso Práctico Unidad 3, materia Generative IA, "
    "Maestría en Ciencia de Datos y Analítica Visual, Instituto Europeo de Posgrado. "
    "Generación de imágenes vía Pollinations.ai (gratuito, sin clave). Edición de "
    "texto vía Groq / Llama 3.3 70B (capa gratuita)."
)
