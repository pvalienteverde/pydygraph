#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Ayuda sobre los metodos se los objetos DyGraph: http://dygraphs.com/jsdoc/symbols/Dygraph.html
"""


# https://docs.python.org/2/library/stdtypes.html#string-formatting
from string import Template
import pandas as pd
import json
from templates_html import templates_html
from templates_html import axesXHTML
import re
import webbrowser
import numpy as np
import tempfile
import time


class DygraphChart(templates_html):

    def __init__(self, **kwargs):
        """
        Constructor
        """
        self.__numero_chart__ = 0
        self.__contenedor__ = ''
        self.__charts_sincronizados__ = {}
        self.__charts_no_sincronizados__ = []
        self.__datos_charts__ = {}
        self.__opciones_charts__ = {}
        self.__visibilidad__ = {}
        # Ayuda: http://www.w3schools.com/css/default.asp
        self.__estilos_css_a_inclustar__ = []
        self.__atributos_charts__ = {}
        self.__funciones_charts__ = {}

        self.__atributos_charts_default__ = {'width': '100%',
                                             'height': '400px'}

        self.__opciones_charts_default__ = {'showRangeSelector': 'true',
                                            'legend': "'always'", }

    def addSerie(self, *args, **kwargs):
        """
        Se añade la serie a plotear
        """
        self.__numero_chart__ += 1
        kwargs['idc'] = "div%03d" % (self.__numero_chart__)

        self.addChart(**kwargs)
        self.addCuerpo(*args, **kwargs)

    def addHtml(self, *args):
        """
        Se añade la serie a plotear
        """
        self.addCuerpo(*args)

    def addChart(self, **kwargs):
        '''
        Constructor de cada uno del jschart
        '''

        # Introducimos valores por defecto

        opciones_usuario = self.__opciones_charts_default__.copy()
        if 'opciones' in kwargs:
            opciones_usuario = dict(
                opciones_usuario.items() | kwargs['opciones'].copy().items())

        atributos_usuarios = self.__atributos_charts_default__.copy()
        if 'atributos' in kwargs:
            atributos_usuarios = dict(
                atributos_usuarios.items() | kwargs['atributos'].copy().items())

        if 'nombre_fichero' in kwargs and 'dataframe' in kwargs:
            raise AssertionError(
                "No se puede utilizar el argumento nombre_fichero y dataframe a la vez")

        if 'nombre_fichero' in kwargs:
            kwargs['tipo_datos'] = '"' + kwargs['nombre_fichero'] + '"'
        elif 'dataframe' in kwargs:
            kwargs['tipo_datos'] = self.pd2str(kwargs['dataframe'], index_timestamp=(
                type(kwargs['dataframe'].index[0]) is pd.tslib.Timestamp))
            opciones_usuario[
                'labels'] = '["Indice","' + '","'.join(kwargs['dataframe'].columns.values) + '"]'
        else:
            raise AssertionError("Se necesita alguna fuente de datos")

        # Creamos los grupos de sincronizacion o no
        if 'sincronizar' in kwargs:
            # GUardamos en cada grupo de sincronizacion
            if kwargs['sincronizar'] in self.__charts_sincronizados__:
                self.__charts_sincronizados__[
                    kwargs['sincronizar']].append(kwargs['idc'])
            else:
                self.__charts_sincronizados__[
                    kwargs['sincronizar']] = [kwargs['idc']]
        else:
            self.__charts_no_sincronizados__.append(kwargs['idc'])

        # Guardamos los datos
        self.__datos_charts__[kwargs['idc']] = kwargs['tipo_datos']
        self.__opciones_charts__[kwargs['idc']] = opciones_usuario
        self.__atributos_charts__[kwargs['idc']] = atributos_usuarios
        self.__funciones_charts__[kwargs['idc']] = str.join("\n", kwargs.get(
            'fun_java_script', ['']))  # Se añade funciones que se tienen que incrustar
        # Generamos la opcion de chequear la visibilidad, por ahora solamente
        # para asincronos
        self.__visibilidad__[kwargs['idc']] = kwargs.get(
            'anadir_opc_visibilidad', True)

    def buildJs(self):
        '''
        COntructor del recubrimiento del js        
        '''
        more_opciones = ''
        # more_opciones+="""
        #        ,highlightSeriesOpts: {
        #		  strokeWidth: 3,
        #		  strokeBorderWidth: 1,
        #		  highlightCircleSize: 5,
        #		}
        #         """

        cuerpo_js = Template(self.__template_js__)

        # Primeros generamos los que no estan sincronizados con ninguno
        cuerpo_charts_asin = Template(self.__template_chart_asincrono__)
        js_asincrono = ''
        js_opc_visibilidad = ''
        js_funciones_java_script = ''
        for id_manejador in self.__charts_no_sincronizados__:
            id_interno_charts = "asin_" + id_manejador
            js_asincrono += cuerpo_charts_asin.substitute(id_interno=id_interno_charts,
                                                          idc=id_manejador,
                                                          tipo_datos=self.__datos_charts__[
                                                              id_manejador],
                                                          opciones=self.dictOpciones2str(self.__opciones_charts__[id_manejador]) + more_opciones)

            if self.__visibilidad__[id_manejador]:
                cuerpo_opc_visibilidad = Template(
                    self.__template_opc_visibilidad__)
                js_opc_visibilidad += cuerpo_opc_visibilidad.substitute(id_interno_asin=id_interno_charts,
                                                                        id_interno=id_manejador)

            js_funciones_java_script += self.__funciones_charts__[id_manejador]
        script_asincrono = cuerpo_js.substitute(
            charts=js_asincrono + js_opc_visibilidad, funciones_script=js_funciones_java_script)

        # AHora los que están sincronizados, se generarán por grupos
        cuerpo_charts_sin_push = Template(self.__template_push_sincrono__)
        script_sincrono = ''
        js_funciones_java_script = ''
        for id_grupo_manejador in self.__charts_sincronizados__:
            js_sincrono = id_grupo_manejador + ''' = [];
            var blockRedraw = false;
            var initialized = false;
            '''

            for id_manejador in self.__charts_sincronizados__[id_grupo_manejador]:
                id_interno_charts = "sin_" + id_manejador
                cuerpo_grupo_sincro = Template(self.__more_opciones_sincrono__)
                more_opciones_sincro = cuerpo_grupo_sincro.substitute(num_elementos_interactivos=len(self.__charts_sincronizados__[id_grupo_manejador]),
                                                                      id_grupo=id_grupo_manejador)
                js_sincrono += cuerpo_charts_asin.substitute(id_interno=id_interno_charts,
                                                             idc=id_manejador,
                                                             tipo_datos=self.__datos_charts__[
                                                                 id_manejador],
                                                             opciones=self.dictOpciones2str(self.__opciones_charts__[id_manejador]) + more_opciones_sincro + more_opciones)

                if self.__visibilidad__[id_manejador]:
                    cuerpo_opc_visibilidad = Template(
                        self.__template_opc_visibilidad__)
                    js_opc_visibilidad += cuerpo_opc_visibilidad.substitute(id_interno_asin=id_interno_charts,
                                                                            id_interno=id_manejador)
                js_sincrono += cuerpo_charts_sin_push.substitute(id_interno=id_interno_charts,
                                                                 id_grupo=id_grupo_manejador)

                js_funciones_java_script += self.__funciones_charts__[
                    id_manejador]
           # Lo relleno
            script_sincrono_charts = js_sincrono + js_opc_visibilidad
            script_sincrono += cuerpo_js.substitute(
                charts=script_sincrono_charts + script_sincrono_charts, funciones_script=js_funciones_java_script)

        return script_asincrono + script_sincrono

