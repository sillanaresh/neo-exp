import re
from typing import List, Dict, Any
from app.config import settings
import markdown
from pypdf import PdfReader
import tiktoken

class DocumentProcessor:
    def __init__(self):
        # Use token-based chunking instead of character-based
        self.max_tokens = 2000  # Safe limit for embedding (well under 8192)
        self.overlap_tokens = 100
        # Use cl100k_base encoding (same as GPT-4 and text-embedding-3-small)
        self.encoder = tiktoken.get_encoding("cl100k_base")

    def process_file(self, file_path: str, file_type: str) -> str:
        """Process file based on type and return text content"""
        if file_type == 'markdown' or file_path.endswith('.md'):
            return self._process_markdown(file_path)
        elif file_type == 'pdf' or file_path.endswith('.pdf'):
            return self._process_pdf(file_path)
        elif file_type == 'text' or file_path.endswith('.txt'):
            return self._process_text(file_path)
        else:
            # Try to read as plain text
            return self._process_text(file_path)

    def _process_markdown(self, file_path: str) -> str:
        """Read markdown file"""
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()

    def _process_pdf(self, file_path: str) -> str:
        """Extract text from PDF"""
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text

    def _process_text(self, file_path: str) -> str:
        """Read plain text file"""
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()

    def chunk_text(self, text: str, metadata: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Split text into token-based overlapping chunks"""
        if metadata is None:
            metadata = {}

        # Clean text
        text = self._clean_text(text)

        # Split into paragraphs first, then sentences
        paragraphs = text.split('\n\n')
        sentences = []
        for para in paragraphs:
            # Split paragraph into sentences
            para_sentences = re.split(r'(?<=[.!?])\s+', para)
            sentences.extend(para_sentences)

        chunks = []
        current_chunk_sentences = []
        current_tokens = 0

        for sentence in sentences:
            # Count tokens in this sentence
            sentence_tokens = len(self.encoder.encode(sentence))

            # If adding this sentence exceeds max tokens, save current chunk
            if current_tokens + sentence_tokens > self.max_tokens and current_chunk_sentences:
                # Create chunk from current sentences
                chunk_text = " ".join(current_chunk_sentences)
                chunks.append({
                    'text': chunk_text.strip(),
                    'metadata': metadata
                })

                # Start new chunk with overlap (keep last few sentences)
                overlap_sentences = self._get_overlap_sentences(current_chunk_sentences)
                current_chunk_sentences = overlap_sentences + [sentence]
                current_tokens = sum(len(self.encoder.encode(s)) for s in current_chunk_sentences)
            else:
                current_chunk_sentences.append(sentence)
                current_tokens += sentence_tokens

        # Add final chunk
        if current_chunk_sentences:
            chunk_text = " ".join(current_chunk_sentences)
            chunks.append({
                'text': chunk_text.strip(),
                'metadata': metadata
            })

        return chunks

    def _get_overlap_sentences(self, sentences: List[str]) -> List[str]:
        """Get last few sentences for overlap, staying under overlap token limit"""
        overlap_sentences = []
        overlap_tokens = 0

        # Add sentences from the end until we hit overlap limit
        for sentence in reversed(sentences):
            sentence_tokens = len(self.encoder.encode(sentence))
            if overlap_tokens + sentence_tokens <= self.overlap_tokens:
                overlap_sentences.insert(0, sentence)
                overlap_tokens += sentence_tokens
            else:
                break

        return overlap_sentences

    def _clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove special characters that might cause issues
        text = text.replace('\x00', '')
        return text.strip()

    def process_and_chunk(self, file_path: str, file_type: str, document_name: str) -> List[Dict[str, Any]]:
        """Main method: process file and return chunks ready for embedding"""
        # Extract text
        text = self.process_file(file_path, file_type)

        # Create chunks with metadata
        metadata = {
            'source': document_name,
            'file_type': file_type
        }

        chunks = self.chunk_text(text, metadata)

        print(f"Processed {document_name}: {len(chunks)} chunks created")
        return chunks

# Global instance
document_processor = DocumentProcessor()
