from pathlib import Path
import argparse
from dotenv import load_dotenv
from src.document_loader import load_document
from src.qna_generator import generate_multilingual_qna
from src.excel_writer import write_qna_excel

def main():
    load_dotenv()
    parser = argparse.ArgumentParser(description='Generate multilingual QnA Excel.')
    parser.add_argument('input_file', type=Path)
    parser.add_argument('--output', type=Path, default=Path('output/QnA.xlsx'))
    parser.add_argument('--num-qna', type=int, default=10)
    parser.add_argument('--model', default=None)
    args = parser.parse_args()
    if args.num_qna < 1:
        raise SystemExit('--num-qna must be at least 1.')
    text = load_document(args.input_file)
    result = generate_multilingual_qna(text, args.num_qna, args.model)
    output = write_qna_excel(result, args.output)
    print(f'Created: {output}')
    for language, rows in result.items():
        print(f'{language}: {len(rows)} QnA pairs')

if __name__ == '__main__':
    main()
