"""Genera el informe PDF de diagnostico de la AE1 de Unidad II."""

from pathlib import Path
import hashlib
import sys
import zipfile

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from PIL import Image as PILImage, ImageDraw, ImageFont

# ReportLab is provided by the Codex document runtime. Appending after loading
# the project's numeric stack avoids replacing this venv's NumPy/Pandas wheels.
sys.path.append(r"C:\Users\crepe\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\Lib\site-packages")
from reportlab.graphics.shapes import Drawing, Rect, String
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import BaseDocTemplate, Frame, Image, PageBreak, PageTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "raw" / "dry_bean_dataset" / "DryBeanDataset" / "Dry_Bean_Dataset.xlsx"
OUT = ROOT / "docs" / "Hernandez_Trejo_Kevin_U2_AE1_Diagnostico.pdf"
CHARTS = ROOT / "tmp" / "pdfs" / "u2_ae1"
CHARTS.mkdir(parents=True, exist_ok=True)
COVER = CHARTS / "portada_institucional_u2.png"
TEMPLATE_DOCX = Path(r"C:\Users\crepe\Downloads\U2_Fase 4AP.docx")

NAVY = colors.HexColor("#173B63")
TEAL = colors.HexColor("#197A7A")
GREEN = colors.HexColor("#3B7D4B")
INK = colors.HexColor("#27333F")
MUTED = colors.HexColor("#5E6B76")
PALE = colors.HexColor("#EEF3F6")
LINE = colors.HexColor("#CBD6DE")
WHITE = colors.white


def fonts():
    normal = Path(r"C:\Windows\Fonts\aptos.ttf")
    bold = Path(r"C:\Windows\Fonts\aptos-bold.ttf")
    if not normal.exists():
        normal, bold = Path(r"C:\Windows\Fonts\arial.ttf"), Path(r"C:\Windows\Fonts\arialbd.ttf")
    pdfmetrics.registerFont(TTFont("Doc", str(normal)))
    pdfmetrics.registerFont(TTFont("DocB", str(bold)))


fonts()
df = pd.read_excel(DATA)
sha = hashlib.sha256(DATA.read_bytes()).hexdigest()
numeric = df.select_dtypes(include="number")


def _font_path(bold=False):
    choices = [
        Path(r"C:\Windows\Fonts\aptos-bold.ttf" if bold else r"C:\Windows\Fonts\aptos.ttf"),
        Path(r"C:\Windows\Fonts\arialbd.ttf" if bold else r"C:\Windows\Fonts\arial.ttf"),
    ]
    return str(next(p for p in choices if p.exists()))


def _fit(draw, text, max_width, start, minimum=28, bold=False):
    for size in range(start, minimum - 1, -2):
        font = ImageFont.truetype(_font_path(bold), size)
        if draw.textbbox((0, 0), text, font=font)[2] <= max_width:
            return font
    return ImageFont.truetype(_font_path(bold), minimum)


def _center(draw, y, text, font, fill):
    box = draw.textbbox((0, 0), text, font=font)
    draw.text(((2550 - (box[2] - box[0])) / 2, y), text, font=font, fill=fill)


