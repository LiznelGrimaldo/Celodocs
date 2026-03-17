# 📊 CeloDocs — Guía de instalación y uso

## ¿Qué hace esta herramienta?
Extrae Objects y Events de Celonis (OCPM), genera reportes en **Excel y JSON**, y opcionalmente los envía por correo automáticamente.

---

## ✅ Requisitos previos
- Python 3.10 o superior instalado  
  → Descarga: https://www.python.org/downloads/
- Acceso a tu instancia de Celonis con un API Token

---

## 🚀 Instalación (solo la primera vez)

### Paso 1 — Abrir terminal
- **Windows**: presiona `Win + R`, escribe `cmd`, Enter
- **Mac/Linux**: abre la aplicación "Terminal"

### Paso 2 — Ir a la carpeta del proyecto
```bash
cd ruta/a/la/carpeta/celodocs
```

### Paso 3 — Instalar dependencias
```bash
pip install -r requirements.txt
```
> ⏳ Esto puede tardar 1-2 minutos la primera vez.

---

## ▶️ Cómo usar la herramienta (cada vez que quieras ejecutarla)

### Opción A — Interfaz visual (recomendada para no técnicos)

```bash
streamlit run app_streamlit.py
```

Se abrirá automáticamente una página en tu navegador en http://localhost:8501

Allí llenas los campos:
1. **URL de Celonis** y **API Token**
2. Seleccionas los namespaces que quieres extraer
3. (Opcional) configuras el correo para recibir el reporte
4. Haces clic en **Ejecutar extracción**
5. Descargas el Excel directamente desde la pantalla

---

### Opción B — Desde la línea de comandos

1. Crea un archivo `config.cfg` con este contenido:
```ini
[INPUT]
url = https://tuempresa.celonis.cloud
token = TU_API_TOKEN_AQUI
key_type = USER_KEY
data_pool_ids_to_extract_from = []
```

2. Ejecuta:
```bash
python celodocs_extractor.py
```

Los archivos se guardan en la carpeta `out_celodocs/`.

---

## 📧 Configurar envío de correo (opcional)

Para Gmail, necesitas una **App Password** (no tu contraseña normal):
1. Ve a https://myaccount.google.com/apppasswords
2. Crea una contraseña para "Correo"
3. Úsala en el campo "Contraseña / App Password" de la interfaz

---

## 📁 ¿Dónde están los archivos generados?
Todos los reportes se guardan en la carpeta `out_celodocs/`:
- `Requirements_Filled_YYYYMMDD_HHMMSS.xlsx` → Reporte principal en Excel
- `ocpm_requirements_snapshot_YYYYMMDD_HHMMSS.json` → Snapshot en JSON
- `sql_full/` → Carpeta con todos los SQLs generados
- `sql_full_TIMESTAMP.zip` → ZIP con los SQLs (si lo activaste)

---

## ❓ Problemas frecuentes

| Error | Solución |
|-------|----------|
| `pip: command not found` | Instala Python desde python.org |
| `ModuleNotFoundError` | Corre `pip install -r requirements.txt` de nuevo |
| `Authentication failed` | Verifica tu API Token en Celonis |
| `No encontré el template` | Asegúrate de que `Requirements Template (OCPM).xlsx` esté en la misma carpeta |
| Email no llega | Usa App Password de Gmail, no tu contraseña normal |

---

## 🆘 ¿Necesitas ayuda?
Contacta al equipo técnico con el mensaje de error completo que aparece en pantalla.
