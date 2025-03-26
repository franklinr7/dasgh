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
            
            # Limpieza básica de datos
            data["Nombre Cliente"] = data["Nombre Cliente"].fillna("Sin datos")
            data["Apagado Orlando"] = data["Apagado Orlando"].fillna("Sin datos")

            # Si existe la columna WebHosting, limpiarla también
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
                
                # 1) Escala de color dinámica para "Apagado Orlando"
                #    Definimos colores conocidos y un color por defecto (ej. azul) para valores nuevos.
                status_colors = {
                    "Activo": "green",
                    "Desactivado": "red",
                    "Sin datos": "gray"
                }
                
                unique_values_apagado = sorted(list(data_filtrado["Apagado Orlando"].unique()))
                
                domain_apagado = []
                range_apagado = []
                
                for val in unique_values_apagado:
                    if val in status_colors:
                        domain_apagado.append(val)
                        range_apagado.append(status_colors[val])
                    else:
                        # Para valores no contemplados, asignar un color por defecto (ej. azul)
                        domain_apagado.append(val)
                        range_apagado.append("blue")
                
                color_scale_apagado = alt.Scale(domain=domain_apagado, range=range_apagado)
                
                # Gráfico de barras para Apagado Orlando
                chart_bar = alt.Chart(data_filtrado).mark_bar().encode(
                    x=alt.X("Apagado Orlando:N", title="Apagado Orlando"),
                    y=alt.Y("count():Q", title="Cantidad"),
                    color=alt.Color("Apagado Orlando:N", scale=color_scale_apagado),
                    tooltip=[alt.Tooltip("count()", title="Cantidad")]
                ).properties(
                    width=600,
                    height=400,
                    title="Distribución de 'Apagado Orlando' (Barras)"
                ).interactive()
                st.altair_chart(chart_bar, use_container_width=True)
                
                # Gráfico de pastel para Apagado Orlando
                pie_data = data_filtrado.groupby("Apagado Orlando").size().reset_index(name="count")
                chart_pie = alt.Chart(pie_data).mark_arc(innerRadius=50).encode(
                    theta=alt.Theta(field="count", type="quantitative"),
                    color=alt.Color("Apagado Orlando:N", scale=color_scale_apagado),
                    tooltip=[alt.Tooltip("Apagado Orlando:N", title="Estatus"),
                             alt.Tooltip("count:Q", title="Cantidad")]
                ).properties(
                    width=400,
                    height=400,
                    title="Distribución de 'Apagado Orlando' (Pastel)"
                )
                st.altair_chart(chart_pie, use_container_width=True)
                
                # 2) Si existe la columna WebHosting, visualización dinámica también
                if "WebHosting" in data_filtrado.columns:
                    st.write("### Distribución de WebHosting (Barras)")
                    
                    # Colores para WebHosting
                    web_colors = {
                        "Activo": "blue",
                        "Inactivo": "orange",
                        "Sin datos": "gray"
                    }
                    
                    unique_values_web = sorted(list(data_filtrado["WebHosting"].unique()))
                    domain_web = []
                    range_web = []
                    
                    for val in unique_values_web:
                        if val in web_colors:
                            domain_web.append(val)
                            range_web.append(web_colors[val])
                        else:
                            domain_web.append(val)
                            range_web.append("pink")  # color por defecto si aparece algo nuevo
                            
                    color_scale_web = alt.Scale(domain=domain_web, range=range_web)
                    
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
                if not data_filtrado.empty:
                    resumen = data_filtrado.describe(include='all')
                    st.dataframe(resumen)
                else:
                    st.write("No hay datos para mostrar en el resumen estadístico.")
                
                st.markdown("""
                **Recomendaciones Estratégicas:**
                - **Verificar estados críticos:** Observa si existen muchos registros con 'Desactivado' o nuevos estados no contemplados (aparecerán en azul/rosado).
                - **Monitorear WebHosting:** Correlaciona el estado de WebHosting con la actividad de los clientes para identificar cuellos de botella.
                - **Segmentación de clientes:** Usa "Nombre Cliente" para estrategias de marketing y soporte específicas.
                """)
            
            st.info("Dashboard cargado correctamente")
            
        except Exception as e:
            st.error(f"Error al cargar el archivo: {e}")
    else:
        st.warning("Por favor, cargue un archivo Excel")

if __name__ == '__main__':
    main()


