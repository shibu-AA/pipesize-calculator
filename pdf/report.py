from io import BytesIO

from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

pdfmetrics.registerFont(TTFont("IPAexGothic", "fonts/ipaexg.ttf"))


def create_pdf(input_data, result):
    buffer = BytesIO()

    doc = SimpleDocTemplate(buffer)
    styles = getSampleStyleSheet()

    styles["Heading1"].fontName = "IPAexGothic"
    styles["Normal"].fontName = "IPAexGothic"

    rows = [
        ("気体の分子量", input_data["molecular_weight"]),
        ("流量", input_data["max_flow_rate"]),
        ("入口圧力", input_data["inlet_pressure"]),
        ("出力圧力", input_data["outlet_pressure"]),
        ("基準温度", input_data["temperature"]),
        ("許容流速", input_data["velocity_limit"]),
        ("配管規格", input_data["schedule"]),
        ("管の長さ", input_data["pipe_length"]),
        ("係数", input_data["coefficient"]),
        ("90°エルボ(2･1/2まで)", input_data["fitting_counts"][0]),
        ('90°エルボ(3"～6")', input_data["fitting_counts"][1]),
        ("90°ベンド", input_data["fitting_counts"][2]),
        ("45°エルボ", input_data["fitting_counts"][3]),
        ("チーズ", input_data["fitting_counts"][4]),
        ("弁(2･1/2まで)", input_data["fitting_counts"][5]),
        ('弁(3"～6")', input_data["fitting_counts"][6]),
        ("最大流量の実流量", result["actual_flow_rate"]),
        ("最大流量の推奨配管サイズ", result["recommended_pipe_name_max"]),
        ("最大流量×係数の実流量", result["design_flow_rate"]),
        ("最大流量×係数の推奨配管サイズ", result["recommended_pipe_name_design"]),
        ("最適配管の内径", result["inner_diameter"]),
        ("最適配管の摩擦係数", result["friction"]),
        ("流体の密度", result["fluid_density"]),
        ("継ぎ手の抵抗相当長さ(n)", result["equivalent_length_factor"]),
        ("相当長さ(Ln)", result["equivalent_pipe_length"]),
        ("流速", result["velocity"]),
        ("最適配管の圧力損失", result["delta_P"]),
        ("最適配管サイズ", result["optimal_pipe_name"]),
    ]

    story = [Paragraph("配管サイズ計算結果", styles["Heading1"])]

    for label, value in rows:
        story.append(Paragraph(f"{label}：{value}", styles["Normal"]))

    doc.build(story)

    buffer.seek(0)
    return buffer
