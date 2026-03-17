# -*- coding: utf-8 -*-
"""
CeloDocs - Interfaz web para usuarios no técnicos
Ejecutar con: streamlit run app_streamlit.py
"""

import streamlit as st
import os
import subprocess
import sys
import datetime
from pathlib import Path
import glob

# ========================
# CONFIG DE PÁGINA
# ========================
st.set_page_config(
    page_title="CeloDocs Extractor",
    page_icon="📊",
    layout="centered",
)

st.title("📊 CeloDocs — Extractor OCPM")
st.caption("Genera reportes de Objects y Events desde Celonis, exporta a Excel/JSON y envía por correo.")

# ========================
# SECCIÓN 1: CONEXIÓN
# ========================
with st.expander("🔌 Conexión a Celonis", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        url = st.text_input("URL de Celonis", placeholder="https://tuempresa.celonis.cloud")
        key_type = st.selectbox("Tipo de API Key", ["USER_KEY", "APP_KEY"])
    with col2:
        token = st.text_input("API Token", type="password", placeholder="tu-token-aqui")
        environment = st.selectbox("Ambiente", ["develop", "staging", "production"])

    data_pool_input = st.text_input(
        "Data Pool IDs (separados por coma, opcional)",
        placeholder="id1, id2  — dejar vacío para usar el primero disponible"
    )
    
with st.expander("🔄 Comparación (Diff)", expanded=True):
    st.info("Sube el Excel generado anteriormente para obtener el resumen de cambios.")
    prev_file = st.file_uploader("Reporte anterior (.xlsx)", type=["xlsx"])
# ========================
# SECCIÓN 2: NAMESPACES
# ========================
with st.expander("📂 Namespaces a extraer", expanded=False):
    ns_default = ["custom", "catalog", "standard", "sap", "celonis"]
    namespaces = st.multiselect(
        "Selecciona namespaces",
        options=["custom", "catalog", "standard", "sap", "celonis"],
        default=ns_default,
    )

# ========================
# SECCIÓN 3: EMAIL
# ========================
with st.expander("📧 Envío de correo (opcional)", expanded=False):
    st.info("Si no completas estos campos, el reporte se generará igualmente y podrás descargarlo aquí.")
    email_to  = st.text_input("Para (separar por coma)",  placeholder="analista@empresa.com")
    email_cc  = st.text_input("CC (opcional)",             placeholder="jefe@empresa.com")
    email_bcc = st.text_input("BCC (opcional)")

    col3, col4 = st.columns(2)
    with col3:
        email_user = st.text_input("Tu correo Gmail / SMTP",  placeholder="tuusuario@gmail.com")
        smtp_server = st.text_input("Servidor SMTP", value="smtp.gmail.com")
    with col4:
        email_pass = st.text_input("Contraseña / App Password", type="password")
        smtp_port  = st.number_input("Puerto SMTP", value=587, step=1)

    attach_zip = st.checkbox("Adjuntar ZIP con todos los archivos SQL")

# ========================
# BOTÓN DE EJECUCIÓN
# ========================
st.divider()
run = st.button("🚀 Ejecutar extracción", type="primary", use_container_width=True)

if run:
    if prev_file is not None:
        prev_temp_path = "prev_report_temp.xlsx"
        with open(prev_temp_path, "wb") as f:
            f.write(prev_file.getbuffer())
        env_vars["CELODOCS_PREV_FILE"] = prev_temp_path
    # Validación mínima
    if not url or not token:
        st.error("❌ Debes ingresar la URL y el API Token de Celonis.")
        st.stop()

    if not namespaces:
        st.error("❌ Selecciona al menos un namespace.")
        st.stop()

    # Preparar data_pool_ids
    dp_ids = []
    if data_pool_input.strip():
        dp_ids = [x.strip() for x in data_pool_input.split(",") if x.strip()]

    # Armar config.cfg temporal
    cfg_content = f"""[INPUT]
url = {url}
token = {token}
key_type = {key_type}
data_pool_ids_to_extract_from = {dp_ids}
"""
    with open("config.cfg", "w") as f:
        f.write(cfg_content)

    # Variables de entorno
    env_vars = os.environ.copy()
    env_vars["CELODOCS_ENVIRONMENT"]   = environment
    env_vars["CELODOCS_NAMESPACES"]    = ",".join(namespaces)
    env_vars["CELODOCS_ATTACH_SQL_ZIP"] = "1" if attach_zip else "0"

    if email_to:        env_vars["CELODOCS_EMAIL_TO"]  = email_to
    if email_cc:        env_vars["CELODOCS_EMAIL_CC"]  = email_cc
    if email_bcc:       env_vars["CELODOCS_EMAIL_BCC"] = email_bcc
    if email_user:      env_vars["EMAIL_USER"]          = email_user
    if email_pass:      env_vars["EMAIL_PASS"]          = email_pass
    if smtp_server:     env_vars["SMTP_SERVER"]         = smtp_server
    env_vars["SMTP_PORT"] = str(int(smtp_port))

    # Ejecutar script principal
    with st.spinner("⏳ Extrayendo datos de Celonis... (puede tardar varios minutos)"):
        result = subprocess.run(
            [sys.executable, "celodocs_extractor.py"],
            capture_output=True,
            text=True,
            env=env_vars,
        )

    if result.returncode == 0:
        st.success("✅ ¡Extracción completada con éxito!")
        st.code(result.stdout, language="text")

        # Mostrar archivos generados para descarga
        out_dir = Path("out_celodocs")
        tag_pattern = datetime.datetime.now().strftime("%Y%m%d")

        xlsx_files = sorted(out_dir.glob(f"Requirements_Filled_*.xlsx"), reverse=True)
        json_files = sorted(out_dir.glob(f"ocpm_requirements_snapshot_*.json"), reverse=True)
        zip_files  = sorted(out_dir.glob(f"sql_full_*.zip"), reverse=True)

        st.subheader("📥 Descargar archivos generados")

        if xlsx_files:
            with open(xlsx_files[0], "rb") as f:
                st.download_button(
                    label=f"⬇️ Descargar Excel: {xlsx_files[0].name}",
                    data=f,
                    file_name=xlsx_files[0].name,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True,
                )

        if json_files:
            with open(json_files[0], "rb") as f:
                st.download_button(
                    label=f"⬇️ Descargar JSON: {json_files[0].name}",
                    data=f,
                    file_name=json_files[0].name,
                    mime="application/json",
                    use_container_width=True,
                )

        if zip_files:
            with open(zip_files[0], "rb") as f:
                st.download_button(
                    label=f"⬇️ Descargar ZIP SQL: {zip_files[0].name}",
                    data=f,
                    file_name=zip_files[0].name,
                    mime="application/zip",
                    use_container_width=True,
                )
    else:
        st.error("❌ El script terminó con errores.")
        st.subheader("Detalle del error:")
        st.code(result.stderr or result.stdout, language="text")
        st.info("💡 Tip: Verifica que el URL, token y Data Pool ID sean correctos.")
