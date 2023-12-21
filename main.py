import argparse
import os
from openai_gpt_client import generate_repair_proposal, analyze_image_with_gpt4
from image_preprocessor import preprocess_image
from pdf_text_extractor import extract_text_from_pdf

def main():
    parser = argparse.ArgumentParser(description="Process text and images with GPT-4.")
    parser.add_argument('--text', type=str, help='Text to process with GPT-4.')
    parser.add_argument('--image', type=str, help='Path to the image file for GPT-4 analysis.')
    parser.add_argument('--pdf', type=str, help='Path to the PDF file for text extraction.')
    args = parser.parse_args()

    api_key = os.getenv("OPENAI_API_KEY")  # Ensure your API key is set in environment variables

    if not api_key:
        print("OpenAI API key not found. Please set your API key as an environment variable.")
        return

    if args.text:
        print("Generating repair proposal based on text...")
        print(generate_repair_proposal(args.text, api_key))

    if args.image:
        print("Analyzing image with GPT-4 Vision...")
        preprocessed_image = preprocess_image(args.image)
        print(analyze_image_with_gpt4(preprocessed_image, "What’s in this image?", api_key))

    if args.pdf:
        print("Extracting text from PDF and processing...")
        pdf_text = extract_text_from_pdf(args.pdf)
        print(generate_repair_proposal(pdf_text, api_key))

if __name__ == "__main__":
    main()