def create_cover():
    """Reproduce la portada institucional utilizada en la Unidad I."""
    if not TEMPLATE_DOCX.exists():
        raise FileNotFoundError(f"No se encontró la plantilla institucional: {TEMPLATE_DOCX}")
    with zipfile.ZipFile(TEMPLATE_DOCX) as zf:
        background = PILImage.open(zf.open("word/media/image4.jpg")).convert("RGB")
        background.load()
    img = background.resize((2550, 3300), PILImage.Resampling.LANCZOS)
    draw = ImageDraw.Draw(img, "RGBA")
    draw.rounded_rectangle((445, 985, 2105, 2580), radius=38, fill=(255, 255, 255, 242))

    _center(draw, 1065, "UNIDAD II", ImageFont.truetype(_font_path(True), 72), "#173B63")
    title = "EXPLORACIÓN Y DIAGNÓSTICO DEL DATASET"
    _center(draw, 1170, title, _fit(draw, title, 1500, 67, 42, True), "#173B63")
    _center(draw, 1360, "Clasificación automática y análisis morfológico",
            _fit(draw, "Clasificación automática y análisis morfológico", 1540, 52, 34, True), "#197A7A")
    _center(draw, 1430, "de variedades de frijol",
            ImageFont.truetype(_font_path(True), 48), "#197A7A")
    draw.line((700, 1535, 1850, 1535), fill="#C9D5DE", width=4)

    rows = [
        ("ASIGNATURA", "Extracción de Conocimiento en Bases de Datos"),
        ("ACTIVIDAD", "Evaluación 1 - Unidad II"),
        ("ESTUDIANTE", "Kevin Hernandez Trejo"),
        ("MATRÍCULA", "23300950"),
        ("GRUPO Y CARRERA", "10IDGS-G1"),
        ("DOCENTE", "Ing. Jose Luis Herrera Gallardo, MTI"),
        ("FECHA", "9 de noviembre de 2026"),
    ]
    label_font = ImageFont.truetype(_font_path(True), 33)
    value_font = ImageFont.truetype(_font_path(False), 38)
    y = 1630
    for label, value in rows:
        draw.text((625, y), label, font=label_font, fill="#173B63")
        draw.text((1035, y - 3), value, font=value_font, fill="#27333F")
        y += 117
    _center(draw, 2470, "Universidad Tecnológica de Tula-Tepeji",
            ImageFont.truetype(_font_path(False), 31), "#5E6B76")
    img.save(COVER, quality=96)


def charts():
    sns.set_theme(style="whitegrid", palette="colorblind")
    counts = df["Class"].value_counts()
    fig, ax = plt.subplots(figsize=(9, 4.8))
    sns.barplot(x=counts.index, y=counts.values, hue=counts.index, palette="viridis", legend=False, ax=ax)
    ax.set(title="Número de granos por variedad", xlabel="Variedad", ylabel="Registros")
    ax.tick_params(axis="x", rotation=25)
    for p in ax.patches:
        ax.annotate(f"{int(p.get_height()):,}", (p.get_x()+p.get_width()/2, p.get_height()), ha="center", va="bottom", fontsize=8)
    fig.tight_layout(); fig.savefig(CHARTS / "clases.png", dpi=190); plt.close(fig)

    fig, axes = plt.subplots(1, 3, figsize=(12, 4))
    for ax, col in zip(axes, ["Area", "Perimeter", "AspectRation"]):
        sns.boxplot(data=df, x=col, ax=ax, color="#66b3a6")
        ax.set_title(col)
    fig.suptitle("Valores atípicos por regla IQR", fontweight="bold")
    fig.tight_layout(); fig.savefig(CHARTS / "boxplots.png", dpi=190); plt.close(fig)

    fig, ax = plt.subplots(figsize=(9, 5.4))
    sns.scatterplot(data=df, x="MajorAxisLength", y="MinorAxisLength", hue="Class", s=13, alpha=.5, ax=ax)
    ax.set(title="Relación entre ejes por variedad", xlabel="Eje mayor (px)", ylabel="Eje menor (px)")
    ax.legend(title="Variedad", bbox_to_anchor=(1.02, 1), loc="upper left")
    fig.tight_layout(); fig.savefig(CHARTS / "dispersion.png", dpi=190); plt.close(fig)

    fig, ax = plt.subplots(figsize=(9.5, 7.2))
    sns.heatmap(numeric.corr(), cmap="vlag", center=0, vmin=-1, vmax=1, square=True, ax=ax, cbar_kws={"label": "Correlación"})
    ax.set_title("Matriz de correlación morfológica")
    fig.tight_layout(); fig.savefig(CHARTS / "correlacion.png", dpi=190); plt.close(fig)


create_cover()
charts()


styles = getSampleStyleSheet()
styles.add(ParagraphStyle("T", fontName="DocB", fontSize=18, leading=22, textColor=NAVY, spaceAfter=8, keepWithNext=True))
styles.add(ParagraphStyle("H1", fontName="DocB", fontSize=13.5, leading=17, textColor=NAVY, spaceBefore=5, spaceAfter=7, keepWithNext=True))
styles.add(ParagraphStyle("H2", fontName="DocB", fontSize=10.5, leading=13, textColor=TEAL, spaceBefore=5, spaceAfter=4, keepWithNext=True))
styles.add(ParagraphStyle("B", fontName="Doc", fontSize=9.1, leading=12.8, textColor=INK, alignment=TA_JUSTIFY, spaceAfter=6))
styles.add(ParagraphStyle("S", fontName="Doc", fontSize=7.7, leading=10, textColor=INK))
styles.add(ParagraphStyle("TH", fontName="DocB", fontSize=7.3, leading=8.5, textColor=WHITE))
styles.add(ParagraphStyle("TC", fontName="Doc", fontSize=6.9, leading=8.5, textColor=INK))
styles.add(ParagraphStyle("Ref", fontName="Doc", fontSize=8, leading=11, textColor=INK, leftIndent=14, firstLineIndent=-14, spaceAfter=5))


