import io
from xhtml2pdf import pisa
from datetime import datetime
from typing import List, Dict, Any
from zoneinfo import ZoneInfo
from domain.repositories.pdf_repository_interface import IPDFRepository


"""
Infrastructure repository to generate PDF reports.
"""


class PDFRepository(IPDFRepository):
    def generate_quality_report(
        self,
        errors: List[Dict[str, Any]],
        warnings: List[Dict[str, Any]],
        duplicados: List[Dict[str, Any]] | None = None,
        institution: str = "",
        filename: str = "",
        upload_date: str = "",
        user: str = "",
    ) -> io.BytesIO:
        report_date = datetime.now(ZoneInfo("America/Bogota")).strftime("%d/%m/%Y %H:%M")

        if errors:
            title = "Reporte de Calidad de Datos"
            intro = """
                <h2><li>Corrección de errores en la información cargada</li></h2>
                <p>
                    Este reporte tiene como objetivo concientizar sobre la importancia de la calidad de los datos.
                    Al revisar los archivos enviados se identificaron <b>dos tipos de observaciones</b>:
                </p>
                <ul>
                    <li><b>Errores:</b> Deben corregirse de manera obligatoria antes de volver a cargar la información.</li>
                    <li><b>Advertencias:</b> No requieren corrección inmediata, pero pueden afectar el funcionamiento de algunos filtros en la plataforma 
                    (por ejemplo, que cierta información no aparezca en el excel o nuevos roles en algunas columnas).</li>
                </ul>
                <p><b>Recomendación:</b> Corregir siempre ambos tipos para garantizar la mejor calidad de los datos.</p>
                <h2><li>Estructura de Datos Esperada</li></h2>
                <p>La siguiente tabla describe el formato estándar que debe seguirse al cargar los datos:</p>
                <table>
                    <tr><th>Columna</th><th>Valores admitidos / Observaciones</th></tr>
                    <tr><td>tipo_documento</td><td>cédula de ciudadanía, cédula de extranjería, pasaporte</td></tr>
                    <tr><td>identificación</td><td>Número de identificación según tipo</td></tr>
                    <tr><td>primer_apellido</td><td>Primer apellido del autor</td></tr>
                    <tr><td>segundo_apellido</td><td>Segundo apellido del autor</td></tr>
                    <tr><td>nombres</td><td>Todos los nombres del autor</td></tr>
                    <tr><td>nivel_académico</td><td>técnico, pregrado, maestría, doctorado, especialización, especialización médica</td></tr>
                    <tr><td>tipo_contrato</td><td>vinculado, ocasional, cátedra, prestación de servicios, postdoc</td></tr>
                    <tr><td>jornada_laboral</td><td>medio tiempo, tiempo completo, tiempo parcial</td></tr>
                    <tr><td>categoría_laboral</td><td>auxiliar, asociado, titular</td></tr>
                    <tr><td>sexo</td><td>hombre, mujer, intersexual (vacío si no se tiene)</td></tr>
                    <tr><td>fechas (nacimiento / inicial vinculación / final vinculación)</td><td>Formato DD/MM/YYYY (fecha corta de Excel)</td></tr>
                    <tr><td>código_unidad_académica</td><td>Código único (fijo en futuras actualizaciones)</td></tr>
                    <tr><td>unidad_académica</td><td>Nombre completo de la facultad o dependencia</td></tr>
                    <tr><td>código_subunidad_académica</td><td>Código único de subunidad (si existe)</td></tr>
                    <tr><td>subunidad_académica</td><td>Nombre del departamento o subunidad</td></tr>
                </table>

                <h2><li> Recomendaciones Adicionales</li></h2>
                <ul>
                    <li>Evitar <b>abreviaciones</b>. Ejemplo: <i>Fac Med</i> → <i>Facultad de Medicina</i> </li>
                    <li><b>unidad_académica</b> puede equivaler a facultad en algunas instituciones.</li>
                    <li><b>subunidad_académica</b> puede equivaler a departamento.</li>
                    <li>Revisar que no existan <b>caracteres extraños</b> o problemas de codificación.</li>
                    <li>Si la institución solo maneja <b>un nivel</b>, se diligencian únicamente las unidades académicas y se deja vacío el campo de subunidades.</li>
                </ul>

                <p class="note">
                    Documento de referencia: 
                    <a href="https://data.colav.co/Formato_datos_impactu.pdf">Formato original de información</a>
                </p>
            """

        else:
            title = "Reporte de Subida Exitoso"
            intro = """
                <p>
                    El archivo fue cargado correctamente, pero se detectaron observaciones que deben ser tenidas en cuenta.
                </p>
            """
        html = f"""
        <html>
            <head>
                <style>
                    @page {{
                        @frame header_frame {{
                            -pdf-frame-content: header_content;
                            top: 0px;
                            left: 0px;
                            width: 100%;
                            heigth: 100px;
                        }}
                        @frame content_frame {{
                            top: 120px;
                            left: 20px;
                            right: 20px;
                            bottom: 20px;
                        }}
                    }}
                    body {{
                        font-family: Arial, sans-serif;
                        font-size: 12px;
                    }}
                    h1, h2, h3 {{
                        color: black;
                        font-weight: bold;
                        text-align: center;
                    }}
                    h2, h3 {{
                        text-align: left;
                        margin-top: 20px;
                    }}
                    p {{
                        text-align: justify;
                        margin: 10px 0;
                    }}
                    table {{
                        width: 100%;
                        border: 1px solid #000;
                        margin-top: 20px;
                        border-collapse: collapse;
                        table-layout: fixed;
                    }}
                    table th {{
                        background-color: #f2f2f2;
                        padding: 5px;
                        font-weight: bold;
                        text-align: center;
                    }}
                    tr, td, th {{
                        page-break-inside: avoid;
                        text-align: center;
                        padding: 5px;
                    }}
                    .header-img {{
                        width: 100%;
                        height: auto;
                        display: block;
                        margin: 0;
                        padding: 0;
                    }}
                    .note {{
                        font-size: 11px;
                        color: #555;
                        margin-top: 10px;
                    }}
                    .cell-content{{
                        display: block;
                        white-space: normal;
                        word-wrap: break-word;
                        overflow-wrap: break-word;
                        page-break-inside: auto;
                    }}
                </style>
            </head>
            <body>
                <div id="header_content" style="width:100%">
                    <img src="https://raw.githubusercontent.com/jhonbg/fotos/main/Membrete_Header.png" class="header-img"/>
                </div>
                <h1>{title}</h1>
                
                <p><b>Institución:</b> {institution}<br>
                <b>Archivo validado:</b> {filename}<br>
                <b>Fecha y hora de carga:</b> {upload_date}<br>
                <b>Fecha y hora de generación del reporte:</b> {report_date}<br>
                <b>Usuario responsable:</b> {user}</p>
                {intro}
        """
        if errors:
            html += """
                    <h2><li> Errores Encontrados<li></h2>
                    <table>
                        <tr>
                            <th>Columna</th>
                            <th>Detalle</th>
                            <th>Ejemplos (máx. 3)</th>
                            <th>Número de filas con el error</th>
                        </tr>
            """

            for err in errors:
                columna_e = err.get("columna", "")
                detalle_e = err.get("detalle", "")
                ejemplos_e = ", ".join(map(str, err.get("ejemplos", [])))
                total_e = err.get("total_filas", 0)
                html += f"""
                    <tr>
                        <td> {columna_e} </td>
                        <td> {detalle_e} </td>
                        <td> {ejemplos_e} </td>
                        <td> {total_e} </td>
                    </tr>
                """

            html += "</table>"
        if warnings:
            html += """
                <h2><li> Advertencias Encontradas</li></h2>
                <table>
                    <tr>
                        <th>Columna</th>
                        <th>Detalle</th>
                        <th>Valor</th>
                        <th>Ejemplos (máx. 3)</th>
                        <th>Número de filas con la advertencias</th>
                    </tr>
            """

            for warn in warnings:
                columna_w = warn.get("columna", "")
                detalle_w = warn.get("detalle", "")
                valor_w = warn.get("valor", "")
                ejemplos_W = ", ".join(map(str, warn.get("ejemplos", [])))
                total_w = warn.get("total_filas", 0)
                html += f"""
                    <tr>
                        <td> {columna_w} </td>
                        <td> {detalle_w} </td>
                        <td> {valor_w} </td>
                        <td> {ejemplos_W} </td>
                        <td> {total_w} </td>
                    </tr>
                """
            html += "</table>"

        if duplicados and len(duplicados) > 0:
            html += f"<h2><li>Duplicados</li></h2><p>Se detectaron {len(duplicados)} registros duplicados.</p>"
            eje = duplicados[:2]
            html += "<p><b>Ejemplo de duplicados:</b></p><ul>"
            for dup in eje:
                dup.get("index") or "?"
                row = dup.get("row") or {}
                preview = {
                    "identificación": row.get("identificación"),
                    "primer_apellido": row.get("primer_apellido"),
                    "nombres": row.get("nombres"),
                    "jornada_laboral": row.get("jornada_laboral"),
                    "....": "....",
                    "unidad_académica": row.get("unidad_académica"),
                }
                html += f"<li>{preview}</li>"
            html += "</ul>"

        html += "</body></html>"

        pdf_bytes = io.BytesIO()
        pisa.CreatePDF(io.StringIO(html), dest=pdf_bytes)
        pdf_bytes.seek(0)
        return pdf_bytes
    
    def generate_quality_report_ciarp(
        self,
        errors: List[Dict[str, Any]],
        warnings: List[Dict[str, Any]],
        duplicados: List[Dict[str, Any]] | None = None,
        institution: str = "",
        filename: str = "",
        upload_date: str = "",
        user: str = "",
    ) -> io.BytesIO:
        report_date = datetime.now(ZoneInfo("America/Bogota")).strftime("%d/%m/%Y %H:%M")

        if errors:
            title = "Reporte de Calidad de Datos"
            intro = """
                <h2><li>Corrección de errores en la información cargada</li></h2>
                <p>
                    Este reporte tiene como objetivo concientizar sobre la importancia de la calidad de los datos.
                    Al revisar los archivos enviados se identificaron <b>dos tipos de observaciones</b>:
                </p>
                <ul>
                    <li><b>Errores:</b> Deben corregirse de manera obligatoria antes de volver a cargar la información.</li>
                    <li><b>Advertencias:</b> No requieren corrección inmediata, pero pueden afectar el funcionamiento de algunos filtros en la plataforma 
                    (por ejemplo, que cierta información no aparezca en el excel o nuevos roles en algunas columnas).</li>
                </ul>
                <p><b>Recomendación:</b> Corregir siempre ambos tipos para garantizar la mejor calidad de los datos.</p>
                <h2><li>Estructura de Datos Esperada</li></h2>
                <p>La siguiente tabla describe el formato estándar que debe seguirse al cargar los datos:</p>
                <table>
                    <tr><th>Columna</th><th>Valores admitidos / Observaciones</th></tr>
                    <tr><td>tipo_documento</td><td>cédula de ciudadanía, cédula de extranjería, pasaporte</td></tr>
                    <tr><td>identificación</td><td>Número de identificación según tipo</td></tr>
                    <tr><td>primer_apellido</td><td>Primer apellido del autor</td></tr>
                    <tr><td>segundo_apellido</td><td>Segundo apellido del autor</td></tr>
                    <tr><td>nombres</td><td>Todos los nombres del autor</td></tr>
                    <tr><td>nivel_académico</td><td>técnico, pregrado, maestría, doctorado, especialización, especialización médica</td></tr>
                    <tr><td>tipo_contrato</td><td>vinculado, ocasional, cátedra, prestación de servicios, postdoc</td></tr>
                    <tr><td>jornada_laboral</td><td>medio tiempo, tiempo completo, tiempo parcial</td></tr>
                    <tr><td>categoría_laboral</td><td>auxiliar, asociado, titular</td></tr>
                    <tr><td>sexo</td><td>hombre, mujer, intersexual (vacío si no se tiene)</td></tr>
                    <tr><td>fechas (nacimiento / inicial vinculación / final vinculación)</td><td>Formato DD/MM/YYYY (fecha corta de Excel)</td></tr>
                    <tr><td>código_unidad_académica</td><td>Código único (fijo en futuras actualizaciones)</td></tr>
                    <tr><td>unidad_académica</td><td>Nombre completo de la facultad o dependencia</td></tr>
                    <tr><td>código_subunidad_académica</td><td>Código único de subunidad (si existe)</td></tr>
                    <tr><td>subunidad_académica</td><td>Nombre del departamento o subunidad</td></tr>
                </table>

                <h2><li> Recomendaciones Adicionales</li></h2>
                <ul>
                    <li>Evitar <b>abreviaciones</b>. Ejemplo: <i>Fac Med</i> → <i>Facultad de Medicina</i> </li>
                    <li><b>unidad_académica</b> puede equivaler a facultad en algunas instituciones.</li>
                    <li><b>subunidad_académica</b> puede equivaler a departamento.</li>
                    <li>Revisar que no existan <b>caracteres extraños</b> o problemas de codificación.</li>
                    <li>Si la institución solo maneja <b>un nivel</b>, se diligencian únicamente las unidades académicas y se deja vacío el campo de subunidades.</li>
                </ul>

                <p class="note">
                    Documento de referencia: 
                    <a href="https://data.colav.co/Formato_datos_impactu.pdf">Formato original de información</a>
                </p>
            """

        else:
            title = "Reporte de Subida Exitoso"
            intro = """
                <p>
                    El archivo fue cargado correctamente, pero se detectaron observaciones que deben ser tenidas en cuenta.
                </p>
            """
        html = f"""
        <html>
            <head>
                <style>
                    @page {{
                        @frame header_frame {{
                            -pdf-frame-content: header_content;
                            top: 0px;
                            left: 0px;
                            width: 100%;
                            heigth: 100px;
                        }}
                        @frame content_frame {{
                            top: 120px;
                            left: 20px;
                            right: 20px;
                            bottom: 20px;
                        }}
                    }}
                    body {{
                        font-family: Arial, sans-serif;
                        font-size: 12px;
                    }}
                    h1, h2, h3 {{
                        color: black;
                        font-weight: bold;
                        text-align: center;
                    }}
                    h2, h3 {{
                        text-align: left;
                        margin-top: 20px;
                    }}
                    p {{
                        text-align: justify;
                        margin: 10px 0;
                    }}
                    table {{
                        width: 100%;
                        border: 1px solid #000;
                        margin-top: 20px;
                        border-collapse: collapse;
                        table-layout: fixed;
                    }}
                    table th {{
                        background-color: #f2f2f2;
                        padding: 5px;
                        font-weight: bold;
                        text-align: center;
                    }}
                    tr, td, th {{
                        page-break-inside: avoid;
                        text-align: center;
                        padding: 5px;
                    }}
                    .header-img {{
                        width: 100%;
                        height: auto;
                        display: block;
                        margin: 0;
                        padding: 0;
                    }}
                    .note {{
                        font-size: 11px;
                        color: #555;
                        margin-top: 10px;
                    }}
                    .cell-content{{
                        display: block;
                        white-space: normal;
                        word-wrap: break-word;
                        overflow-wrap: break-word;
                        page-break-inside: auto;
                    }}
                </style>
            </head>
            <body>
                <div id="header_content" style="width:100%">
                    <img src="https://raw.githubusercontent.com/jhonbg/fotos/main/Membrete_Header.png" class="header-img"/>
                </div>
                <h1>{title}</h1>
                
                <p><b>Institución:</b> {institution}<br>
                <b>Archivo validado:</b> {filename}<br>
                <b>Fecha y hora de carga:</b> {upload_date}<br>
                <b>Fecha y hora de generación del reporte:</b> {report_date}<br>
                <b>Usuario responsable:</b> {user}</p>
                {intro}
        """
        if errors:
            html += """
                    <h2><li> Errores Encontrados<li></h2>
                    <table>
                        <tr>
                            <th>Columna</th>
                            <th>Detalle</th>
                            <th>Ejemplos (máx. 3)</th>
                            <th>Número de filas con el error</th>
                        </tr>
            """

            for err in errors:
                columna_e = err.get("columna", "")
                detalle_e = err.get("detalle", "")
                ejemplos_e = ", ".join(map(str, err.get("ejemplos", [])))
                total_e = err.get("total_filas", 0)
                html += f"""
                    <tr>
                        <td> {columna_e} </td>
                        <td> {detalle_e} </td>
                        <td> {ejemplos_e} </td>
                        <td> {total_e} </td>
                    </tr>
                """

            html += "</table>"
        if warnings:
            html += """
                <h2><li> Advertencias Encontradas</li></h2>
                <table>
                    <tr>
                        <th>Columna</th>
                        <th>Detalle</th>
                        <th>Valor</th>
                        <th>Ejemplos (máx. 3)</th>
                        <th>Número de filas con la advertencias</th>
                    </tr>
            """

            html += f"""
                <h3>Advertencias</h3>
                <p><strong>Total de advertencias:</strong> {warnings["total_advertencias"]}</p>
            """
            html += "</table>"

        if duplicados and len(duplicados) > 0:
            html += f"<h2><li>Duplicados</li></h2><p>Se detectaron {len(duplicados)} registros duplicados.</p>"
            eje = duplicados[:2]
            html += "<p><b>Ejemplo de duplicados:</b></p><ul>"
            for dup in eje:
                dup.get("index") or "?"
                row = dup.get("row") or {}
                preview = {
                    "identificación": row.get("identificación"),
                    "primer_apellido": row.get("primer_apellido"),
                    "nombres": row.get("nombres"),
                    "jornada_laboral": row.get("jornada_laboral"),
                    "....": "....",
                    "unidad_académica": row.get("unidad_académica"),
                }
                html += f"<li>{preview}</li>"
            html += "</ul>"

        html += "</body></html>"

        pdf_bytes = io.BytesIO()
        pisa.CreatePDF(io.StringIO(html), dest=pdf_bytes)
        pdf_bytes.seek(0)
        return pdf_bytes
