import re
from typing import List, Dict, Any
from app.config import settings
import markdown
from pypdf import PdfReader

class DocumentProcessor:
    def __init__(self):
        self.chunk_size = settings.CHUNK_SIZE
        self.chunk_overlap = settings.CHUNK_OVERLAP

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
        """Split text into overlapping chunks"""
        if metadata is None:
            metadata = {}

        # Clean text
        text = self._clean_text(text)

        # Split into sentences (simple approach)
        sentences = re.split(r'(?<=[.!?])\s+', text)

        chunks = []
        current_chunk = ""
        current_length = 0

        for sentence in sentences:
            sentence_length = len(sentence)

            # If adding this sentence exceeds chunk size, save current chunk
            if current_length + sentence_length > self.chunk_size and current_chunk:
                chunks.append({
                    'text': current_chunk.strip(),
                    'metadata': metadata
                })

                # Start new chunk with overlap
                # Keep last few sentences for overlap
                overlap_text = self._get_overlap(current_chunk)
                current_chunk = overlap_text + " " + sentence
                current_length = len(current_chunk)
            else:
                current_chunk += " " + sentence
                current_length += sentence_length

        # Add final chunk
        if current_chunk.strip():
            chunks.append({
                'text': current_chunk.strip(),
                'metadata': metadata
            })

        return chunks

    def _clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove special characters that might cause issues
        text = text.replace('\x00', '')
        return text.strip()

    def _get_overlap(self, text: str) -> str:
        """Get overlap text from end of chunk"""
        if len(text) <= self.chunk_overlap:
            return text

        # Get last N characters for overlap
        return text[-self.chunk_overlap:]

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
