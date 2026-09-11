# DidactIA

Generador de Material Didáctico con IA — prototipo académico.

**Caso Práctico Unidad 3**, materia Generative IA, Maestría en Ciencia de Datos y
Analítica Visual, Instituto Europeo de Posgrado.

Aplicación de elección personal, orientada al entorno profesional del autor
(formador corporativo), en lugar del escenario de marketing/publicidad del
enunciado original (que la profesora confirmó como alternativa válida).

## Qué hace

- **Generación de imágenes** para material de curso, con selección de estilo,
  usando Pollinations.ai (gratuito, sin API key).
- **Edición de contenido de texto** con IA (resumir, expandir, corregir,
  generar variación), usando Llama 3.3 70B vía la API gratuita de Groq.
- **Roles simples**: Instructor (genera y edita) y Revisor (visualiza y
  comenta).
- **Historial de versiones** del contenido editado, con opción de reversión.
- **Comentarios de revisión** asociados a cada rol.

## Estructura

```
didactia_app/
├── app.py              # Aplicación Streamlit
├── requirements.txt    # Dependencias
└── README.md
```

## Cómo desplegarlo (gratis) en Streamlit Community Cloud

1. Sube este contenido a un repositorio de GitHub.
2. Entra a share.streamlit.io e inicia sesión con tu cuenta de GitHub.
3. "New app" → selecciona el repositorio, la rama y `app.py`.
4. (Opcional) En Advanced settings → Secrets, agrega `GROQ_API_KEY = "tu_key"`
   para que los visitantes no necesiten ingresar su propia key.
5. Deploy.

## Cómo correrlo localmente

```bash
pip install -r requirements.txt
streamlit run app.py
```
