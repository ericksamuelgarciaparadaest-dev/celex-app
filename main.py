import os

# Entorno gráfico estable para Windows y Android
os.environ['KIVY_GL_BACKEND'] = 'angle_sdl2'
os.environ['ANGLE_DEFAULT_PLATFORM'] = 'd3d11'
os.environ['KIVY_GRAPHICS'] = 'gles'

import psycopg2
from functools import partial
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField, MDTextFieldHintText
from kivymd.uix.button import MDButton, MDButtonText
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.list import MDList, MDListItem, MDListItemHeadlineText, MDListItemSupportingText
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.dialog import (
    MDDialog,
    MDDialogHeadlineText,
    MDDialogSupportingText,
    MDDialogButtonContainer,
)

DB_URI = "postgresql://neondb_owner:npg_uBxvgk0iyXK8@ep-fragrant-fog-b5cyavrb-pooler.c-7.us-east-2.aws.neon.tech/neondb?sslmode=require"

class BusquedaGeneralScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dialogo_detalle = None
        self.tabla_periodo_actual = None
        self.tablas_bimestres = []
        
        main_layout = MDBoxLayout(
            orientation='vertical',
            padding=[15, 20, 15, 10],
            spacing=10
        )

        # Header
        titulo = MDLabel(
            text="SISTEMA CELEX",
            halign="center",
            font_style="Headline",
            role="medium",
            size_hint_y=None,
            height=30
        )
        subtitulo = MDLabel(
            text="Búsqueda General por Bimestre",
            halign="center",
            font_style="Title",
            role="medium",
            theme_text_color="Custom",
            text_color=(0, 0.7, 0.7, 1),
            size_hint_y=None,
            height=25
        )
        main_layout.add_widget(titulo)
        main_layout.add_widget(subtitulo)

        # Selector de Periodo / Bimestre
        box_periodo = MDBoxLayout(
            orientation='horizontal',
            spacing=10,
            size_hint_y=None,
            height=45,
            pos_hint={"center_x": 0.5}
        )

        lbl_bim = MDLabel(
            text="Bimestre / Periodo:",
            size_hint_x=None,
            width=140,
            halign="left",
            font_style="Body",
            role="medium"
        )

        self.btn_bimestre = MDButton(
            MDButtonText(text="Cargando periodos... ▼"),
            on_release=self.abrir_menu_bimestres
        )

        box_periodo.add_widget(lbl_bim)
        box_periodo.add_widget(self.btn_bimestre)
        main_layout.add_widget(box_periodo)

        # Entrada de Texto con Búsqueda Inteligente (on_text)
        self.input_busqueda = MDTextField(
            MDTextFieldHintText(text="Escribe nombre, folio o matrícula..."),
            size_hint_y=None,
            height=50
        )
        self.input_busqueda.bind(text=self.al_cambiar_texto)
        main_layout.add_widget(self.input_busqueda)

        # Estado/Resultados
        self.lbl_estado = MDLabel(
            text="Conectando a Neon para consultar periodos...",
            halign="center",
            font_style="Body",
            role="small",
            size_hint_y=None,
            height=20
        )
        main_layout.add_widget(self.lbl_estado)

        # Contenedor con Scroll para Móvil
        scroll = MDScrollView(always_overscroll=False)
        self.lista_resultados = MDList()
        scroll.add_widget(self.lista_resultados)
        main_layout.add_widget(scroll)

        self.add_widget(main_layout)

        # Cargar las tablas de periodos disponibles
        self.obtener_tablas_bimestres()

    def obtener_tablas_bimestres(self):
        """Obtiene de Neon únicamente las tablas de periodos (excluye pb2 y tablas del sistema)."""
        try:
            with psycopg2.connect(DB_URI) as conn:
                with conn.cursor() as cur:
                    query = """
                        SELECT table_name 
                        FROM information_schema.tables 
                        WHERE table_schema = 'public' 
                          AND table_type = 'BASE TABLE'
                          AND table_name != 'pb2'
                        ORDER BY table_name DESC;
                    """
                    cur.execute(query)
                    filas = cur.fetchall()
                    self.tablas_bimestres = [f[0] for f in filas]

                    if self.tablas_bimestres:
                        self.tabla_periodo_actual = self.tablas_bimestres[0]
                        self.btn_bimestre.children[0].text = f"Periodo {self.tabla_periodo_actual} ▼"
                        self.lbl_estado.text = f"Periodos cargados. Escribe para buscar en {self.tabla_periodo_actual}."
                        self.crear_menu_bimestres()
                    else:
                        # Fallback a pb2 si no hay periodos
                        self.tabla_periodo_actual = "pb2"
                        self.btn_bimestre.children[0].text = "Tabla pb2 ▼"
                        self.lbl_estado.text = "Mostrando registros generales de pb2."
        except Exception as e:
            self.lbl_estado.text = f"Error al cargar periodos: {e}"

    def crear_menu_bimestres(self):
        """Construye las opciones del menú con las tablas de periodos encontradas."""
        menu_items = [
            {
                "text": f"Periodo: {t}",
                "on_release": lambda x=t: self.seleccionar_periodo(x)
            }
            for t in self.tablas_bimestres
        ]

        self.menu_bimestres = MDDropdownMenu(
            caller=self.btn_bimestre,
            items=menu_items,
            position="bottom",
            width_mult=4,
        )

    def abrir_menu_bimestres(self, instance):
        if hasattr(self, 'menu_bimestres'):
            self.menu_bimestres.open()

    def seleccionar_periodo(self, tabla):
        self.tabla_periodo_actual = tabla
        self.btn_bimestre.children[0].text = f"Periodo {tabla} ▼"
        self.menu_bimestres.dismiss()
        
        if self.input_busqueda.text.strip():
            self.ejecutar_busqueda_general(self.input_busqueda.text.strip())

    def al_cambiar_texto(self, instance, texto):
        criterio = texto.strip()
        if len(criterio) < 2:
            self.lista_resultados.clear_widgets()
            self.lbl_estado.text = "Escribe al menos 2 caracteres..."
            return
        
        if self.tabla_periodo_actual:
            self.ejecutar_busqueda_general(criterio)

    def ejecutar_busqueda_general(self, criterio):
        """
        Ejecuta la lógica de la App de Escritorio:
        Realiza un INNER JOIN entre la tabla de periodo elegida (ej. 2026_04) 
        y la tabla maestra de alumnos (pb2) anclada por la Matrícula/ID.
        """
        self.lista_resultados.clear_widgets()
        periodo = self.tabla_periodo_actual

        try:
            with psycopg2.connect(DB_URI) as conn:
                with conn.cursor() as cur:
                    # 1. Obtener estructura de columnas
                    cur.execute("SELECT * FROM pb2 LIMIT 0;")
                    cols_pb2 = [desc[0] for desc in cur.description]
                    col_id_pb2 = cols_pb2[0]

                    cur.execute(f'SELECT * FROM "{periodo}" LIMIT 0;')
                    cols_periodo = [desc[0] for desc in cur.description]
                    col_id_periodo = cols_periodo[0]

                    # 2. INNER JOIN entre pb2 y la tabla del periodo por matrícula/ID
                    sql = f"""
                        SELECT 
                            p.{col_id_pb2} AS matricula,
                            p.nombre AS nombre_alumno,
                            b.*
                        FROM pb2 p
                        INNER JOIN "{periodo}" b 
                            ON CAST(p.{col_id_pb2} AS TEXT) = CAST(b.{col_id_periodo} AS TEXT)
                        WHERE p.nombre ILIKE %s 
                           OR CAST(p.{col_id_pb2} AS TEXT) LIKE %s
                        LIMIT 30;
                    """
                    patron = f"%{criterio}%"
                    cur.execute(sql, (patron, patron))
                    registros = cur.fetchall()

                    if not registros:
                        self.lbl_estado.text = f"Sin alumnos inscritos en {periodo} para '{criterio}'"
                        return

                    self.lbl_estado.text = f"Coincidencias en Periodo {periodo}: {len(registros)}"

                    # 3. Mapear resultados a la lista
                    for reg in registros:
                        matricula = reg[0]
                        nombre_alumno = reg[1]
                        
                        # Guardar todos los datos del periodo
                        datos_periodo = dict(zip(cols_periodo, reg[2:]))
                        datos_periodo['nombre'] = nombre_alumno
                        datos_periodo['matricula'] = matricula

                        # Extraer detalles relevantes para el subtítulo
                        detalles = []
                        for col in ['curso', 'nivel', 'grupo', 'horario', 'estatus', 'calificacion']:
                            if col in datos_periodo and datos_periodo[col]:
                                detalles.append(f"{col.capitalize()}: {datos_periodo[col]}")

                        subtexto = f"Matrícula: {matricula}"
                        if detalles:
                            subtexto += " • " + " | ".join(detalles)

                        item = MDListItem(
                            MDListItemHeadlineText(text=f"{nombre_alumno}"),
                            MDListItemSupportingText(text=subtexto)
                        )
                        item.bind(on_release=partial(self.abrir_ficha_inscripcion, datos_periodo, periodo))
                        self.lista_resultados.add_widget(item)

        except Exception as e:
            # Si la tabla del periodo no requiere JOIN o difiere, consulta directa
            self.busqueda_directa_periodo(criterio, periodo)

    def busqueda_directa_periodo(self, criterio, periodo):
        """Lógica de respaldo para consultar la tabla de periodo directamente."""
        try:
            with psycopg2.connect(DB_URI) as conn:
                with conn.cursor() as cur:
                    cur.execute(f'SELECT * FROM "{periodo}" LIMIT 0;')
                    columnas = [desc[0] for desc in cur.description]

                    sql = f"""
                        SELECT * FROM "{periodo}"
                        WHERE CAST({columnas[0]} AS TEXT) LIKE %s
                           OR (ARRAY_TO_STRING(ARRAY_ROW(*), ' ')) ILIKE %s
                        LIMIT 30;
                    """
                    patron = f"%{criterio}%"
                    cur.execute(sql, (patron, patron))
                    registros = cur.fetchall()

                    if not registros:
                        self.lbl_estado.text = f"Sin registros en {periodo} para '{criterio}'"
                        return

                    self.lbl_estado.text = f"Registros en {periodo}: {len(registros)}"

                    for reg in registros:
                        fila = dict(zip(columnas, reg))
                        mat = reg[0]
                        nombre = fila.get('nombre', f"Matrícula: {mat}")

                        item = MDListItem(
                            MDListItemHeadlineText(text=f"{nombre}"),
                            MDListItemSupportingText(text=f"Matrícula/ID: {mat} | Periodo: {periodo}")
                        )
                        item.bind(on_release=partial(self.abrir_ficha_inscripcion, fila, periodo))
                        self.lista_resultados.add_widget(item)

        except Exception as err:
            self.lbl_estado.text = f"Error al consultar periodo '{periodo}': {err}"

    def abrir_ficha_inscripcion(self, datos, periodo, *args):
        """Abre la ficha modal detallada con los datos del periodo seleccionado."""
        lineas = []
        for col, val in datos.items():
            val_fmt = str(val) if val is not None else "---"
            lineas.append(f"• [b]{col.upper()}:[/b] {val_fmt}")
        
        texto_ficha = "\n".join(lineas)

        self.dialogo_detalle = MDDialog(
            MDDialogHeadlineText(
                text=str(datos.get('nombre', 'Ficha del Alumno'))
            ),
            MDDialogSupportingText(
                text=f"Inscripción en Periodo [b]{periodo}[/b]:\n\n{texto_ficha}"
            ),
            MDDialogButtonContainer(
                MDButton(
                    MDButtonText(text="CERRAR"),
                    on_release=lambda x: self.dialogo_detalle.dismiss()
                ),
                spacing="8dp",
            ),
        )
        self.dialogo_detalle.open()


class CelexApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Teal"
        return BusquedaGeneralScreen()

if __name__ == "__main__":
    CelexApp().run()