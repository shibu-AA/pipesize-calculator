from io import BytesIO

from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

pdfmetrics.registerFont(TTFont("IPAexGothic", "fonts/ipaexg.ttf"))


def create_pdf(result):
    buffer = BytesIO()

    doc = SimpleDocTemplate(buffer)
    styles = getSampleStyleSheet()

    styles["Heading1"].fontName = "IPAexGothic"
    styles["Normal"].fontName = "IPAexGothic"

    story = [
        Paragraph("配管サイズ計算結果", styles["Heading1"]),
        Paragraph(f"最大流量の実流量：{result['actual_flow_rate']}", styles["Normal"]),
        Paragraph(
            f"最大流量の推奨配管サイズ：{result['recommended_pipe_name_max']}",
            styles["Normal"],
        ),
        Paragraph(
            f"最大流量×係数の実流量：{result['design_flow_rate']}", styles["Normal"]
        ),
        Paragraph(
            f"最大流量×係数の推奨配管サイズ：{result['recommended_pipe_name_design']}",
            styles["Normal"],
        ),
        Paragraph(f"最適配管の内径：{result['inner_diameter']}", styles["Normal"]),
        Paragraph(f"最適配管の摩擦係数：{result['friction']}", styles["Normal"]),
        Paragraph(f"流体の密度：{result['fluid_density']}", styles["Normal"]),
        Paragraph(
            f"継ぎ手の抵抗相当長さ(n)：{result['equivalent_length_factor']}",
            styles["Normal"],
        ),
        Paragraph(
            f"相当長さ(Ln)：{result['equivalent_pipe_length']}", styles["Normal"]
        ),
        Paragraph(f"流速：{result['velocity']}", styles["Normal"]),
        Paragraph(f"最適配管の圧力損失：{result['delta_P']}", styles["Normal"]),
        Paragraph(f"最適配管サイズ：{result['optimal_pipe_name']}", styles["Normal"]),
    ]

    doc.build(story)

    buffer.seek(0)
    return buffer
