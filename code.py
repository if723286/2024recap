import streamlit as st
import pandas as pd
import plotly.express as px

# Función para cargar el archivo Excel
def cargar_datos(uploaded_file):
    return pd.read_excel(uploaded_file, sheet_name=None)

# Función para calcular las estadísticas
def calcular_estadisticas(df):
    df['Utilidad'] = df['Ingreso'] - df['Egreso']
    df['Margen'] = (df['Utilidad'] / df['Ingreso'])
    df['Ingreso por viaje'] = df['Ingreso'] / df['Viajes']
    df['Egreso por viaje'] = df['Egreso'] / df['Viajes']
    df['Utilidad por viaje'] = df['Utilidad'] / df['Viajes']
    return df

# Subir archivo Excel
uploaded_file = st.file_uploader("Sube tu archivo Excel", type=["xlsx"])

if uploaded_file is not None:
    # Cargar los datos del archivo
    datos = cargar_datos(uploaded_file)
    
    # Selección de los meses a incluir en el análisis
    meses = list(datos.keys())
    meses_seleccionados = st.multiselect("Selecciona los meses", meses, default=meses[:1])
    
    # Combinar datos de los meses seleccionados
    df_completo = pd.concat([datos[mes] for mes in meses_seleccionados], ignore_index=True)


    # Opciones para filtrar por Cliente o Ruta
    filtro_tipo = st.radio("Filtrar por", ["Cliente", "Ruta"])
    
    if filtro_tipo == "Cliente":
        df_agrupado = df_completo.groupby('Cliente').sum().reset_index()
    else:
        df_agrupado = df_completo.groupby(['Ruta', 'Cliente']).sum().reset_index()
    
    # Calcular las estadísticas
    df_agrupado = calcular_estadisticas(df_agrupado)
    
    # Selección de columnas a mostrar
    columnas_disponibles = ['Ingreso', 'Egreso', 'Utilidad', 'Margen', 'Viajes', 'Ingreso por viaje', 'Egreso por viaje', 'Utilidad por viaje']
    columnas_seleccionadas = st.multiselect("Selecciona las columnas a mostrar", columnas_disponibles, default=columnas_disponibles[:3])
    
    # Opción para ordenar la tabla
    columna_orden = st.selectbox("Selecciona la columna para ordenar", columnas_seleccionadas)
    orden_ascendente = st.checkbox("Orden ascendente", value=False)
    df_agrupado = df_agrupado.sort_values(by=columna_orden, ascending=orden_ascendente)

    
    # Mostrar las estadísticas filtradas
    st.write(f"Estadísticas para los meses seleccionados, agrupado por {filtro_tipo}")
    st.dataframe(df_agrupado[['Cliente'] + columnas_seleccionadas] if filtro_tipo == "Cliente" else df_agrupado[['Ruta', 'Cliente'] + columnas_seleccionadas])
    
    # Selección del parámetro para la gráfica
    parametro_seleccionado = st.selectbox('Selecciona el parámetro para la gráfica', columnas_disponibles)
    
    # Ordenar y mostrar el top 10
    df_top10 = df_agrupado.nlargest(10, parametro_seleccionado)
    
    # Crear la gráfica mejorada con Plotly
    fig = px.bar(df_top10, x=parametro_seleccionado, y=filtro_tipo, title=f'Top 10 {filtro_tipo} por {parametro_seleccionado}',
                 labels={parametro_seleccionado: parametro_seleccionado, filtro_tipo: filtro_tipo}, height=600)
    fig.update_layout(xaxis_title=parametro_seleccionado, yaxis_title=filtro_tipo)
    st.plotly_chart(fig)