# Sobre los **kwargs:
# http://www.juanjoconti.com.ar/2010/10/13/entendiendo-args-y-kwargs-en-python/
    def addCuerpo(self, *args, **kwargs):
        """
        Tanto para incorporar contenido interno como externo, debe ser lineal
        """
        titulo = ""
        if len(args) != 0:
            for elemento in args:
                titulo += str(elemento) + "\n"

        anadir_chart = ""
        if len(kwargs) != 0:
            cuerpo_contenedor = Template(self.__template_cuerpo_interno__)
            anadir_chart += cuerpo_contenedor.substitute(idc=kwargs['idc'],
                                                         atributos=self.dictAtributos2str(self.__atributos_charts__[kwargs['idc']]))

            if self.__visibilidad__[kwargs['idc']]:
                cuerpo_label_visibilidad = Template(
                    self.__template_label_visibilidad__)
                anadir_chart += '<p class="texto_centrado"><b>Series :</b>'
                for id_num_curva, id_str_curva in enumerate(kwargs['dataframe'].columns.values):
                    anadir_chart += cuerpo_label_visibilidad.substitute(id_num_curva=id_num_curva,
                                                                        descriptor_curva=id_str_curva,
                                                                        id_interno=kwargs['idc'])
                anadir_chart += '</p>'

        self.__contenedor__ += titulo + anadir_chart

    def buildCSS(self):
        estilos_css = ''
        for css in self.__estilos_css_a_inclustar__:
            estilos_css += css
        return estilos_css

    def addCSS(self, identificador, atributos):
        if identificador is None or atributos is None:
            raise AssertionError(
                "Falta ipor declarar idenrificaodr o los atributos")

        self.__estilos_css_a_inclustar__.append(
            "." + identificador + '{' + atributos + "}\n")

    def buildHTML(self):
        """
        Creacion del HTML
        """
        cuerpo_html = Template(self.__template_html__)
        return cuerpo_html.substitute(css=self.buildCSS(), contenedor=self.__contenedor__, js=self.buildJs())
        
    @staticmethod
    def _in_ipynb():
        try:
            from IPython import get_ipython
            cfg = get_ipython().config 
            if cfg['IPKernelApp']['parent_appname'] == 'ipython-notebook':
                return True
            else:
                return False
        except NameError:
            return False 
    
    def plotIPython(self):
        """
        plotear del HTML
        """
        todo_html = self.buildHTML()         
        
        if (self._in_ipynb()):
            from IPython.display import display,HTML
            return display(HTML(todo_html))
        
        
    def plotHTML(self,nombre_fichero=None):
        """
        plotear del HTML, sino se le pasa el nombre, se crea un fichero temporal
        """
        todo_html = self.buildHTML() 
            
        fichero = tempfile.NamedTemporaryFile(delete=True,prefix='pydygraph_') if (nombre_fichero is None) else open(nombre_fichero, 'w')    
        
        fichero.write(todo_html.encode('utf-8'))              
        
        webbrowser.open_new_tab(fichero.name)
        
        time.sleep(1);#Para que no se borre antes de abrirlo        
        
        fichero.close()    

    def pd2str(self, dataframe, index_timestamp=True):
        """
        Convierte dataframe al tipo requerido, EL indice debe de ser una fecha
        """
        indice_fechas= pd.to_datetime(dataframe.index).map(lambda fecha : 'new Date("{}")'.format(fecha.strftime('%Y/%m/%d %H:%M:%S'))) if index_timestamp else dataframe.index.values
        datos=np.column_stack((indice_fechas,dataframe.get_values()))
        
        #np.apply_along_axis(lambda fila: "[{}],".format(','.join(map(str,fila))).replace('nan', 'NaN'),1,a)            
        str_data = '['
        for linea_de_datos in datos:
            str_data += "[{}],\n".format(','.join(map(str,linea_de_datos))).replace('nan', 'NaN')

        str_data += ']'

        return  str_data


    def dictOpciones2str(self, diccionario):
        regex = re.compile("^{(.*)}$")  # Quitamos corchetes de inicio y fin
        opciones = regex.search(str(diccionario)).groups()[0]
        resultado=opciones.replace("'", '').replace('u["', '["')
        return resultado

    def dictAtributos2str(self, diccionario):
        resultado= json.dumps(diccionario).replace('{', '').replace('}', '').replace('"', '').replace(',', ';')
        return resultado

''' Diferentes utilies para pandas:'''
# Ayuda a unir de diferentes diccionarios, el valor de un mismo resultado


def joinN2(array_of_claves, dict_of_hash, clave):
    dicc = dict()
    for cod in array_of_claves:
        if len(dicc):
            dicc = dicc.join(
                dict_of_hash[cod][[clave]].rename(columns={clave: cod}), how='outer')
        else:
            dicc = dict_of_hash[cod][[clave]].rename(columns={clave: cod})
    return dicc


''' Para devolver un obejto cuando se lanza '''
if __name__ == "__main__":
    pydygraph = DygraphChart()
