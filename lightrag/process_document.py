import os
import argparse
import glob
import io
import math
from dotenv import load_dotenv
import tiktoken # Add tiktoken import back
import PyPDF2 # For splitting PDF
import requests # For Upstage API call
import shutil # For temp directory cleanup
import time # For potential retries or delays

# Load environment variables 
load_dotenv()
UPSTAGE_API_KEY = os.getenv("UPSTAGE_API_KEY")

# --- Text Chunking Function (Add back) --- 
def chunk_text(text: str, chunk_size: int = 500, chunk_overlap: int = 50, model_name: str = "cl100k_base") -> list[str]:
    """Splits text into chunks with overlap based on token count."""
    if not text:
        return []
    try:
        encoding = tiktoken.get_encoding(model_name)
    except Exception:
        encoding = tiktoken.get_encoding("cl100k_base")
    tokens = encoding.encode(text)
    total_tokens = len(tokens)
    chunks = []
    start_idx = 0
    while start_idx < total_tokens:
        end_idx = min(start_idx + chunk_size, total_tokens)
        chunk_tokens = tokens[start_idx:end_idx]
        if not chunk_tokens:
             if start_idx >= total_tokens:
                  break 
             else:
                  start_idx = end_idx 
                  continue 
        chunk_text = encoding.decode(chunk_tokens)
        chunks.append(chunk_text)
        step = max(1, chunk_size - chunk_overlap)
        start_idx += step
        if start_idx >= total_tokens:
            break
    return chunks

# --- Function to call Upstage API for a single (small) PDF --- 
def call_upstage_parser(pdf_path: str) -> str | None:
    """Calls Upstage API for a given PDF file path and returns extracted text."""
    global UPSTAGE_API_KEY
    if not UPSTAGE_API_KEY:
        print("Error: UPSTAGE_API_KEY not found in environment.")
        return None
    if not os.path.exists(pdf_path):
        print(f"Error: Temp PDF not found at {pdf_path}")
        return None
    url = "https://api.upstage.ai/v1/document-digitization"
    headers = {"Authorization": f"Bearer {UPSTAGE_API_KEY}"}
    data = {"ocr": "auto", "output_formats": "['text']", "model": "document-parse"}
    response = None
    file_handle = None
    try:
        file_handle = open(pdf_path, "rb")
        files = {"document": file_handle}
        print(f"    - Calling Upstage API for {os.path.basename(pdf_path)}...")
        response = requests.post(url, headers=headers, files=files, data=data, timeout=180)
        if response.status_code == 413:
             print(f"    - Error 413: File {os.path.basename(pdf_path)} is likely too large or has too many pages.")
             return None
        elif response.status_code >= 400:
            print(f"    - Error {response.status_code} processing {os.path.basename(pdf_path)}.")
            try:
                print(f"      API Response: {response.text[:500]}...") 
            except Exception as print_e:
                pass
            response.raise_for_status()
        result = response.json()
        text_content = []
        for element in result.get("elements", []):
            if element and "content" in element and isinstance(element["content"], dict) and "text" in element["content"]:
                text = element["content"]["text"]
                if isinstance(text, str) and text.strip():
                    text_content.append(text)
        extracted_text = "\n".join(text_content)
        return extracted_text
    except requests.exceptions.Timeout:
         print(f"    - Error: Upstage API request timed out for {os.path.basename(pdf_path)}.")
         return None
    except requests.exceptions.RequestException as e:
        print(f"    - Error during Upstage API request for {os.path.basename(pdf_path)}: {e}")
        return None
    except Exception as e:
        print(f"    - An unexpected error occurred calling Upstage API for {os.path.basename(pdf_path)}: {e}")
        return None
    finally:
        if file_handle and not file_handle.closed:
            file_handle.close()

