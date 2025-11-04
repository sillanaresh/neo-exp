# Neo RAG Chatbot

An AI-powered chatbot that helps users understand Neo's capabilities by referencing real-world implementations from various brands.

## Features

- **Conversational RAG**: Ask questions in natural language and get contextual answers
- **Persistent Knowledge Base**: Uses Pinecone for permanent document storage
- **Easy Document Upload**: Admin panel for uploading markdown, text, and PDF files
- **Source Attribution**: Shows which documents were used to answer questions
- **Session Memory**: Maintains conversation context across multiple questions

## Tech Stack

- **Backend**: FastAPI (Python)
- **Vector Database**: Pinecone (serverless)
- **Embeddings**: OpenAI text-embedding-3-small
- **LLM**: Claude 3.5 Sonnet via OpenRouter
- **Frontend**: Vanilla HTML/CSS/JS

## Local Setup

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up environment variables**:
   - Copy `.env` file and update with your API keys
   - Required keys:
     - `OPENROUTER_API_KEY`
     - `OPENAI_API_KEY`
     - `PINECONE_API_KEY`
     - `ADMIN_PASSWORD`

3. **Run the application**:
   ```bash
   python -m uvicorn app.main:app --reload
   ```

4. **Access the application**:
   - Chat interface: http://localhost:8000/chat
   - Admin panel: http://localhost:8000/admin
   - API docs: http://localhost:8000/docs

## Usage

### Chat Interface
1. Open http://localhost:8000/chat
2. Ask questions about Neo's capabilities
3. The bot will search the knowledge base and provide contextual answers

### Admin Panel
1. Open http://localhost:8000/admin
2. Enter admin password (default: `neo-admin-2024`)
3. Upload markdown, text, or PDF documents
4. Documents are automatically processed and added to the knowledge base

### Uploading Documents
- Supported formats: `.md`, `.txt`, `.pdf`
- The system automatically:
  - Chunks the document into manageable pieces
  - Creates embeddings for each chunk
  - Stores them in Pinecone
  - Makes them immediately searchable

## Deployment to Render

1. **Push this code to GitHub**

2. **Create a new Web Service on Render**:
   - Connect your GitHub repository
   - Render will auto-detect the `render.yaml` configuration

3. **Set environment variables** in Render dashboard:
   - `OPENROUTER_API_KEY`
   - `OPENAI_API_KEY`
   - `PINECONE_API_KEY`
   - `ADMIN_PASSWORD`

4. **Deploy!**
   - Render will automatically build and deploy
   - Your app will be live at: `https://your-app-name.onrender.com`

## API Endpoints

- `POST /api/chat` - Chat with the bot
- `POST /api/clear/{session_id}` - Clear conversation history
- `POST /api/admin/upload` - Upload documents (requires password)
- `GET /api/admin/documents` - View knowledge base stats (requires password)
- `GET /api/search` - Search the knowledge base directly

## Configuration

Edit `.env` or environment variables:

- `PINECONE_INDEX_NAME` - Name of Pinecone index (default: neo-knowledge)
- `EMBEDDING_MODEL` - OpenAI embedding model (default: text-embedding-3-small)
- `LLM_MODEL` - OpenRouter model (default: anthropic/claude-3.5-sonnet)
- `ADMIN_PASSWORD` - Password for admin panel

## Architecture

```
User Query
    ↓
Embedding Creation (OpenAI)
    ↓
Vector Search (Pinecone) → Retrieve Top 5 Relevant Chunks
    ↓
Context Building
    ↓
LLM Query (Claude via OpenRouter) → Answer with Sources
    ↓
Response to User
```

## Cost Estimation (POC)

- **Pinecone**: Free tier (100K vectors)
- **OpenAI Embeddings**: ~$0.0001 per 1K tokens
- **OpenRouter (Claude)**: ~$0.003 per 1K input tokens, ~$0.015 per 1K output tokens
- **Render**: Free tier or $7/month for hobby plan

**Estimated monthly cost for light usage**: $5-10

## Security

- Admin endpoints are password-protected
- API keys stored in environment variables (not in code)
- `.gitignore` prevents committing sensitive files

## Future Enhancements

- [ ] User authentication for chat interface
- [ ] Document versioning and updates
- [ ] Better document management (delete, list, update)
- [ ] Analytics and usage tracking
- [ ] Multi-language support
- [ ] Export conversations

## License

MIT