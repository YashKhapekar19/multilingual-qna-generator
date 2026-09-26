# Multilingual Question-Answer (QnA) Generation

Python + Streamlit system for generating context-aware Question-Answer pairs from PDF, DOCX, and TXT documents in English, Hindi, and Marathi.

## Features
- PDF, DOCX, TXT input
- Context-grounded QnA generation
- English, Hindi, Marathi outputs
- Single `QnA.xlsx` workbook
- Sheets: English, Hindi, Marathi
- Columns: Questions, Answers
- Streamlit UI
- Configurable QnA count
- Long-document chunking and deduplication

## Setup
```bash
py -m pip install -r requirements.txt
```
Copy `.env.example` to `.env` and add your Gemini API key.

CLI:
```bash
py generate_qna.py input/sample.txt --output output/QnA.xlsx --num-qna 10
```

UI:
```bash
streamlit run app.py
```

Never commit `.env` or API keys.
