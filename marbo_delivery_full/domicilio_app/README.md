# Food Delivery Flask App for Vercel

Este proyecto es una aplicación de delivery de comida hecha con Flask, lista para desplegar en Vercel usando `vercel-python-wsgi`.

## Estructura del proyecto

```
domicilio_app/
├── api/
│   └── index.py           # Handler para Vercel
├── backend/
│   ├── app.py             # App principal Flask
│   ├── ...                # Resto de tu backend
│   └── templates/         # Templates HTML
├── requirements.txt       # Dependencias (incluye vercel-python-wsgi)
└── vercel.json            # Configuración de Vercel
```

## Deploy en Vercel desde GitHub

1. **Sube todo el contenido de `domicilio_app` a tu repositorio de GitHub.**
2. **En Vercel:**
   - Ve a https://vercel.com/import/git y selecciona tu repo.
   - Cuando te pregunte la raíz del proyecto, selecciona la carpeta `domicilio_app`.
   - Vercel detectará automáticamente `vercel.json` y usará Python.
   - Haz click en Deploy.
3. **¡Listo!**
   - Tu app estará disponible en la URL que te da Vercel.

## Notas importantes
- El filesystem de Vercel es efímero: los datos de SQLite NO se guardan entre deploys. Para producción, usa una base de datos externa.
- Si cambias la estructura de carpetas, ajusta el import en `api/index.py`.
- Todas las dependencias deben estar en `requirements.txt`.

---

¿Dudas? Consulta la documentación oficial de [vercel-python-wsgi](https://github.com/juancarlospaco/vercel-python-wsgi) o pregunta aquí.