# --- Function to split PDF into smaller PDFs --- 
def split_pdf(input_pdf_path: str, output_dir: str, pages_per_split: int = 20) -> list[str]:
    """Splits a PDF into smaller PDFs with a specified number of pages.
    
    Args:
        input_pdf_path: Path to the original PDF.
        output_dir: Directory to save the split PDF files.
        pages_per_split: Number of pages per smaller PDF file.

    Returns:
        A list of paths to the created smaller PDF files.
    """
    split_pdf_paths = []
    try:
        print(f"  -> Splitting PDF: {os.path.basename(input_pdf_path)} into chunks of {pages_per_split} pages...")
        reader = PyPDF2.PdfReader(input_pdf_path)
        total_pages = len(reader.pages)
        num_splits = math.ceil(total_pages / pages_per_split)
        print(f"    - Total pages: {total_pages}, Number of splits: {num_splits}")

        for i in range(num_splits):
            writer = PyPDF2.PdfWriter()
            start_page = i * pages_per_split
            end_page = min((i + 1) * pages_per_split, total_pages)
            
            for page_num in range(start_page, end_page):
                writer.add_page(reader.pages[page_num])
            
            split_filename = f"{os.path.splitext(os.path.basename(input_pdf_path))[0]}_split_{i+1:03d}.pdf"
            split_output_path = os.path.join(output_dir, split_filename)
            
            with open(split_output_path, "wb") as f:
                writer.write(f)
            split_pdf_paths.append(split_output_path)
            # print(f"    - Created split file: {split_filename}")
            
        print(f"  -> Finished splitting into {len(split_pdf_paths)} files in {output_dir}")
        return split_pdf_paths

    except PyPDF2.errors.PdfReadError as e:
         print(f"  -> Error reading PDF for splitting {os.path.basename(input_pdf_path)}: {e}")
         return []
    except Exception as e:
        print(f"  -> An unexpected error occurred during PDF splitting for {os.path.basename(input_pdf_path)}: {e}")
        return []

