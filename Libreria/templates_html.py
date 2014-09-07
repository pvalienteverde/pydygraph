# -*- coding: utf-8 -*-


class templates_html(object):    
    __template_chart_asincrono__="""
      $id_interno = new Dygraph(
          document.getElementById("$idc"),
          $tipo_datos,
          {
            $opciones
            }
      );
"""
    
    __more_opciones_sincrono__="""
            ,drawCallback: function(me, initial) {
                if (blockRedraw || initial) return;
                blockRedraw = true;
                var range = me.xAxisRange();
                //var yrange = me.yAxisRange();
                for (var j = 0; j < $num_elementos_interactivos; j++) {
                  if ($id_grupo[j] == me) continue;
                  $id_grupo[j].updateOptions( {
                    dateWindow: range,
                    //valueRange: yrange
                  } );
                }
                blockRedraw = false;
            }
"""    
    
    __template_push_sincrono__="""
        $id_grupo.push(
          $id_interno
        );
"""    
    
    __template_js__="""
<script type="text/javascript">
    $charts
    $funciones_script
</script>
"""


    __template_html__="""
<html>
<head>

<link rel="stylesheet" href="/home/pedro/workspacePython/pydygraph/style.css">
<style type="text/css">
    $css
</style>

<script type="text/javascript"
    src="/home/pedro/workspacePython/pydygraph/dygraph-combined.js"></script>
</head>
<body>

$contenedor

$js

</body>
</html>    
"""

    __template_cuerpo_interno__="""
<div id="$idc" style="$atributos"></div>
"""

    __template_opc_visibilidad__="""
    function change_$id_interno(el) {
        $id_interno_asin.setVisibility(parseInt(el.id), el.checked);
    }
"""

    __template_label_visibilidad__="""
    <input type=checkbox id="$id_num_curva" checked onClick="change_$id_interno(this)">
    <label for="$id_num_curva"> $descriptor_curva </label>
"""
    
    
class axesXHTML(object):
        
    
    opcion_axes_x_numero={
        'axes':"""{x:{axisLabelFormatter:function(x){return continuo2Time(x)},valueFormatter: function(x){return continuo2Time(x)},},}"""
    }

    funcion_axes_x_numero="""
    function continuo2Time(x) {
							var dias_aviles=parseInt(x/30600);
							var dias_totales=dias_aviles+parseInt(dias_aviles/5)*2;
							var segundo_unix=dias_totales*86400+x%30600+1388966400+7*3600;
							var a = new Date(segundo_unix*1000);
							var year = a.getFullYear();
							 var month = a.getMonth();
							 var date = a.getDate();
							 var hour = a.getHours();
							 var min = a.getMinutes();
							 var sec = a.getSeconds();
							 var time_str = year+'/'+month+'/'+date+' '+hour+':'+min+':'+sec;
							 return time_str;
                        }
    """