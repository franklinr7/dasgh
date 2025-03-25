import streamlit as st
import pandas as pd
import altair as alt
import numpy as np

def main():
    st.title("Dashboard Estratégico: Seguimiento de WebHosting y Estatus de Clientes")
    st.write(
        "Este dashboard permite monitorear el estado de WebHosting y el estatus de los clientes, "
        "ofreciendo análisis interactivo, KPIs y recomendaciones estratégicas para un seguimiento en tiempo real."
    )
    
    # Cargar archivo Excel
    uploaded_file = st.file_uploader("Cargar archivo Excel", type=["xlsx"])
    
    if uploaded_file is not None:
        try:
            data = pd.read_excel(uploaded_file)
            st.write("Data cargada correctamente")
            st.dataframe(data)
            
            # Verificar columnas requeridas
            required_columns = ["Nombre Cliente", "Apagado Orlando"]
            missing_cols = [col for col in required_columns if col not in data.columns]
            if missing_cols:
                st.error(f"Faltan las siguientes columnas: {', '.join(missing_cols)}")
                return
            
            # Limpieza y validación de datos
            data["Nombre Cliente"] = data["Nombre Cliente"].fillna("Sin datos")
            data["Apagado Orlando"] = data["Apagado Orlando"].fillna("Sin datos")
            
            # Validación de valores en 'Apagado Orlando'
            # Convertimos a minúsculas para comparar sin problemas
            valores_apagado = data["Apagado Orlando"].str.lower().unique()
            if "desactivado" in valores_apagado:
                st.warning("Se detectaron registros con 'desactivado' en 'Apagado Orlando'. Verificar seguimiento y estado.")
            
            # Si existe la columna WebHosting, limpiarla
            if "WebHosting" in data.columns:
                data["WebHosting"] = data["WebHosting"].fillna("Sin datos")
            
            # Sección de KPIs
            total_registros = len(data)
            total_clientes = data["Nombre Cliente"].nunique()
            conteo_apagado = data["Apagado Orlando"].value_counts().to_dict()
            
            st.subheader("KPIs Estratégicos")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Registros", total_registros)
            with col2:
                st.metric("Clientes Únicos", total_clientes)
            with col3:
                st.write("**Estatus 'Apagado Orlando':**")
                st.write(conteo_apagado)
            
            # Organización en pestañas
            tab1, tab2, tab3 = st.tabs(["Data Filtrada", "Visualizaciones", "Resumen y Recomendaciones"])
            
            # TAB 1: Data Filtrada
            with tab1:
                st.subheader("Filtros Interactivos")
                # Filtro por "Nombre Cliente"
                clientes = sorted(data["Nombre Cliente"].unique(), key=lambda x: str(x))
                clientes.insert(0, "Todos")
                filtro_cliente = st.selectbox("Filtrar por Nombre Cliente", clientes)
                
                data_filtrado = data.copy()
                if filtro_cliente != "Todos":
                    data_filtrado = data_filtrado[data_filtrado["Nombre Cliente"] == filtro_cliente]
                
                # Filtro por "Apagado Orlando"
                def preparar_valores(col):
                    valores = col.unique().tolist()
                    valores = ["Sin datos" if pd.isna(x) else x for x in valores]
                    return sorted(valores, key=lambda x: (x == "Sin datos", str(x)))
                
                opciones_apagado = preparar_valores(data_filtrado["Apagado Orlando"])
                opciones_apagado.insert(0, "Todos")
                filtro_apagado = st.selectbox("Filtrar por Apagado Orlando", opciones_apagado)
                
                if filtro_apagado != "Todos":
                    data_filtrado = data_filtrado[data_filtrado["Apagado Orlando"] == filtro_apagado]
                
                st.write("**Data Filtrada:**")
                st.dataframe(data_filtrado)
            
            # TAB 2: Visualizaciones
            with tab2:
                st.subheader("Visualizaciones Interactivas")
                # Definir escala de colores personalizada para Apagado Orlando
                color_scale = alt.Scale(
                    domain=["Activo", "Desactivado", "Sin datos"],
                    range=["green", "red", "gray"]
                )
                
                # Gráfico de barras para Apagado Orlando
                chart_bar = alt.Chart(data_filtrado).mark_bar().encode(
                    x=alt.X("Apagado Orlando:N", title="Apagado Orlando"),
                    y=alt.Y("count():Q", title="Cantidad"),
                    color=alt.Color("Apagado Orlando:N", scale=color_scale),
                    tooltip=[alt.Tooltip("count()", title="Cantidad")]
                ).properties(
                    width=600,
                    height=400,
                    title="Distribución de 'Apagado Orlando' (Barras)"
                ).interactive()
                st.altair_chart(chart_bar, use_container_width=True)
                
                # Gráfico de pastel para Apagado Orlando
                pie_data = data_filtrado.groupby("Apagado Orlando").size().reset_index(name="count")
                pie_data["angle"] = pie_data["count"] / pie_data["count"].sum() * 2 * np.pi
                chart_pie = alt.Chart(pie_data).mark_arc(innerRadius=50).encode(
                    theta=alt.Theta(field="count", type="quantitative"),
                    color=alt.Color(field="Apagado Orlando", type="nominal", scale=color_scale),
                    tooltip=[alt.Tooltip("Apagado Orlando:N", title="Estatus"),
                             alt.Tooltip("count:Q", title="Cantidad")]
                ).properties(
                    width=400,
                    height=400,
                    title="Distribución de 'Apagado Orlando' (Pastel)"
                )
                st.altair_chart(chart_pie, use_container_width=True)
                
                # Visualización para WebHosting (si existe)
                if "WebHosting" in data_filtrado.columns:
                    st.write("### Distribución de WebHosting")
                    color_scale_web = alt.Scale(
                        domain=["Activo", "Inactivo", "Sin datos"],
                        range=["blue", "orange", "gray"]
                    )
                    chart_web = alt.Chart(data_filtrado).mark_bar().encode(
                        x=alt.X("WebHosting:N", title="WebHosting"),
                        y=alt.Y("count():Q", title="Cantidad"),
                        color=alt.Color("WebHosting:N", scale=color_scale_web),
                        tooltip=[alt.Tooltip("count()", title="Cantidad")]
                    ).properties(
                        width=600,
                        height=400,
                        title="Distribución de WebHosting"
                    ).interactive()
                    st.altair_chart(chart_web, use_container_width=True)
            
            # TAB 3: Resumen y Recomendaciones
            with tab3:
                st.subheader("Resumen y Recomendaciones Estratégicas")
                st.write("**Resumen Estadístico de la Data Filtrada:**")
                resumen = data_filtrado.describe(include='all')
                st.dataframe(resumen)
                
                st.markdown("""
                **Recomendaciones Estratégicas:**
                - **Verificar estados críticos:** Se ha detectado una incidencia de registros con 'desactivado' en 'Apagado Orlando'. Es crucial revisar estos casos para asegurar el correcto funcionamiento del servicio.
                - **Monitorear WebHosting:** Correlacionar el estado de WebHosting con la actividad de los clientes puede ayudar a identificar cuellos de botella o necesidades de actualización.
                - **Segmentación de clientes:** Utilizar la información de 'Nombre Cliente' para personalizar estrategias de marketing y soporte.
                - **Profundizar en análisis:** Considerar la integración de datos históricos y métricas adicionales (tiempos de respuesta, incidencias, etc.) para prever tendencias y optimizar recursos.
                - **Revisión periódica:** Actualiza y revisa este dashboard cada 5 minutos para detectar cambios en tiempo real y tomar decisiones informadas.
                """)
            
            st.info("Dashboard se actualiza cada 5 minutos")
            
        except Exception as e:
            st.error(f"Error al cargar el archivo: {e}")
    else:
        st.warning("Por favor, cargue un archivo Excel")

if __name__ == '__main__':
    main()

