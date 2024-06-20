import os
import fitz  # PyMuPDF
import argparse


def convert_pdf_to_text(pdf_path, output_path):
    """
    Convert a single PDF file to a text file.
    """
    try:
        # Open the PDF file
        document = fitz.open(pdf_path)

        # Extract text from each page
        text = ""
        for page_num in range(document.page_count):
            page = document.load_page(page_num)
            text += page.get_text()

        # Save the text to a file
        with open(output_path, "w", encoding="utf-8") as text_file:
            text_file.write(text)

        print(f"Converted {pdf_path} to {output_path}")
    except Exception as e:
        print(f"Error converting {pdf_path}: {e}")


def convert_pdfs_in_directory(input_dir, output_dir):
    """
    Convert all PDF files in a directory to text files.
    """
    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Process each PDF file in the input directory
    for file_name in os.listdir(input_dir):
        if file_name.lower().endswith(".pdf"):
            pdf_path = os.path.join(input_dir, file_name)
            text_file_name = os.path.splitext(file_name)[0] + ".txt"
            output_path = os.path.join(output_dir, text_file_name)
            convert_pdf_to_text(pdf_path, output_path)


if __name__ == "__main__":
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Convert PDF files to text files.")
    parser.add_argument(
        "--input_dir",
        type=str,
        required=True,
        help="Directory containing PDF files to convert.",
    )
    parser.add_argument(
        "--output_dir",
        type=str,
        required=True,
        help="Directory to save the converted text files.",
    )

    # Parse arguments
    args = parser.parse_args()

    # Convert all PDFs in the input directory to text files in the output directory
    convert_pdfs_in_directory(args.input_dir, args.output_dir)