def P(text, style="B"):
    return Paragraph(text, styles[style])


def bullet(text):
    return Paragraph("• " + text, ParagraphStyle("bt", parent=styles["B"], leftIndent=12, firstLineIndent=-8, spaceAfter=3))


def tbl(rows, widths, repeat=1):
    data = []
    for i, row in enumerate(rows):
        st = "TH" if i == 0 else "TC"
        data.append([c if hasattr(c, "wrap") else P(str(c), st) for c in row])
    t = Table(data, colWidths=widths, repeatRows=repeat, hAlign="LEFT")
    cmds = [
        ("BACKGROUND", (0,0), (-1,0), NAVY), ("GRID", (0,0), (-1,-1), .45, LINE),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"), ("LEFTPADDING", (0,0), (-1,-1), 5),
        ("RIGHTPADDING", (0,0), (-1,-1), 5), ("TOPPADDING", (0,0), (-1,-1), 4),
        ("BOTTOMPADDING", (0,0), (-1,-1), 4),
    ]
    for i in range(2, len(rows), 2): cmds.append(("BACKGROUND", (0,i), (-1,i), colors.HexColor("#F5F7F9")))
    t.setStyle(TableStyle(cmds)); return t


class Doc(BaseDocTemplate):
    def __init__(self, path):
        super().__init__(path, pagesize=letter, leftMargin=1.7*cm, rightMargin=1.7*cm, topMargin=2.0*cm, bottomMargin=1.7*cm,
                         title="Diagnóstico técnico del Dry Bean Dataset", author="Kevin Hernandez Trejo")
        frame = Frame(self.leftMargin, self.bottomMargin, self.width, self.height, id="body")
        # Draw navigation after the page content so charts cannot cover it.
        self.addPageTemplates(PageTemplate(id="all", frames=frame, onPageEnd=header_footer))


def header_footer(canvas, doc):
    if doc.page == 1:
        canvas.saveState()
        canvas.drawImage(str(COVER), 0, 0, width=letter[0], height=letter[1], preserveAspectRatio=False, mask="auto")
        canvas.restoreState()
        return
    canvas.saveState(); canvas.setFillColor(NAVY); canvas.rect(0, letter[1]-1.05*cm, letter[0], 1.05*cm, fill=1, stroke=0)
    canvas.setFillColor(WHITE); canvas.setFont("DocB", 8.4); canvas.drawString(1.7*cm, letter[1]-.7*cm, "UNIDAD II | EXPLORACIÓN Y DIAGNÓSTICO")
    canvas.setFont("Doc", 8.2); canvas.drawRightString(letter[0]-1.7*cm, letter[1]-.7*cm, "Kevin Hernandez Trejo")
    canvas.setStrokeColor(TEAL); canvas.line(1.7*cm, 1.22*cm, letter[0]-1.7*cm, 1.22*cm)
    canvas.setFillColor(MUTED); canvas.setFont("Doc", 8); canvas.drawString(1.7*cm, .75*cm, "ECBD · Recursamiento 2026")
    canvas.drawRightString(letter[0]-1.7*cm, .75*cm, f"Página {doc.page}"); canvas.restoreState()


story = [Spacer(1, 23.5*cm), PageBreak()]

story += [P("Índice", "T")]
for line in ["1. Resumen ejecutivo", "2. Identificación y fuente", "3. Estructura y exploración", "4. Diccionario de datos", "5. Diagnóstico de calidad", "6. Estadística descriptiva", "7. Valores atípicos", "8. Visualizaciones", "9. Propuestas analíticas", "10. Conclusiones", "11. Referencias"]: story.append(P(line, "B"))
story.append(PageBreak())

