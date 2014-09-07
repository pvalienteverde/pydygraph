#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Ayuda sobre los metodos se los objetos DyGraph: http://dygraphs.com/jsdoc/symbols/Dygraph.html
"""


from string import Template #https://docs.python.org/2/library/stdtypes.html#string-formatting
import pandas as pd
import json
from templates_html import templates_html
    
class DygraphChart(templates_html):
    
    def __init__(self, **kwargs):
        """
        Constructor
        """
        self.__numero_chart__=0
        self.__contenedor__=''
        self.__charts_sincronizados__={}
        self.__charts_no_sincronizados__=[]
        self.__datos_charts__={}
        self.__opciones_charts__={}
        self.__visibilidad__={}
        self.__estilos_css_a_inclustar__=[]      # Ayuda: http://www.w3schools.com/css/default.asp    
        self.__atributos_charts__={}
        
        self.__atributos_charts_default__={'width':'100%',
                                           'height':'400px'}
                                        
        self.__opciones_charts_default__={'showRangeSelector': 'true',
                                          'legend': "'always'",}                                
    
    def addSerie(self,*args,**kwargs):
        """
        Se añade la serie a plotear
        """
        self.__numero_chart__+=1
        kwargs['idc']="div%03d" %(self.__numero_chart__)
        
        self.addChart(**kwargs)
        self.addCuerpo(*args,**kwargs)
        
    def addHtml(self,*args):
        """
        Se añade la serie a plotear
        """
        self.addCuerpo(*args)
    
    def addChart(self,**kwargs):
        '''
        Constructor de cada uno del jschart
        '''
        
        #Introducimos valores por defecto
        
        opciones_usuario=self.__opciones_charts_default__.copy()       
        if kwargs.has_key('opciones'):
            opciones_usuario=dict(opciones_usuario.items()+kwargs['opciones'].copy().items())  
            
        atributos_usuarios=self.__atributos_charts_default__.copy()
        if kwargs.has_key('atributos'):
            atributos_usuarios=dict(atributos_usuarios.items()+kwargs['atributos'].copy().items())  
        
        
        if kwargs.has_key('nombre_fichero') and kwargs.has_key('dataframe'):
            raise AssertionError("No se puede utilizar el argumento nombre_fichero y dataframe a la vez") 
            
        if kwargs.has_key('nombre_fichero'):
            kwargs['tipo_datos']='"'+kwargs['nombre_fichero']+'"'
        elif kwargs.has_key('dataframe'):
            kwargs['tipo_datos']=self.pd2str(kwargs['dataframe'])
            opciones_usuario['labels']='["Indice","'+'","'.join(kwargs['dataframe'].columns.values)+'"]'
        else:
            raise AssertionError("Se necesita alguna fuente de datos")              
        
        
        
        # Creamos los grupos de sincronizacion o no
        if kwargs.has_key('sincronizar'):
            # GUardamos en cada grupo de sincronizacion
            if self.__charts_sincronizados__.has_key(kwargs['sincronizar']):
                self.__charts_sincronizados__[kwargs['sincronizar']].append(kwargs['idc'])
            else:
                self.__charts_sincronizados__[kwargs['sincronizar']]=[kwargs['idc']]
        else:
            self.__charts_no_sincronizados__.append(kwargs['idc'])             
            
        # Guardamos los datos
        self.__datos_charts__[kwargs['idc']]=kwargs['tipo_datos']
        self.__opciones_charts__[kwargs['idc']]=opciones_usuario
        self.__atributos_charts__[kwargs['idc']]=atributos_usuarios
        # Generamos la opcion de chequear la visibilidad, por ahora solamente para asincronos
        self.__visibilidad__[kwargs['idc']]=kwargs.get('anadir_opc_visibilidad',True) 
            
            
        
    def buildJs(self):
        '''
        COntructor del recubrimiento del js        
        '''
        more_opciones=''
        #more_opciones+="""
        #        ,highlightSeriesOpts: {
		#		  strokeWidth: 3,
		#		  strokeBorderWidth: 1,
		#		  highlightCircleSize: 5,
		#		}
           #         """        
        
        cuerpo_js = Template(self.__template_js__)        
        
        # Primeros generamos los que no estan sincronizados con ninguno
        cuerpo_charts_asin = Template(self.__template_chart_asincrono__) 
        js_asincrono=''
        js_opc_visibilidad=''
        for id_manejador in self.__charts_no_sincronizados__:
            id_interno_charts="asin_"+id_manejador
            js_asincrono += cuerpo_charts_asin.substitute(id_interno=id_interno_charts,
                                                          idc=id_manejador,
                                                          tipo_datos=self.__datos_charts__[id_manejador],
                                                          opciones=self.dictOpciones2str(self.__opciones_charts__[id_manejador])+more_opciones)
            
            if self.__visibilidad__[id_manejador]:
                cuerpo_opc_visibilidad = Template(self.__template_opc_visibilidad__)
                js_opc_visibilidad += cuerpo_opc_visibilidad.substitute(id_interno_asin=id_interno_charts,
                                                                        id_interno=id_manejador)
        script_asincrono=cuerpo_js.substitute(charts=js_asincrono+js_opc_visibilidad)        
        
        
        
        
        # AHora los que están sincronizados, se generarán por grupos
        cuerpo_charts_sin_push = Template(self.__template_push_sincrono__)
        script_sincrono=''
        for id_grupo_manejador in self.__charts_sincronizados__:
            js_sincrono=id_grupo_manejador+''' = [];
            var blockRedraw = false;
            var initialized = false;
            '''         
            
            for id_manejador in self.__charts_sincronizados__[id_grupo_manejador]:
                id_interno_charts="sin_"+id_manejador
                cuerpo_grupo_sincro=Template(self.__more_opciones_sincrono__)
                more_opciones_sincro=cuerpo_grupo_sincro.substitute(num_elementos_interactivos=len(self.__charts_sincronizados__[id_grupo_manejador]),
                                                              id_grupo=id_grupo_manejador)
                js_sincrono += cuerpo_charts_asin.substitute(id_interno=id_interno_charts,
                                                              idc=id_manejador,
                                                              tipo_datos=self.__datos_charts__[id_manejador],
                                                              opciones=self.dictOpciones2str(self.__opciones_charts__[id_manejador])+more_opciones_sincro+more_opciones)
                
                if self.__visibilidad__[id_manejador]:
                    cuerpo_opc_visibilidad = Template(self.__template_opc_visibilidad__)
                    js_opc_visibilidad += cuerpo_opc_visibilidad.substitute(id_interno_asin=id_interno_charts,
                                                                            id_interno=id_manejador)
                js_sincrono+=cuerpo_charts_sin_push.substitute(id_interno=id_interno_charts,
                                                               id_grupo=id_grupo_manejador)                                                            
           #Lo relleno                                                                            
            script_sincrono_charts=js_sincrono+js_opc_visibilidad                                                           
            script_sincrono+=cuerpo_js.substitute(charts=script_sincrono_charts+script_sincrono_charts)
        
        
        return script_asincrono+script_sincrono
    
