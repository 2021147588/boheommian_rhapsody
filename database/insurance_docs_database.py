import os
import json
import chromadb
from chromadb.utils import embedding_functions
# Check if chromadb.utils.embedding_functions exists, otherwise import from chromadb.embeddings
try:
    from chromadb.utils.embedding_functions import EmbeddingFunction
except ImportError:
    from chromadb.utils.embedding_functions import EmbeddingFunction

from openai import OpenAI
from typing import List, Dict, Any
from tqdm import tqdm
import re
import sys
from dotenv import load_dotenv

load_dotenv()


# Constants
# Assuming the script is in data_preprocess, go up one level for base dir
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # 현재 파일의 위치가 루트
DATA_DIR = os.path.join(BASE_DIR, "insurance_docs")    # 실제 JSON이 들어 있는 디렉토리명
DB_PATH = os.path.join(BASE_DIR, "vector_db")          # 벡터 DB 위치
COLLECTION_NAME = "insurance_docs_v2"
# It's better practice to get the API key within the functions or classes
# where it's needed, rather than as a global constant upon import.
UPSTAGE_API_KEY = os.environ.get("UPSTAGE_API_KEY")
if not UPSTAGE_API_KEY:
    print("Error: UPSTAGE_API_KEY environment variable not set.", file=sys.stderr)
    sys.exit(1) # Exit if key is missing

# --- Upstage Embedding Function ---
class UpstageEmbeddingFunction(EmbeddingFunction):
    """Custom embedding function for ChromaDB using Upstage."""
    def __init__(self, api_key: str, model: str = "embedding-query", base_url: str = "https://api.upstage.ai/v1"):
        if not api_key:
             raise ValueError("Upstage API key is required.")
        self._client = OpenAI(api_key=api_key, base_url=base_url)
        self._model = model

    def __call__(self, input_texts: List[str]) -> List[List[float]]:
        embeddings = []
        for text in tqdm(input_texts, desc="Generating Embeddings"):
            # Handle potential empty strings which can cause API errors
            if not text or not text.strip():
                print("Warning: Encountered empty or whitespace-only text chunk, using zero vector.", file=sys.stderr)
                embeddings.append([0.0] * 1024) # Placeholder zero vector
                continue

            try:
                # Upstage API expects a list, even for single items
                response = self._client.embeddings.create(
                    input=[text], # Pass as a list
                    model=self._model
                )
                embeddings.append(response.data[0].embedding)
            except Exception as e:
                print(f"Error getting embedding for text chunk: {e}", file=sys.stderr)
                print(f"Problematic text snippet (first 100 chars): {text[:100]}", file=sys.stderr)
                embeddings.append([0.0] * 1024) # Placeholder zero vector on error
        return embeddings

# --- Text Chunking ---
def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    """
    Splits text into overlapping chunks based on sentences.
    Tries to respect sentence boundaries. Handles Korean better.
    """
    if not text:
        return []

    # More robust sentence splitting for Korean and English
    sentences = re.split(r'(?<=[.!?다까죠요])\s+', text.replace('\n', ' ').strip())
    sentences = [s.strip() for s in sentences if s.strip()] # Clean up splits

    if not sentences:
        return []

    chunks = []
    current_chunk_sentences = []
    current_length = 0

    for i, sentence in enumerate(sentences):
        sentence_length = len(sentence)

        # If adding the sentence exceeds chunk size, finalize the current chunk
        if current_length + sentence_length > chunk_size and current_chunk_sentences:
            chunks.append(" ".join(current_chunk_sentences))

            # Start new chunk with overlap: find suitable number of sentences for overlap
            overlap_sentences = []
            overlap_len = 0
            for j in range(len(current_chunk_sentences) - 1, -1, -1):
                sent = current_chunk_sentences[j]
                if overlap_len + len(sent) < overlap:
                    overlap_sentences.insert(0, sent)
                    overlap_len += len(sent)
                else:
                    break
            # Ensure the current sentence is included in the new chunk
            current_chunk_sentences = overlap_sentences + [sentence]
            current_length = sum(len(s) for s in current_chunk_sentences) + max(0, len(current_chunk_sentences) - 1)

        # Otherwise, add the sentence to the current chunk
        else:
            current_chunk_sentences.append(sentence)
            current_length += sentence_length + (1 if current_chunk_sentences else 0) # Add 1 for space

    # Add the last chunk if it's not empty
    if current_chunk_sentences:
        chunks.append(" ".join(current_chunk_sentences))

    return [chunk for chunk in chunks if chunk] # Ensure no empty chunks


