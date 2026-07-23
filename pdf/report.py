from io import BytesIO

from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Table,
    TableStyle,
    Spacer,
    Image,
    Indenter,
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_CENTER

import pandas as pd

from datetime import datetime

pdfmetrics.registerFont(TTFont("IPAexGothic", "fonts/ipaexg.ttf"))


def create_pdf(gas_name, input_data, result):
    buffer = BytesIO()

    doc = SimpleDocTemplate(buffer)
    styles = getSampleStyleSheet()

    styles["Heading1"].fontName = "IPAexGothic"
    styles["Heading1"].alignment = TA_CENTER
    styles["Normal"].fontName = "IPAexGothic"

    left_rows = [
        ("流体名", gas_name),
        ("流量", str(input_data["max_flow_rate"]) + "  (L/min)"),
        ("入口圧力", str(input_data["inlet_pressure"]) + "  (MPaG)"),
        ("出力圧力", str(input_data["outlet_pressure"]) + "  (MPaG)"),
        ("基準温度", str(input_data["temperature"]) + "  (℃)"),
        ("許容流速", str(input_data["velocity_limit"]) + "  (m/s)"),
        ("配管規格", input_data["schedule"]),
        ("管の長さ", str(input_data["pipe_length"]) + "  (m)"),
        ("稼働率", str(input_data["coefficient"]) + "  (%)"),
    ]

    right_rows = [
        ("90°エルボ(2･1/2まで)", input_data["fitting_counts"][0]),
        ('90°エルボ(3"～6")', input_data["fitting_counts"][1]),
        ("90°ベンド", input_data["fitting_counts"][2]),
        ("45°エルボ", input_data["fitting_counts"][3]),
        ("チーズ", input_data["fitting_counts"][4]),
        ("弁(2･1/2まで)", input_data["fitting_counts"][5]),
        ('弁(3"～6")', input_data["fitting_counts"][6]),
    ]

    pipe_table = pd.read_csv(f"data/pipe/{input_data['schedule']}.csv")
    pipe_thickness = pipe_table.loc[
        pipe_table["呼び径"] == result["optimal_pipe_name"], "肉圧(mm)"
    ].iloc[0]

    result_rows = [
        ("推奨配管サイズ", result["recommended_pipe_name_design"]),
        ("最適配管サイズ", result["optimal_pipe_name"]),
        ("配管肉圧", str(pipe_thickness) + "  (mm)"),
        ("摩擦係数  f", result["friction"]),
        (
            "実効配管長  L+Ln",
            str(input_data["pipe_length"] + result["equivalent_pipe_length"]) + "  (m)",
        ),
        ("流体の密度  ρ", str(f"{result['fluid_density']:.4g}") + "  (kg/m³)"),
        ("流速  v", str(f"{result['velocity']:.4g}") + "  (m/s)"),
        ("配管の内径  D", str(result["inner_diameter"]) + "  (mm)"),
        ("配管の圧力損失  ΔP", str(f"{result['delta_P']:.4g}") + "  kgf/cm³"),
    ]

    def draw_logo(canvas, doc):
        canvas.drawImage(
            "assets/logo.png",
            x=40,
            y=780,
            width=135,
            height=15,
            mask="auto",
        )

    table_data = []
    for i in range(max(len(left_rows), len(right_rows))):
        left = left_rows[i] if i < len(left_rows) else ("", "")
        right = right_rows[i] if i < len(right_rows) else ("", "")

        table_data.append([left[0], str(left[1]), right[0], str(right[1])])

    table = Table(table_data, colWidths=[60, 180, 120, 20])
    table.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (-1, -1), "IPAexGothic"),
            ]
        )
    )

    story = [
        Paragraph("配管内径の算出", styles["Heading1"]),
        table,
        Spacer(1, 12),
    ]

    result_table = Table(
        result_rows,
        colWidths=[150, 150],
        hAlign="LEFT",
    )

    result_table.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (-1, -1), "IPAexGothic"),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )

    story.append(Indenter(left=30))
    story.append(result_table)
    story.append(Indenter(left=-30))
    story.append(Spacer(1, 6))
    story.append(
        Image(
            "assets/pressure_loss_formula.png",
            width=300,
            height=45,
        )
    )
    story.append(Spacer(1, 12))
    judge_style = ParagraphStyle(
        "ResultStyle",
        parent=styles["Normal"],
        fontName="IPAexGothic",
        fontSize=16,
    )
    story.append(Indenter(left=90))
    story.append(
        Paragraph(
            "出口圧力 &lt; 入口圧力 - ΔP"
            "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"
            "<font color='green'><b>合格</b></font>",
            judge_style,
        )
    )
    story.append(Indenter(left=-90))

    story.append(Spacer(1, 80))

    story.append(
        Paragraph(
            f"<para alignment='right'>作成日：{datetime.today():%Y/%m/%d}</para>",
            styles["Normal"],
        )
    )

    story.append(Spacer(1, 10))

    approval_table = Table(
        [
            ["作成", "承認"],
            ["", ""],
        ],
        colWidths=[80, 80],
        rowHeights=[20, 80],
        hAlign="RIGHT",
    )

    approval_table.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (-1, -1), "IPAexGothic"),
                ("GRID", (0, 0), (-1, -1), 0.8, "black"),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ]
        )
    )

    story.append(approval_table)

    doc.build(story, onFirstPage=draw_logo)

    buffer.seek(0)
    return buffer