story += [P("1. Resumen ejecutivo", "T"), P("El Dry Bean Dataset contiene 13,611 granos descritos por 16 mediciones morfológicas y una etiqueta de siete variedades. La revisión del archivo crudo encontró 100% de completitud, tipos coherentes, ausencia de valores negativos o proporciones fuera de rango y 68 duplicados exactos (0.500%), todos asociados a HOROZ. Los valores extremos detectados por IQR son plausibles y se conservan. El conjunto es adecuado para continuar con clasificación, regresión y clustering, siempre que posteriormente se controle la duplicación, el desbalance y la fuga de información."),
         P("Hallazgos principales", "H1")]
for x in ["13,611 filas y 17 columnas.", "16 variables numéricas y una variable nominal, Class.", "0 valores faltantes y 68 duplicados exactos.", "Siete clases con desbalance: DERMASON 3,546 y BOMBAY 522.", "El SHA-256 del original es " + sha + "."]: story.append(bullet(x))
story.append(PageBreak())

story += [P("2. Identificación y fuente de los datos", "T")]
ident = [["Elemento","Resultado"],["Proyecto","Clasificación automática y análisis morfológico de variedades de frijol"],["Dataset","Dry Bean Dataset"],["Fuente","UCI Machine Learning Repository, ID 602"],["Formato usado","Microsoft Excel (.xlsx)"],["Dimensiones","13,611 registros × 17 variables"],["Origen","Mediciones biométricas/morfológicas generadas por máquina tras segmentar imágenes de granos"],["Estructura","Estructurada: tabla con esquema fijo de filas y columnas"],["Licencia","Creative Commons Attribution 4.0"]]
story.append(tbl(ident,[4.0*cm,12.0*cm])); story += [Spacer(1,8), P("Cada fila representa un grano fotografiado. Las variables describen tamaño, ejes, proporciones y factores de forma; Class registra la variedad. Aunque el origen inmediato son imágenes, el archivo entregado ya es una tabla estructurada de características extraídas por visión por computadora."), PageBreak()]

story += [P("3. Estructura y exploración con Pandas", "T")]
cmds = [["Instrucción","Resultado e interpretación"],["df.head()","Muestra cinco observaciones y confirma el esquema: 16 mediciones numéricas y Class."],["df.shape","Devuelve (13611, 17): 13,611 granos y 17 columnas."],["df.columns","Lista los nombres originales; AspectRation y roundness requieren normalización posterior de nomenclatura."],["df.info()","Todas las columnas tienen 13,611 valores no nulos; 2 enteras, 14 float y 1 texto."],["df.dtypes","Confirma tipos adecuados; no hay números almacenados como texto."],["df.describe()","Resume conteo, media, dispersión, cuartiles y extremos; revela escalas muy diferentes."]]
story.append(tbl(cmds,[3.2*cm,12.8*cm])); story += [Spacer(1,8), P("La exploración se realizó sobre el Excel original mediante pd.read_excel(). El DataFrame reside en memoria; no se ejecutaron drop_duplicates(), fillna(), rename() ni operaciones de escritura sobre data/raw/."), PageBreak()]

descs = {
"Area":"Área interna del grano","Perimeter":"Longitud del contorno","MajorAxisLength":"Eje mayor","MinorAxisLength":"Eje menor","AspectRation":"Razón eje mayor/eje menor","Eccentricity":"Excentricidad de elipse equivalente","ConvexArea":"Área de envolvente convexa","EquivDiameter":"Diámetro de círculo equivalente","Extent":"Área respecto a caja delimitadora","Solidity":"Area/ConvexArea","roundness":"Redondez 4πA/P²","Compactness":"EquivDiameter/eje mayor","ShapeFactor1":"Factor morfológico 1","ShapeFactor2":"Factor morfológico 2","ShapeFactor3":"Factor morfológico 3","ShapeFactor4":"Factor morfológico 4","Class":"Variedad registrada"}
units = {"Area":"px²","ConvexArea":"px²","Perimeter":"px","MajorAxisLength":"px","MinorAxisLength":"px","EquivDiameter":"px","Class":"Categoría"}
story += [P("4. Diccionario y clasificación de variables", "T")]
rows = [["Variable","Descripción","Python","Tipo / clase","Unidad","Utilidad"]]
for c in df.columns:
    qual = c == "Class"; cls = "Cualitativa / nominal" if qual else ("Cuantitativa / discreta" if c in ["Area","ConvexArea"] else "Cuantitativa / continua")
    util = "Objetivo de clasificación" if qual else ("Objetivo de regresión / tamaño" if c=="Area" else "Predictor morfológico")
    rows.append([c,descs[c],str(df[c].dtype),cls,units.get(c,"Adimensional"),util])
