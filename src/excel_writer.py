import pandas as pd
from openpyxl.styles import Alignment, Font

def write_qna_excel(result, output_path):

    if hasattr(result, "model_dump"):
        data = result.model_dump()

    elif isinstance(result, dict):
        data = result

    else:
        raise TypeError(
            "Invalid QnA result format."
        )

    languages = {
        "English": data.get("english", []),
        "Hindi": data.get("hindi", []),
        "Marathi": data.get("marathi", [])
    }

    with pd.ExcelWriter(
        output_path,
        engine="openpyxl"
    ) as writer:

        for sheet_name, items in languages.items():

            rows = []

            for item in items:

                if isinstance(item, dict):

                    question = item.get(
                        "question",
                        ""
                    )

                    answer = item.get(
                        "answer",
                        ""
                    )

                else:

                    question = getattr(
                        item,
                        "question",
                        ""
                    )

                    answer = getattr(
                        item,
                        "answer",
                        ""
                    )

                if question and answer:

                    rows.append(
                        {
                            "Questions": question,
                            "Answers": answer
                        }
                    )

            df = pd.DataFrame(
                rows,
                columns=[
                    "Questions",
                    "Answers"
                ]
            )

            df.to_excel(
                writer,
                sheet_name=sheet_name,
                index=False
            )

            worksheet = writer.sheets[
                sheet_name
            ]

            worksheet.freeze_panes = "A2"

            worksheet.auto_filter.ref = (
                worksheet.dimensions
            )

            for cell in worksheet[1]:

                cell.font = Font(
                    bold=True
                )

                cell.alignment = Alignment(
                    horizontal="center",
                    vertical="center"
                )

            for row in worksheet.iter_rows():

                for cell in row:

                    cell.alignment = Alignment(
                        vertical="top",
                        wrap_text=True
                    )

            worksheet.column_dimensions[
                "A"
            ].width = 50

            worksheet.column_dimensions[
                "B"
            ].width = 90

            for row_number in range(
                2,
                worksheet.max_row + 1
            ):

                worksheet.row_dimensions[
                    row_number
                ].height = 70