# Sobre los **kwargs: http://www.juanjoconti.com.ar/2010/10/13/entendiendo-args-y-kwargs-en-python/    
    def addCuerpo(self,*args,**kwargs):
        """
        Tanto para incorporar contenido interno como externo, debe ser lineal
        """
        titulo=""
        if len(args) != 0:
            for elemento in args:
                titulo += str(elemento) +"\n"
                
        anadir_chart=""
        if len(kwargs) != 0:
            cuerpo_contenedor = Template(self.__template_cuerpo_interno__)
            anadir_chart+= cuerpo_contenedor.substitute(idc=kwargs['idc'],
                                                        atributos=self.dictAtributos2str(self.__atributos_charts__[kwargs['idc']]))
            
            if self.__visibilidad__[kwargs['idc']]:
                cuerpo_label_visibilidad= Template(self.__template_label_visibilidad__)
                anadir_chart += '<p class="texto_centrado"><b>Series :</b>'
                for id_num_curva,id_str_curva in enumerate(kwargs['dataframe'].columns.values):                    
                    anadir_chart += cuerpo_label_visibilidad.substitute(id_num_curva=id_num_curva,
                                                                        descriptor_curva=id_str_curva,
                                                                        id_interno=kwargs['idc'])
                anadir_chart += '</p>'
            
        
        self.__contenedor__ += titulo + anadir_chart
        
    
    def buildCSS(self):
        estilos_css=''
        for css in self.__estilos_css_a_inclustar__:
            estilos_css+=css
        return estilos_css
        
        
    def addCSS(self,identificador,atributos):
        if identificador is None or atributos is None:
            raise AssertionError("Falta ipor declarar idenrificaodr o los atributos")
        
        self.__estilos_css_a_inclustar__.append("."+identificador+'{'+atributos+"}\n")       
                
        
    def buildHTML(self):
        """
        Creacion del HTML
        """
        cuerpo_html = Template(self.__template_html__)
        return cuerpo_html.substitute(css=self.buildCSS(),contenedor=self.__contenedor__,js=self.buildJs())
    
    def pd2str(self,dataframe):
        
        """
        Convierte dataframe al tipo requerido, EL indice debe de ser una fecha
        """
        template_datos="""[new Date("$indice"),$datos],\n"""
        str_data='['        
        cuerpo = Template(template_datos)
        for index_date, datos_brutos in zip(pd.to_datetime(dataframe.index.values), dataframe.get_values()):
            str_data += cuerpo.substitute(indice=index_date.strftime('%Y/%m/%d %H:%M:%S'),datos=','.join(map(str, datos_brutos)).replace('nan','NaN'))
        
        str_data+=']'
        return str_data
     
    
    def dictOpciones2str(self,diccionario):
        return str(diccionario).replace("'",'').replace('{','').replace('}','')
    
    def dictAtributos2str(self,diccionario):
        return json.dumps(diccionario).replace('{','').replace('}','').replace('"','').replace(',',';')
  
''' Diferentes utilies para pandas:'''
# Ayuda a unir de diferentes diccionarios, el valor de un mismo resultado 
def joinN2(array_of_claves,dict_of_hash,clave):
    dicc=dict()
    for cod in array_of_claves:
        if len(dicc):
            dicc=dicc.join(dict_of_hash[cod][[clave]].rename(columns={clave: cod}),how='outer')
        else:
            dicc=dict_of_hash[cod][[clave]].rename(columns={clave: cod})
    return dicc
      
        
''' Para devolver un obejto cuando se lanza '''       
if __name__ == "__main__":
    pydygraph = DygraphChart()        
        
        
        
        
        
        
        
        
        