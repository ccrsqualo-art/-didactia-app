"""
DidactIA — Generador de Material Didáctico con IA
Caso Práctico Unidad 3, materia Generative IA — Maestría en Ciencia de Datos y
Analítica Visual, Instituto Europeo de Posgrado.

Aplicación de elección personal, aplicada al entorno profesional del autor
(formador corporativo), en lugar del escenario de marketing/publicidad
propuesto en el enunciado original.

Funcionalidades:
- Generación de imágenes ilustrativas para material de curso (Pollinations.ai)
- Generación de diagramas de flujo correctos vía código Mermaid (Groq/Llama),
  agregada tras detectar que los modelos de imagen no representan bien
  diagramas con lógica real (ver nota de hallazgo en la Sección de diagramas).
- Edición de contenido de texto con IA (Groq / Llama 3.3 70B)
- Roles simples: Instructor / Revisor
- Historial de versiones de contenido editado
- Comentarios de revisión
"""

import urllib.parse
from datetime import datetime

import streamlit as st
import requests
import streamlit.components.v1 as components
from groq import Groq

st.set_page_config(page_title="DidactIA", page_icon="🎨", layout="wide")

# ============================================================================
# CONFIGURACIÓN
# ============================================================================
ESTILOS_IMAGEN = {
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

SYSTEM_PROMPT_MERMAID = """Eres un asistente que convierte descripciones de procesos en código
Mermaid válido para diagramas de flujo (flowchart TD).

Reglas:
- Responde ÚNICAMENTE con el código Mermaid, sin explicaciones, sin comentarios,
  sin bloques de markdown (nada de ```mermaid).
- Usa "flowchart TD" como primera línea.
- Usa IDs cortos (A, B, C...) y etiquetas descriptivas entre corchetes.
- Usa flechas simples (-->) para conectar los pasos en el orden lógico correcto.
- Si el proceso tiene una decisión (sí/no), usa la sintaxis de rombo {Pregunta}
  y etiqueta las flechas de salida con "Sí" y "No".
- Máximo 10 nodos, para que el diagrama sea legible."""

# ============================================================================
# ESTADO DE SESIÓN
# ============================================================================
if "galeria" not in st.session_state:
    st.session_state.galeria = []
if "diagramas" not in st.session_state:
    st.session_state.diagramas = []
if "contenido_actual" not in st.session_state:
    st.session_state.contenido_actual = ""
if "version_contenido" not in st.session_state:
    st.session_state.version_contenido = 0
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


def generar_diagrama_mermaid(client: Groq, descripcion: str) -> str:
    respuesta = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT_MERMAID},
            {"role": "user", "content": descripcion},
        ],
        temperature=0.2,
    )
    codigo = respuesta.choices[0].message.content.strip()
    # Por si el modelo agrega el bloque de markdown a pesar de la instrucción
    codigo = codigo.replace("```mermaid", "").replace("```", "").strip()
    return codigo


def render_mermaid(codigo: str, key: str):
    html = f"""
    <div class="mermaid">
    {codigo}
    </div>
    <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
    <script>
        mermaid.initialize({{ startOnLoad: true, theme: 'default' }});
    </script>
    """
    components.html(html, height=400, scrolling=True)


