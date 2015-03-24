# -*- coding: utf-8 -*-

import pydygraph as pydy
import pandas as pd
from datetime import datetime

# Procesando Pandas
produccion = pd.read_csv("potencias.csv", sep=",", index_col=[
                         "Fecha"], parse_dates=True, dtype={'Fecha': datetime})
produccion_tanto = (produccion / produccion.max()) * produccion.max().max()

var_exp_demanda = pd.read_csv("variables_explicativas_demanda_mini.csv", sep=",", index_col=[
                              "Fecha"], parse_dates=True, dtype={'Fecha': datetime})


# Generando HTML
html = pydy.DygraphChart()

# Opciones

opciones_grafico_01 = {'ylabel': "'Potencia (MW)'",
                       'showRangeSelector': 'true',
                       'valueRange': '[0,6000]', }

opciones_grafico_02 = {'showRangeSelector': 'true'}

atributos_h200 = {'width': '100%', 'height': '200px'}

html.addCSS(identificador='css_titulo',
            atributos="font-weight:bold;text-align: center; font-variant:small-caps;font-size:medium;")

html.addHtml(
    "<p class='css_titulo'>Pequena demostracion de como funciona la clase</p>")
html.addHtml('<hr align="LEFT" size="2" width="100%" color="Black" noshade>')

html.addSerie("<p class='texto_centrado_negrita'>Potencias sin redimensionar</p>",
              opciones=opciones_grafico_01,
              atributos={'width': '100%', 'height': '600px'},
              dataframe=produccion)

html.addHtml('<hr align="LEFT" size="2" width="100%" color="Black" noshade>')

html.addSerie("<p class='texto_centrado_negrita'>Potencias Repotenciadas</p>",
              dataframe=produccion_tanto)

html.addHtml('<hr align="LEFT" size="2" width="100%" color="Black" noshade>')

html.addSerie("<p class='texto_centrado_negrita'>Grupo 1, Temperaturas</p>",
              atributos=atributos_h200,
              dataframe=var_exp_demanda[['DewPnt', 'DryBulb']],
              sincronizar='grupo1')


html.addSerie("<p class='texto_centrado_negrita'>Grupo 1, DA_DEMD</p>",
              dataframe=var_exp_demanda[['DA_DEMD']],
              sincronizar='grupo1')


html.addHtml('<hr align="LEFT" size="2" width="100%" color="Black" noshade>')

html.addSerie("<p class='texto_centrado_negrita'>Grupo 2, Precios</p>",
              atributos=atributos_h200,
              dataframe=var_exp_demanda[['RT_EC', 'RT_LMP', 'RT_CC']],
              sincronizar='grupo2')

html.addSerie("<p class='texto_centrado_negrita'>Grupo 2, DA_DEMD</p>",
              dataframe=var_exp_demanda[['DA_DEMD']],
              opciones={'showRangeSelector': 'false', 'showRoller': 'true'},
              sincronizar='grupo2')
              
              
# Mas tipos de opciones
"""
opciones_grafico_02 = {'ylabel': "'Potencia (KW)'","colors": '["#303030", "#0099ff", "#ee2c2c", "#aa2c2c"]','observacion': "{ strokeWidth: 2,highlightCircleSize: 2}",
                       'valueRange': '[0,' + str(df_total.max().max() * 1.1) + ']',
                       }
"""

# Guardado del HTML generado
html.plotHTML('curvas_produccion_dy02') # Se guarda el fichero
html.plotHTML() # Fichero Temporal