story.append(tbl(rows,[2.5*cm,4.0*cm,1.8*cm,3.2*cm,1.7*cm,3.0*cm])); story.append(PageBreak())

story += [P("5. Diagnóstico de calidad", "T"), P("5.1 Completitud", "H1"), P("df.isnull().sum() reporta cero faltantes en las 17 columnas. La completitud es 100%; no se propone imputación para este archivo."), P("5.2 Duplicados", "H1"), P("df.duplicated().sum() identifica 68 duplicados exactos, equivalentes al 0.500% del conjunto. Las 136 filas involucradas en pares repetidos pertenecen a HOROZ. La causa puede ser repetición durante captura o consolidación. En una copia procesada se conservará una sola observación de cada duplicado antes de separar entrenamiento y prueba."), P("5.3 Inconsistencias", "H1")]
quality = [["Control","Incidencias"],["Valores numéricos negativos","0"],["Eccentricity fuera de [0,1)","0"],["Extent, Solidity, roundness o Compactness fuera de (0,1]","0"],["Clases vacías, con espacios o desconocidas","0"],["Nombres no estandarizados","AspectRation y roundness"]]
story.append(tbl(quality,[11.8*cm,4.2*cm])); story += [Spacer(1,8), P("No se modificó ningún valor. Los nombres se documentan ahora y se normalizarán únicamente en una copia procesada."), PageBreak()]

story += [P("6. Análisis estadístico inicial", "T")]
sel=["Area","Perimeter","AspectRation"]; st=df[sel].agg(["mean","median","min","max","std"]).T
rows=[["Variable","Media","Mediana","Mínimo","Máximo","Desv. estándar"]]
for c in sel: rows.append([c,f"{st.loc[c,'mean']:,.3f}",f"{st.loc[c,'median']:,.3f}",f"{st.loc[c,'min']:,.3f}",f"{st.loc[c,'max']:,.3f}",f"{st.loc[c,'std']:,.3f}"])
story.append(tbl(rows,[3.0*cm,2.6*cm,2.6*cm,2.6*cm,2.6*cm,2.6*cm])); story += [Spacer(1,8), P("Area y Perimeter presentan medias superiores a sus medianas, señal de asimetría hacia granos grandes. AspectRation varía entre 1.025 y 2.430, diferenciando formas casi redondas de granos alargados. Las variables resumen tamaño, contorno y proporción, tres dimensiones centrales del proyecto."), P("Distribución de clases", "H1")]
classrows=[["Clase","Registros","Porcentaje"]]+[[c,f"{n:,}",f"{n/len(df)*100:.2f}%"] for c,n in df["Class"].value_counts().items()]
story.append(tbl(classrows,[6*cm,5*cm,5*cm])); story.append(PageBreak())

story += [P("7. Detección inicial de valores atípicos", "T"), Image(str(CHARTS/"boxplots.png"), width=16.2*cm, height=5.4*cm)]
orows=[["Variable","Límite inferior","Límite superior","Casos IQR","Porcentaje"]]
for c in sel:
    q1,q3=df[c].quantile([.25,.75]); i=q3-q1; lo,hi=q1-1.5*i,q3+1.5*i; n=int(((df[c]<lo)|(df[c]>hi)).sum()); orows.append([c,f"{lo:,.3f}",f"{hi:,.3f}",f"{n:,}",f"{n/len(df)*100:.2f}%"])
story += [Spacer(1,6), tbl(orows,[3.2*cm,3.4*cm,3.4*cm,3.0*cm,3.0*cm]), Spacer(1,7), P("Los boxplots señalan 551 casos en Area, 500 en Perimeter y 473 en AspectRation. No se consideran errores por defecto: pertenecen a un dataset multiclase, son positivos y respetan rangos físicos. Se conservarán y se estudiarán por variedad antes de aplicar transformaciones robustas."), PageBreak()]

