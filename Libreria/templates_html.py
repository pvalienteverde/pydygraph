# -*- coding: utf-8 -*-


class templates_html(object):
    __template_chart_asincrono__ = """
      $id_interno = new Dygraph(
          document.getElementById("$idc"),
          $tipo_datos,
          {
            $opciones
            }
      );
"""

    __more_opciones_sincrono__ = """
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

    __template_push_sincrono__ = """
        $id_grupo.push(
          $id_interno
        );
"""

    __template_js__ = """
<script type="text/javascript">
    $charts
    $funciones_script
</script>
"""

    __template_html__ = """
<html>
<head>

<link rel="stylesheet" href=$ruta_archivo_css>
<style type="text/css">
    $css
</style>

<script type="text/javascript"
    src="http://dygraphs.com/1.1.0/dygraph-combined.js"></script>
</head>
<body>

$contenedor

$js

</body>
</html>    
"""

    __template_cuerpo_interno__ = """
<div id="$idc" style="$atributos"></div>
"""

    __template_opc_visibilidad__ = """
    function change_$id_interno(el) {
        $id_interno_asin.setVisibility(parseInt(el.id), el.checked);
    }
"""

    __template_label_visibilidad__ = """
    <input type=checkbox id="$id_num_curva" checked onClick="change_$id_interno(this)">
    <label for="$id_num_curva"> $descriptor_curva </label>
"""