if __name__ == "__main__":
    DEFAULT_INPUT_DIR = "docs"
    DEFAULT_OUTPUT_DIR = "processed"
    DEFAULT_PAGES_PER_SPLIT = 20
    # Add chunking parameters back
    DEFAULT_CHUNK_SIZE = 500
    DEFAULT_CHUNK_OVERLAP = 50

    parser = argparse.ArgumentParser(description="Split PDF, process splits via API, combine text, chunk combined text, join chunks, and save.")
    parser.add_argument("input_dir", nargs='?', default=DEFAULT_INPUT_DIR, help=f"Input PDF directory (default: {DEFAULT_INPUT_DIR}).")
    parser.add_argument("output_dir", nargs='?', default=DEFAULT_OUTPUT_DIR, help=f"Output directory for final combined text files (default: {DEFAULT_OUTPUT_DIR}).")
    parser.add_argument("--pages_per_split", type=int, default=DEFAULT_PAGES_PER_SPLIT, help=f"Pages per split PDF for API call (default: {DEFAULT_PAGES_PER_SPLIT}).")
    # Add chunking args back
    parser.add_argument("--chunk_size", type=int, default=DEFAULT_CHUNK_SIZE, help=f"Chunk size in tokens (default: {DEFAULT_CHUNK_SIZE}).")
    parser.add_argument("--chunk_overlap", type=int, default=DEFAULT_CHUNK_OVERLAP, help=f"Token overlap (default: {DEFAULT_CHUNK_OVERLAP}).")
    parser.add_argument("--keep_splits", action='store_true', help="Keep the temporary split PDF files after processing.")

    args = parser.parse_args()

    if not UPSTAGE_API_KEY:
        print("Error: UPSTAGE_API_KEY not found in .env file.")
        exit(1)

    if not os.path.isdir(args.input_dir):
        print(f"Error: Input directory not found: {args.input_dir}")
        exit(1)

    if not os.path.exists(args.output_dir):
        print(f"Creating output directory: {args.output_dir}")
        os.makedirs(args.output_dir)
        
    temp_split_dir_base = os.path.join(args.output_dir, "_temp_splits")
    print(f"Using base temporary directory for split PDFs: {temp_split_dir_base}")

    pdf_files = glob.glob(os.path.join(args.input_dir, "*.pdf"))
    pdf_files.extend(glob.glob(os.path.join(args.input_dir, "*.PDF")))
    pdf_files = list(set(pdf_files))
    
    if not pdf_files:
        print(f"No PDF files found in directory: {args.input_dir}")
    else:
        print(f"Found {len(pdf_files)} PDF files to process in {args.input_dir}.")
        
        total_processed_files = 0
        total_failed_files = 0
        
        for pdf_path in pdf_files:
            print(f"--- Processing PDF: {os.path.basename(pdf_path)} ---")
            pdf_base_name = os.path.splitext(os.path.basename(pdf_path))[0]
            temp_split_dir = os.path.join(temp_split_dir_base, pdf_base_name)
            if not os.path.exists(temp_split_dir):
                 os.makedirs(temp_split_dir)
                 
            combined_text_from_api = ""
            split_files = []
            processing_success = True
            try:
                # 1. Split the PDF locally
                split_files = split_pdf(pdf_path, temp_split_dir, args.pages_per_split)

                if not split_files:
                    print(f"  -> Failed to split PDF {os.path.basename(pdf_path)}. Skipping.")
                    total_failed_files += 1
                    processing_success = False
                    continue

                # 2. Process each split PDF via Upstage API
                print(f"  -> Calling Upstage API for {len(split_files)} split files...")
                split_texts = []
                api_call_failed = False
                for i, split_pdf_path in enumerate(split_files):
                    extracted_text = call_upstage_parser(split_pdf_path)
                    if extracted_text is None: 
                        print(f"    - Failed to get text from split file {i+1}. Output might be incomplete.")
                        api_call_failed = True 
                    elif extracted_text:
                         split_texts.append(extracted_text)
                    
                if api_call_failed and not split_texts: 
                     print(f"  -> All API calls failed for splits of {os.path.basename(pdf_path)}. Skipping.")
                     total_failed_files += 1
                     processing_success = False
                     continue 
                elif api_call_failed:
                     print(f"  -> Warning: Some API calls failed for splits of {os.path.basename(pdf_path)}. Combined text might be incomplete.")
                     
                # 3. Combine text from successful splits
                combined_text_from_api = "\n\n".join(split_texts)
                print(f"  -> Combined text from API. Total length: {len(combined_text_from_api)} chars.")

                if not combined_text_from_api.strip():
                     print(f"  -> Combined text is empty after API processing. Skipping chunking and save.")
                     total_failed_files += 1 
                     processing_success = False
                     continue 
                     
                # 4. Chunk the combined text
                print(f"  -> Chunking combined text (size={args.chunk_size}, overlap={args.chunk_overlap})...")
                text_chunks = chunk_text(
                    combined_text_from_api, 
                    chunk_size=args.chunk_size, 
                    chunk_overlap=args.chunk_overlap
                )
                print(f"  -> Generated {len(text_chunks)} chunks.")

                if not text_chunks:
                     print(f"  -> No chunks generated from combined text. Skipping save.")
                     total_failed_files += 1
                     processing_success = False
                     continue
                     
                # 5. Join all chunks back into a single string (with overlap)
                final_text_to_save = "\n\n---CHUNK SEPARATOR---\n\n".join(text_chunks) # Join chunks with a separator
                print(f"  -> Joined {len(text_chunks)} chunks into final text. Final length: {len(final_text_to_save)} chars.")

                # 6. Save the joined chunked text to a single file
                base_filename_no_ext = os.path.splitext(os.path.basename(pdf_path))[0]
                output_txt_path = os.path.join(args.output_dir, f"{base_filename_no_ext}.txt")
                try:
                    with open(output_txt_path, 'w', encoding='utf-8') as f:
                        f.write(final_text_to_save)
                    print(f"  -> Saved final joined text to: {output_txt_path}")
                    total_processed_files += 1
                except IOError as e:
                    print(f"    Error saving final text to {output_txt_path}: {e}")
                    total_failed_files += 1
                    processing_success = False

            except Exception as e:
                print(f"An unexpected error occurred processing {os.path.basename(pdf_path)}: {e}")
                import traceback
                traceback.print_exc()
                total_failed_files += 1
                processing_success = False
            finally:
                 if temp_split_dir and os.path.exists(temp_split_dir) and not args.keep_splits:
                      try: 
                          shutil.rmtree(temp_split_dir)
                      except OSError as e:
                           print(f"    - Warning: Could not remove temp directory {temp_split_dir}: {e}")
                           
        if not args.keep_splits and os.path.exists(temp_split_dir_base):
             print(f"Cleaning up base temporary directory: {temp_split_dir_base}")
             try: 
                 shutil.rmtree(temp_split_dir_base)
             except OSError as e:
                  print(f"Warning: Could not remove main temp directory {temp_split_dir_base}: {e}")
                  
        print(f"\nOverall Processing complete. {total_processed_files} PDFs processed into final text files, {total_failed_files} PDFs failed.") 