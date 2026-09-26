from pathlib import Path
import tempfile

import pandas as pd
import streamlit as st
from dotenv import load_dotenv

from src.document_loader import load_document
from src.qna_generator import generate_multilingual_qna
from src.excel_writer import write_qna_excel

load_dotenv()

st.set_page_config(
    page_title="Multilingual QnA Generator",
    page_icon="📚"
)

st.title("📚 Multilingual QnA Generator")
st.caption(
    "Generate context-aware QnA pairs in English, Hindi, and Marathi."
)

uploaded = st.file_uploader(
    "Upload a document",
    type=["pdf", "docx", "txt"]
)

num_qna = st.number_input(
    "Number of QnA pairs per language",
    min_value=1,
    max_value=50,
    value=10,
    step=1
)

if st.button(
    "Generate QnA",
    type="primary",
    disabled=uploaded is None
):

    suffix = Path(uploaded.name).suffix.lower()

    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=suffix
    ) as tmp:
        tmp.write(uploaded.getbuffer())
        temp_path = Path(tmp.name)

    try:

        with st.spinner("Reading document..."):
            text = load_document(temp_path)

    finally:

        temp_path.unlink(missing_ok=True)

    if not text.strip():
        st.error("Could not extract any text from the uploaded document.")
        st.stop()

    st.success(
        f"Extracted {len(text):,} characters."
    )

    try:

        with st.spinner(
            "Generating multilingual QnA..."
        ):
            result = generate_multilingual_qna(
                text,
                int(num_qna)
            )

    except Exception as e:

        st.error(
            f"QnA generation failed: {e}"
        )
        st.stop()

    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".xlsx"
    ) as tmp:

        output_path = Path(tmp.name)

    try:

        write_qna_excel(
            result,
            output_path
        )

        data = output_path.read_bytes()

    except Exception as e:

        st.error(
            f"Excel file creation failed: {e}"
        )
        st.stop()

    finally:

        output_path.unlink(missing_ok=True)

    st.success(
        "QnA generation completed."
    )

    tabs = st.tabs(
        ["English", "Hindi", "Marathi"]
    )

    result_data = result.model_dump()

    for tab, language in zip(
        tabs,
        ["English", "Hindi", "Marathi"]
    ):

        with tab:

            language_key = language.lower()

            items = result_data.get(
                language_key,
                []
            )

            rows = []

            for item in items:

                rows.append(
                    {
                        "Questions": item.get(
                            "question",
                            ""
                        ),
                        "Answers": item.get(
                            "answer",
                            ""
                        )
                    }
                )

            df = pd.DataFrame(
                rows,
                columns=[
                    "Questions",
                    "Answers"
                ]
            )

            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True
            )

    st.download_button(
        "⬇️ Download QnA.xlsx",
        data=data,
        file_name="QnA.xlsx",
        mime=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        )
    )