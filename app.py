import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

def main():
    st.title("Cargar y Filtrar Archivo Excel")

    # Cargar archivo Excel
    uploaded_file = st.file_uploader("Cargar archivo Excel", type=["xlsx"])
    
    if uploaded_file is not None:
        try:
            data = pd.read_excel(uploaded_file)
            st.write("Data cargada correctamente")
            st.dataframe(data)
    
            # Verificar si existe la columna "Nombre Cliente"
            if "Nombre Cliente" in data.columns:
                # Crear opciones de filtrado para "Nombre Cliente"
                clientes = data["Nombre Cliente"].unique().tolist()
                opciones_clientes = ["Todos"] + sorted(clientes)
                filtro_cliente = st.selectbox("Filtrar por Nombre Cliente", opciones_clientes)
    
                # Filtrar la data según el cliente seleccionado
                data_filtrado = data.copy()
                if filtro_cliente != "Todos":
                    data_filtrado = data_filtrado[data_filtrado["Nombre Cliente"] == filtro_cliente]
    
                # Función para reemplazar valores nulos por "Sin datos"
                def preparar_valores(col):
                    valores = col.unique().tolist()
                    valores = ["Sin datos" if pd.isna(x) else x for x in valores]
                    return sorted(valores, key=lambda x: (x == "Sin datos", x))
    
                # Verificar si existe la columna "Apagado Orlando"
                if "Apagado Orlando" in data.columns:
                    opciones_apagado = ["Todos"] + preparar_valores(data_filtrado["Apagado Orlando"])
                    filtro_apagado = st.selectbox("Filtrar por Apagado Orlando", opciones_apagado)
    
                    # Filtrar la data según la opción seleccionada
                    if filtro_apagado != "Todos":
                        if filtro_apagado == "Sin datos":
                            data_filtrado = data_filtrado[data_filtrado["Apagado Orlando"].isna()]
                        else:
                            data_filtrado = data_filtrado[data_filtrado["Apagado Orlando"] == filtro_apagado]
    
                    # Mostrar la data filtrada
                    st.write("Data Filtrado")
                    st.dataframe(data_filtrado)
    
                    # Gráfico de barras para "Apagado Orlando"
                    st.write("Gráfico de barras")
                    plt.figure(figsize=(10, 4))
                    data_filtrado["Apagado Orlando"].value_counts().plot(kind="bar")
                    st.pyplot(plt)
                else:
                    st.error("No se encontró la columna 'Apagado Orlando'")
            else:
                st.error("No se encontró la columna 'Nombre Cliente'")
            
            st.info("Dashboard se actualiza cada 5 minutos")
        except Exception as e:
            st.error(f"Error al cargar el archivo: {e}")
    else:
        st.warning("Por favor, cargue un archivo Excel")

if __name__ == '__main__':
    main()
