# DidactIA

Generador de material didáctico con IA — prototipo para el Caso Práctico Unidad 3
de la materia Generative IA (Maestría en Ciencia de Datos y Analítica Visual, IEP).

En vez de la app de marketing/publicidad que planteaba el enunciado original, la
apliqué a mi propio trabajo como formador corporativo: generar imágenes y
diagramas de apoyo para mis cursos, y editar contenido de texto con IA.

## Qué hace

- Genera imágenes ilustrativas (portadas, ambientación) con Pollinations.ai.
- Genera diagramas de flujo como código Mermaid, con Llama vía Groq, en vez de
  pedirle a un modelo de imágenes que los dibuje (ver la nota dentro de la app,
  pestaña "Diagramas de flujo" — el porqué de esa decisión está desarrollado
  en el documento de reflexión de la entrega).
- Edita texto (resumir, expandir, corregir, generar variación) con el mismo
  modelo.
- Dos roles simples: Instructor y Revisor.
- Guarda un historial de versiones del contenido editado.

## Archivos

- `app.py` — toda la app.
- `requirements.txt` — dependencias.

## Para correrlo local

```
pip install -r requirements.txt
streamlit run app.py
```

Necesita una API key de Groq (gratis en console.groq.com/keys) para las
pestañas de diagramas y edición de texto. La de imágenes ilustrativas no
necesita ninguna key.