# --- Main Preprocessing Function ---
def preprocess_and_store():
    """Loads data, preprocesses text, and stores embeddings in ChromaDB."""
    print("Starting preprocessing...")
    upstage_api_key = os.environ.get("UPSTAGE_API_KEY")
    if not upstage_api_key:
        print("Error: UPSTAGE_API_KEY environment variable not set.", file=sys.stderr)
        return # Stop processing if key is missing

    # Ensure DB directory exists
    os.makedirs(DB_PATH, exist_ok=True)
    print(f"ChromaDB path: {os.path.abspath(DB_PATH)}")

    # Initialize ChromaDB client and embedding function
    try:
        chroma_client = chromadb.PersistentClient(path=DB_PATH)
        upstage_ef = UpstageEmbeddingFunction(api_key=upstage_api_key, model="embedding-query")
    except Exception as e:
         print(f"Error initializing ChromaDB client or Embedding Function: {e}", file=sys.stderr)
         return


    # Get or create collection (Updated for Chroma v0.6.0+)
    print(f"Accessing collection: {COLLECTION_NAME}")
    collection = None # Initialize collection variable
    try:
        # Try to get the collection directly. This is the standard way in 0.6.0+
        # It will raise an exception if it doesn't exist (likely ValueError or similar, 
        # but we'll catch broadly first and refine if needed).
        collection = chroma_client.get_collection(
            name=COLLECTION_NAME,
            embedding_function=upstage_ef
        )
        print(f"Collection '{COLLECTION_NAME}' already exists.")
        # Ask user if they want to clear it
        clear_collection = input(f"Clear existing collection '{COLLECTION_NAME}'? (y/N): ").lower() == 'y'
        if clear_collection:
            print(f"Clearing collection '{COLLECTION_NAME}'...")
            chroma_client.delete_collection(name=COLLECTION_NAME)
            print("Recreating collection...")
            collection = chroma_client.create_collection(
                name=COLLECTION_NAME,
                embedding_function=upstage_ef,
                metadata={"hnsw:space": "cosine"} 
            )
            print("Collection cleared and recreated.")
            
    except Exception as get_err:
        # Catching a general Exception first to see what get_collection raises when not found.
        # In newer versions, it might be a ValueError or a specific Chroma exception.
        # We assume any error here likely means the collection doesn't exist or there's another setup issue.
        print(f"Collection '{COLLECTION_NAME}' likely does not exist or error getting it: {get_err}")
        print(f"Attempting to create new collection: {COLLECTION_NAME}")
        try:
             collection = chroma_client.create_collection(
                name=COLLECTION_NAME,
                embedding_function=upstage_ef,
                metadata={"hnsw:space": "cosine"}
            )
             print("Collection created successfully.")
        except Exception as create_e:
            print(f"Error creating ChromaDB collection: {create_e}", file=sys.stderr)
            # Print traceback for debugging
            import traceback
            traceback.print_exc()
            return # Stop if creation fails

    # Check if collection was successfully obtained or created
    if collection is None:
        print("Error: Failed to obtain or create the ChromaDB collection.", file=sys.stderr)
        return

    # --- Data Loading and Processing ---
    all_docs = []
    all_metadatas = []
    all_ids = []

    print(f"Loading JSON files from: {os.path.abspath(DATA_DIR)}")
    try:
        json_files = [f for f in os.listdir(DATA_DIR) if f.endswith('.json')]
    except FileNotFoundError:
         print(f"Error: Data directory not found at {DATA_DIR}", file=sys.stderr)
         return
    except Exception as e:
         print(f"Error listing files in {DATA_DIR}: {e}", file=sys.stderr)
         return

    if not json_files:
        print(f"Warning: No JSON files found in {DATA_DIR}", file=sys.stderr)
        # Decide if you want to stop or continue if no files found
        # return

    for filename in tqdm(json_files, desc="Processing Files"):
        file_path = os.path.join(DATA_DIR, filename)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

                # Extract text - adjust path based on actual JSON structure
                if data.get("success") and isinstance(data.get("content"), dict):
                     text_content = data["content"].get("text")
                     if isinstance(text_content, str) and text_content.strip():
                        chunks = chunk_text(text_content)
                        source_file = data.get("filename", filename) # Use filename from JSON if available

                        for i, chunk in enumerate(chunks):
                            if len(chunk) < 20: # Skip very short chunks
                                continue
                            chunk_id = f"{source_file}_{i}"
                            all_docs.append(chunk)
                            all_metadatas.append({"source": source_file, "chunk_index": i})
                            all_ids.append(chunk_id)
                     else:
                         # print(f"Warning: No valid text content found in {filename} under content.text.", file=sys.stderr)
                         pass # Reduce noise for expected empty content
                else:
                    # print(f"Warning: Skipping {filename} due to missing 'success' or 'content.text', or unexpected structure.", file=sys.stderr)
                     pass # Reduce noise

        except json.JSONDecodeError:
            print(f"Error decoding JSON from {filename}. Skipping.", file=sys.stderr)
        except Exception as e:
            print(f"An unexpected error occurred processing {filename}: {e}", file=sys.stderr)

    if not all_docs:
        print("No valid document chunks extracted to add to the database.", file=sys.stderr)
        return

    # --- Add documents to ChromaDB in batches ---
    batch_size = 100 # Adjust batch size based on performance/memory
    print(f"\nAdding {len(all_docs)} document chunks to ChromaDB collection '{COLLECTION_NAME}' in batches of {batch_size}...")

    added_count = 0
    error_count = 0
    for i in tqdm(range(0, len(all_docs), batch_size), desc="Adding to ChromaDB"):
        batch_docs = all_docs[i:i+batch_size]
        batch_metadatas = all_metadatas[i:i+batch_size]
        batch_ids = all_ids[i:i+batch_size]

        # Ensure IDs are unique within the batch and potentially globally if needed
        if len(batch_ids) != len(set(batch_ids)):
             print(f"Warning: Duplicate IDs found in batch starting at index {i}. Skipping batch.", file=sys.stderr)
             error_count += len(batch_ids)
             continue

        try:
            collection.add(
                documents=batch_docs,
                metadatas=batch_metadatas,
                ids=batch_ids
            )
            added_count += len(batch_ids)
        except Exception as e:
            print(f"\nError adding batch starting at index {i} to ChromaDB: {e}", file=sys.stderr)
            # Log problematic IDs or documents here if possible
            print(f"Problematic IDs (first few): {batch_ids[:5]}", file=sys.stderr)
            error_count += len(batch_ids)


    final_count = collection.count()
    print(f"\nPreprocessing finished.")
    print(f"Successfully added: {added_count} chunks.")
    print(f"Failed/Skipped: {error_count} chunks.")
    print(f"Total documents in collection '{COLLECTION_NAME}': {final_count}")

if __name__ == "__main__":
    # Load .env from the root directory relative to this script
    
    # Run the preprocessing
    preprocess_and_store() 