def editar_contenido(client: Groq, texto_original: str, accion: str) -> str:
    instruccion = ACCIONES_TEXTO[accion]
    respuesta = client.chat.completions.create(
        model="openai/gpt-oss-120b",
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


def obtener_cliente_groq():
    if not groq_api_key:
        st.error("Ingresa tu API key de Groq en la barra lateral para continuar.")
        return None
    return Groq(api_key=groq_api_key)


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
            help="Obtén una gratis en console.groq.com/keys. Necesaria para diagramas y edición de texto (no para imágenes ilustrativas).",
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

tab_imagenes, tab_diagramas, tab_contenido = st.tabs([
    "🖼️ Imágenes ilustrativas", "🔀 Diagramas de flujo", "✏️ Edición de contenido",
])

# ============================================================================
# TAB 1: IMÁGENES ILUSTRATIVAS (Pollinations)
# ============================================================================
with tab_imagenes:
    st.subheader("Generar una imagen ilustrativa para tu material de curso")
    st.caption(
        "Úsalo para portadas, ambientación visual o ilustraciones de apoyo. "
        "Para diagramas de flujo o procesos con pasos, usa la pestaña 'Diagramas de flujo' — "
        "los modelos de imagen no representan bien la lógica de un proceso (ver nota ahí)."
    )

    if rol != "Instructor":
        st.info("Estás en modo Revisor. Puedes ver la galería generada, pero solo el Instructor puede generar nuevas imágenes.")

    col1, col2 = st.columns([2, 1])
    with col1:
        prompt_imagen = st.text_area(
            "Describe la imagen que necesitas",
            placeholder="Ej. escritorio de oficina moderno con laptop y gráficas financieras, ambiente profesional",
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
# TAB 2: DIAGRAMAS DE FLUJO (Mermaid) — agregado tras el hallazgo 1
# ============================================================================
with tab_diagramas:
    st.subheader("Generar un diagrama de flujo correcto")

    with st.expander("📋 Por qué existe esta pestaña (hallazgo del desarrollo)"):
        st.write(
            "En una primera versión de esta app, los diagramas de proceso se generaban "
            "con el mismo modelo de imágenes que las ilustraciones (Pollinations/difusión). "
            "El resultado no representaba una secuencia lógica real: aparecían varias cajas "
            "sueltas, sin conexión coherente entre ellas, y el texto dentro de la imagen salía "
            "distorsionado o ilegible. La causa es que los modelos de difusión generan píxeles "
            "por similitud visual con su entrenamiento, no comprenden relaciones lógicas entre "
            "pasos ni texto como caracteres discretos. La corrección fue cambiar de enfoque: "
            "en vez de pedirle a un modelo de imágenes que 'dibuje' el diagrama, se le pide a "
            "un modelo de texto (Llama, vía Groq) que genere el código del diagrama en formato "
            "Mermaid, y ese código se renderiza con una librería que sí entiende su estructura. "
            "El modelo de texto nunca dibuja nada directamente; solo describe la lógica en un "
            "lenguaje que otra herramienta sabe interpretar de forma exacta."
        )

    if rol != "Instructor":
        st.info("Estás en modo Revisor. Puedes ver los diagramas generados, pero solo el Instructor puede generar nuevos.")

    descripcion_proceso = st.text_area(
        "Describe el proceso paso a paso",
        placeholder="Ej. Un empleado solicita un gasto. El gerente revisa la solicitud. Si el monto excede $50,000, requiere aprobación adicional de Gerencia. Si no, se aprueba directamente y se registra el gasto.",
        disabled=(rol != "Instructor"),
    )

    if st.button("Generar diagrama", type="primary", disabled=(rol != "Instructor")):
        if not descripcion_proceso.strip():
            st.warning("Describe el proceso antes de generar el diagrama.")
        else:
            client = obtener_cliente_groq()
            if client:
                with st.spinner("Generando diagrama..."):
                    try:
                        codigo_mermaid = generar_diagrama_mermaid(client, descripcion_proceso)
                        st.session_state.diagramas.append({
                            "descripcion": descripcion_proceso,
                            "codigo": codigo_mermaid,
                            "fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        })
                        st.success("Diagrama generado correctamente.")
                    except Exception as e:
                        st.error(f"No se pudo generar el diagrama: {e}")

    st.divider()
    st.subheader("Diagramas generados en esta sesión")
    if not st.session_state.diagramas:
        st.caption("Aún no se ha generado ningún diagrama.")
    else:
        for i, d in enumerate(reversed(st.session_state.diagramas)):
            st.caption(f"{d['fecha']} — {d['descripcion'][:80]}...")
            render_mermaid(d["codigo"], key=f"mermaid_{i}")
            with st.expander("Ver código Mermaid generado"):
                st.code(d["codigo"], language="text")
            st.divider()

# ============================================================================
# TAB 3: EDICIÓN DE CONTENIDO
# ============================================================================
with tab_contenido:
    st.subheader("Editar contenido de texto para tu curso")

    contenido_widget = st.text_area(
        "Contenido (editable si eres Instructor)",
        value=st.session_state.contenido_actual,
        height=150,
        disabled=(rol != "Instructor"),
        key=f"widget_contenido_{st.session_state.version_contenido}",
    )
    if rol == "Instructor":
        st.session_state.contenido_actual = contenido_widget

    if rol == "Instructor":
        accion_sel = st.selectbox("¿Qué quieres hacer con este contenido?", list(ACCIONES_TEXTO.keys()))

        if st.button("Aplicar con IA", type="primary"):
            if not st.session_state.contenido_actual.strip():
                st.warning("Ingresa un contenido antes de aplicar una acción.")
            else:
                client = obtener_cliente_groq()
                if client:
                    with st.spinner("Procesando con IA..."):
                        try:
                            texto_previo = st.session_state.contenido_actual
                            resultado = editar_contenido(client, texto_previo, accion_sel)
                            st.session_state.historial_versiones.append({
                                "version_anterior": texto_previo,
                                "accion": accion_sel,
                                "fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
                            })
                            st.session_state.contenido_actual = resultado
                            st.session_state.version_contenido += 1
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
                    st.session_state.version_contenido += 1
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
    "Imágenes ilustrativas vía Pollinations.ai (gratuito, sin clave). Diagramas de flujo "
    "y edición de texto vía Groq / Llama 3.3 70B (capa gratuita)."
)