story += [P("8. Visualización e interpretación", "T"), Image(str(CHARTS/"clases.png"), width=15.8*cm, height=8.4*cm), P("Figura 1. DERMASON es la clase más numerosa y BOMBAY la minoritaria. La diferencia exige estratificación y métricas como macro F1 para no ocultar el desempeño de clases pequeñas."), PageBreak(), P("8. Visualización e interpretación", "T"), Image(str(CHARTS/"dispersion.png"), width=15.8*cm, height=9.5*cm), P("Figura 2. Los ejes mayor y menor aumentan juntos. Algunas variedades ocupan regiones distintas por tamaño, pero hay solapamientos que justifican combinar medidas de tamaño con descriptores de forma."), PageBreak(), P("8. Visualización e interpretación", "T"), Image(str(CHARTS/"correlacion.png"), width=14.7*cm, height=11.2*cm), P("Figura 3. Area, ConvexArea y EquivDiameter tienen correlación elevada por construcción geométrica. Para una regresión honesta de Area se excluye EquivDiameter y se revisa ConvexArea para prevenir fuga de información."), PageBreak()]

story += [P("9. Preparación para análisis posteriores", "T")]
proposals=[["Tarea","Objetivo / variables","Justificación y control"],["Regresión","Objetivo: Area. Entradas: Perimeter, ejes, proporciones y factores de forma.","Estimar tamaño. Excluir EquivDiameter y revisar ConvexArea por dependencia directa."],["Clasificación","Objetivo: Class. Siete variedades; entradas: 16 medidas numéricas.","Responde al proyecto de clasificación automática. Usar estratificación y macro F1."],["Agrupamiento","Sin etiqueta; tamaño, ejes, AspectRation, Eccentricity, Extent, Solidity, redondez, compacidad y factores.","Buscar perfiles naturales. Deduplicar y estandarizar antes de usar distancias; contrastar después con Class."]]
story.append(tbl(proposals,[3.0*cm,6.4*cm,6.6*cm])); story += [Spacer(1,10), P("Estas propuestas mantienen la relación con Unidad I: explicar y distinguir variedades mediante morfología, estimar una propiedad continua y descubrir estructuras sin usar etiquetas."), PageBreak()]

story += [P("10. Conclusión del diagnóstico", "T")]
answers=[("1. ¿Qué contiene?","13,611 granos, 16 medidas morfológicas y Class."),("2. ¿Calidad general?","Alta: 100% de completitud, tipos coherentes y rangos plausibles."),("3. ¿Problemas?","68 duplicados, desbalance, nomenclatura no uniforme y valores extremos por IQR."),("4. ¿Qué requiere tratamiento?","Duplicados en copia procesada, nombres, escalas y variables derivadas para regresión."),("5. ¿Faltantes?","No."),("6. ¿Duplicados?","Sí: 68, todos vinculados con HOROZ."),("7. ¿Atípicos?","Sí según IQR, pero plausibles; no se eliminan."),("8. ¿Transformaciones?","Deduplicación, normalización de nombres, escalado cuando corresponda y separación de objetivos."),("9. ¿Adecuado?","Sí, con controles de fuga, desbalance y evaluación por clase."),("10. ¿Conocimiento futuro?","Rasgos que separan variedades, errores entre clases, estimación de tamaño y grupos naturales.")]
for q,a in answers: story.append(P(f"<b>{q}</b> {a}"))
story += [Spacer(1,8), P("Integridad del original", "H1"), P("La huella SHA-256 se verificó antes y después del análisis: <font name='DocB'>"+sha+"</font>. El archivo original permaneció intacto en data/raw/."), PageBreak()]

story += [P("Fuentes de información", "T"), P("Koklu, M., & Özkan, I. A. (2020). Multiclass classification of dry beans using computer vision and machine learning techniques. <i>Computers and Electronics in Agriculture, 174</i>, 105507. https://doi.org/10.1016/j.compag.2020.105507", "Ref"), P("UCI Machine Learning Repository. (2020). <i>Dry Bean</i> [Data set]. https://doi.org/10.24432/C50S4B", "Ref"), Spacer(1,12), P("Repositorio actualizado", "H1"), P("https://github.com/Kaysito/REC_ECBD_2026_Hernandez_Trejo_Kevin"), P("El notebook ejecutable se almacena en notebooks/ y este informe en docs/, conforme a la estructura solicitada.")]

OUT.parent.mkdir(parents=True, exist_ok=True)
Doc(str(OUT)).build(story)
assert hashlib.sha256(DATA.read_bytes()).hexdigest() == sha
print(OUT)
