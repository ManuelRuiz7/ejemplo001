import streamlit as st
import geopandas as gpd
import folium
from shapely.geometry import Polygon
from streamlit_folium import st_folium
import pandas as pd

# Inicializar sesión
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# Formulario de login
if not st.session_state.logged_in:
    st.title("Ingreso")
    user = st.text_input("Usuario")
    password = st.text_input("Contraseña", type="password")
    login_button = st.button("Entrar")

    if login_button:
        if user == "admin" and password == "1234":  # Cambiar a tus credenciales reales
            st.session_state.logged_in = True
            st.success("Bienvenido")
        else:
            st.error("Usuario o contraseña incorrectos")
else:
    st.title("Mapa con Alcaldes")

    # Polyfill arriba del todo
    st.markdown("""
    <script>
    if (!String.prototype.replaceAll) {
      String.prototype.replaceAll = function(search, replace) {
        return this.split(search).join(replace);
      };
    }
    </script>
    """, unsafe_allow_html=True)

    # Cargar municipios
    gdf = gpd.read_file("municipios.geojson")
    gdf = gdf[gdf['name'].notna()]

    # Cargar Alcaldes
    df_alcaldes = pd.read_csv("alcaldes.txt")

    # Unir data por nombre de municipio
    gdf = gdf.merge(df_alcaldes, left_on='name', right_on='municipio', how='left')

    # Polígono del estado
    estado_tam = gdf.unary_union

    # Crear mapa sin tiles base
    m = folium.Map(
        location=[gdf.geometry.centroid.y.mean(), gdf.geometry.centroid.x.mean()],
        zoom_start=7,
        tiles=None
    )

    # Tile blanco de fondo
    folium.TileLayer(
        tiles='https://tiles.wmflabs.org/bw-mapnik/{z}/{x}/{y}.png',
        attr='© Universidad Autónoma de Tamaulipas',
        name='Blank',
        control=False,
        overlay=False
    ).add_to(m)

    # Agregar polígonos municipios con tooltips personalizados
    for _, row in gdf.iterrows():
        tooltip_text = f"<b>Municipio:</b> {row['name']}<br><b>Alcalde:</b> {row['alcalde']}"
        folium.GeoJson(
            data=row['geometry'],
            name=row['name'],
            style_function=lambda feature: {
                'fillColor': '#cccccc',
                'color': 'black',
                'weight': 0.5,
                'fillOpacity': 0.7,
            },
            tooltip=folium.Tooltip(tooltip_text, sticky=True)
        ).add_to(m)

    # Máscara blanca fuera del estado
    big_polygon = Polygon([[-120, 40], [-120, 10], [-80, 10], [-80, 40], [-120, 40]])
    mask_polygon = Polygon(big_polygon.exterior.coords, [estado_tam.exterior.coords])

    folium.GeoJson(
        data=mask_polygon,
        style_function=lambda feature: {
            'fillColor': 'white',
            'color': 'white',
            'fillOpacity': 1,
            'weight': 0,
        }
    ).add_to(m)

    # Mostrar mapa
    st_folium(m, width=700, height=500)

    # Botón para cerrar sesión
    if st.button("Cerrar sesión"):
        st.session_state.logged_in = False
