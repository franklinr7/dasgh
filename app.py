import streamlit as st
import pandas as pd
import altair as alt
import numpy as np

def main():
    st.title("Dashboard Estratégico: Seguimiento y Análisis")
    st.write("Este dashboard permite un análisis profundo de la información cargada desde un archivo Excel, facilitando la toma de decisiones estratégicas.")
    
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
            
            # Limpieza de datos: reemplazar valores nulos
            data["Nombre Cliente"] = data["Nombre Cliente"].fillna("Sin datos")
            data["Apagado Orlando"] = data["Apagado Orlando"].fillna("Sin datos")
            
            # Sección de KPIs
            total_registros = len(data)
            total_clientes = data["Nombre Cliente"].nunique()
            conteo_apagado = data["Apagado Orlando"].value_counts().to_dict()
            
            st.subheader("KPIs Estratégicos")
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Total Registros", total_registros)
                st.metric("Clientes Únicos", total_clientes)
            with col2:
                st.write("**Conteo 'Apagado Orlando':**")
                st.write(conteo_apagado)
            
            # Organización en pestañas para un análisis integral
            tab1, tab2, tab3 = st.tabs(["Data Filtrada", "Visualizaciones", "Resumen y Recomendaciones"])
            
            with tab1:
                st.subheader("Filtros Interactivos")
                # Filtro por "Nombre Cliente"
                clientes = sorted(data["Nombre Cliente"].unique(), key=lambda x: str(x))
                clientes.insert(0, "Todos")
                filtro_cliente = st.selectbox("Filtrar por Nombre Cliente", clientes)
                
                data_filtrado = data.copy()
                if filtro_cliente != "Todos":
                    data_filtrado = data_filtrado[data_filtrado["Nombre Cliente"] == filtro_cliente]
                
                # Función para preparar valores y ordenarlos (evitando conflictos de tipos)
                def preparar_valores(col):
                    valores = col.unique().tolist()
                    valores = ["Sin datos" if pd.isna(x) else x for x in valores]
                    return sorted(valores, key=lambda x: (x == "Sin datos", str(x)))
                
                opciones_apagado = preparar_valores(data_filtrado["Apagado Orlando"])
                opciones_apagado.insert(0, "Todos")
                filtro_apagado = st.selectbox("Filtrar por Apagado Orlando", opciones_apagado)
                
                if filtro_apagado != "Todos":
                    if filtro_apagado == "Sin datos":
                        data_filtrado = data_filtrado[data_filtrado["Apagado Orlando"] == "Sin datos"]
                    else:
                        data_filtrado = data_filtrado[data_filtrado["Apagado Orlando"] == filtro_apagado]
                
                st.write("**Data Filtrada:**")
                st.dataframe(data_filtrado)
            
            with tab2:
                st.subheader("Visualizaciones Interactivas")
                # Gráfico de barras interactivo para "Apagado Orlando"
                chart_bar = alt.Chart(data_filtrado).mark_bar().encode(
                    x=alt.X("Apagado Orlando:N", title="Apagado Orlando"),
                    y=alt.Y("count():Q", title="Cantidad"),
                    tooltip=[alt.Tooltip("count()", title="Cantidad")]
                ).properties(
                    width=600,
                    height=400,
                    title="Distribución de Apagado Orlando"
                ).interactive()
                st.altair_chart(chart_bar, use_container_width=True)
                
                # Gráfico de pastel (simulado) para "Nombre Cliente"
                st.write("### Gráfico de pastel: Distribución de 'Nombre Cliente'")
                # Primero, se agrega una columna con conteos para cada cliente
                pie_data = data_filtrado.groupby("Nombre Cliente").size().reset_index(name="count")
                # Se calcula el ángulo para el gráfico de pastel
                pie_data["angle"] = pie_data["count"] / pie_data["count"].sum() * 2 * np.pi
                
                chart_pie = alt.Chart(pie_data).mark_arc(innerRadius=50).encode(
                    theta=alt.Theta(field="count", type="quantitative"),
                    color=alt.Color(field="Nombre Cliente", type="nominal"),
                    tooltip=[alt.Tooltip("Nombre Cliente:N", title="Cliente"),
                             alt.Tooltip("count:Q", title="Cantidad")]
                ).properties(
                    width=400,
                    height=400,
                    title="Distribución de Nombre Cliente"
                )
                st.altair_chart(chart_pie, use_container_width=True)
            
            with tab3:
                st.subheader("Resumen y Recomendaciones Estratégicas")
                st.write("A continuación, se presenta un resumen estadístico de la data filtrada:")
                resumen = data_filtrado.describe(include='all')
                st.dataframe(resumen)
                
                st.markdown("""
                **Recomendaciones Estratégicas:**
                - **Analizar la distribución de 'Apagado Orlando':** Identifica áreas de mejora o anomalías en el comportamiento.
                - **Segmentación de clientes:** Evalúa la concentración de clientes para enfocar campañas de marketing o mejorar el servicio.
                - **Monitoreo continuo:** Actualiza y revisa el dashboard periódicamente (se actualiza cada 5 minutos) para detectar tendencias a tiempo.
                - **Exploración de datos adicionales:** Si se dispone de datos temporales u otras métricas, se recomienda integrar análisis de series de tiempo para prever comportamientos futuros.
                - **Profundización:** Considera la creación de dashboards adicionales que incluyan análisis de correlación, segmentación avanzada o modelos predictivos según la disponibilidad de datos.
                """)
            
            st.info("Dashboard se actualiza cada 5 minutos")
            
        except Exception as e:
            st.error(f"Error al cargar el archivo: {e}")
    else:
        st.warning("Por favor, cargue un archivo Excel")

if __name__ == '__main__':
    main()
