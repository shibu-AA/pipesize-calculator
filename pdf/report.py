from datetime import datetime
from io import BytesIO
from zoneinfo import ZoneInfo

import pandas as pd
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    Image,
    Indenter,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

pdfmetrics.registerFont(TTFont("IPAexGothic", "fonts/ipaexg.ttf"))


KGF_PER_MPA = 10.197
MPA_PER_KGF = 0.098067


def mpa_to_kgf_cm2(pressure_mpa: float) -> float:
    """MPa → kgf/cm²"""
    return round(pressure_mpa * KGF_PER_MPA, 3)


def kgf_cm2_to_mpa(pressure_kgf_cm2: float) -> float:
    """kgf/cm² → MPa"""
    return round(pressure_kgf_cm2 * MPA_PER_KGF, 3)


def create_pdf(gas_name, input_data, result):
    buffer = BytesIO()

    doc = SimpleDocTemplate(buffer)
    styles = getSampleStyleSheet()

    styles["Heading1"].fontName = "IPAexGothic"
    styles["Heading1"].alignment = TA_CENTER
    styles["Normal"].fontName = "IPAexGothic"

    today = datetime.now(ZoneInfo("Asia/Tokyo"))

    story = [
        Paragraph(
            f"<para alignment='right'>作成日：{today:%Y/%m/%d}</para>",
            styles["Normal"],
        )
    ]

    story.append(Spacer(1, 10))

    left_rows = [
        ("流体名", gas_name),
        ("最大流量", f"{input_data['max_flow_rate']:.1f} L/min"),
        (
            "入口圧力",
            f"{input_data['inlet_pressure']:.2f} MPaG  ({mpa_to_kgf_cm2(input_data['inlet_pressure'])} kgf/cm²G)",
        ),
        (
            "出口圧力",
            f"{input_data['outlet_pressure']:.2f} MPaG  ({mpa_to_kgf_cm2(input_data['outlet_pressure'])} kgf/cm²G)",
        ),
        ("基準温度", f"{input_data['temperature']:.1f} ℃"),
        ("許容流速", f"{input_data['velocity_limit']:.2f} m/s"),
        ("配管規格", input_data["schedule"]),
        ("管の長さ", f"{input_data['pipe_length']:.1f} m"),
        ("稼働率", f"{input_data['coefficient']:.1f} %"),
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
        ("最大流量算定口径", result["recommended_pipe_name_max"]),
        ("実流量算定口径", result["recommended_pipe_name_design"]),
        ("圧損考慮採用口径", result["optimal_pipe_name"]),
        ("配管肉圧", f"{pipe_thickness} mm"),
        ("摩擦係数  f", result["friction"]),
        (
            "実効配管長  L+Ln",
            f"{input_data['pipe_length'] + result['equivalent_pipe_length']} m",
        ),
        ("流体の密度  ρ", f"{result['fluid_density']:.2f} kg/m³"),
        ("流速  v", f"{result['velocity']:.2f} m/s"),
        ("配管の内径  D", f"{result['inner_diameter']} mm"),
        (
            "配管の圧力損失  ΔP",
            f"{kgf_cm2_to_mpa(result['delta_P'])} MPa  ({result['delta_P']:.2f} kgf/cm²)",
        ),
    ]

    def draw_logo(canvas, doc):
        logo_width = 135
        logo_height = 15

        page_width, page_height = doc.pagesize

        canvas.drawImage(
            "assets/logo.png",
            x=(page_width - logo_width) / 2,
            y=20,
            width=logo_width,
            height=logo_height,
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

    story.append(Paragraph("配管内径の算出", styles["Heading1"]))
    story.append(Spacer(1, 20))
    story.append(table)
    story.append(Spacer(1, 20))

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

    story.append(Spacer(1, 40))

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
