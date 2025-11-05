# Neo Knowledge Base

An AI-powered knowledge base assistant that helps users understand Neo's capabilities by referencing real-world implementations from various brands. Features an intuitive interface with a playful design and powerful RAG (Retrieval-Augmented Generation) capabilities.

## ✨ Key Features

### 🤖 AI-Powered Chat Interface
- **Conversational RAG**: Ask questions in natural language and get contextual answers
- **Source Attribution**: Shows which documents were used to answer questions
- **Session Memory**: Maintains conversation context across multiple questions
- **Real-time Responses**: Streaming responses for better user experience

### 📚 Knowledge Base Management
- **Persistent Storage**: Uses Pinecone vector database for permanent document storage
- **Multiple File Formats**: Upload markdown (.md), text (.txt), and PDF (.pdf) files
- **Batch Upload**: Upload multiple documents at once
- **Automatic Processing**: Documents are automatically chunked, embedded, and indexed
- **File Type Detection**: Smart file type recognition with visual indicators
- **Upload Statistics**: Real-time tracking of vectors, files, and document details

### 🎨 Modern User Interface
- **Clean Home Page**: Choose between Chat Interface and Admin Panel
- **Interactive Logo**: Click the Neo logo for a delightful star animation ⭐
- **Cute Cat Companion**: Bottom-right cat mascot that jiggles, meows, and spawns hearts when clicked 🐱💕
- **Responsive Design**: Works seamlessly on desktop, tablet, and mobile devices
- **Enhanced Scrolling**: Always-visible scrollbars for better navigation

### 🔐 Admin Panel
- **Password Protected**: Secure access to administrative functions
- **Document Upload**: Easy drag-and-drop or click-to-upload interface
- **Knowledge Base Stats**: View total vectors, files, and document list
- **Upload Progress**: Real-time progress tracking for multiple file uploads
- **File Preview**: See selected files before uploading with size information

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

## 📖 Usage Guide

### Home Page
1. Open http://localhost:8000/
2. Click the **Neo logo** for a fun star animation ⭐
3. Click the **cute cat** in the bottom right for jiggles, meows, and hearts 🐱
4. Choose between:
   - **Chat Interface** - Public access to ask questions
   - **Admin Panel** - Password-protected document management

### Chat Interface
1. Navigate to http://localhost:8000/chat
2. Type your question about Neo's capabilities
3. The AI searches the knowledge base and provides contextual answers
4. Click on source documents to see where information came from
5. Continue the conversation - context is maintained throughout the session

### Admin Panel
1. Navigate to http://localhost:8000/admin
2. Enter admin password
3. **Upload Documents**:
   - Click or drag-and-drop files (supports multiple files)
   - See preview of selected files with sizes
   - Watch real-time upload progress
   - Get confirmation when upload completes
4. **View Statistics**:
   - Enter admin password and click "Load Statistics"
   - See total vectors and files in the knowledge base
   - Browse list of all uploaded documents with chunk counts
   - Scroll through documents in the styled scrollable area

### Uploading Documents
- **Supported formats**: `.md`, `.txt`, `.pdf`
- **Multiple files**: Upload several documents at once
- **Automatic processing**:
  - Documents are chunked into manageable pieces
  - Embeddings are created for each chunk
  - Chunks are stored in Pinecone vector database
  - Documents become immediately searchable
  - File names are preserved for source attribution

## 🚀 Deployment

### Railway (Recommended)

1. **Push code to GitHub**

2. **Connect to Railway**:
   - Go to [Railway](https://railway.app)
   - Create new project from GitHub repo
   - Railway auto-detects Python and requirements

3. **Set environment variables**:
   - `OPENROUTER_API_KEY`
   - `OPENAI_API_KEY`
   - `PINECONE_API_KEY`
   - `ADMIN_PASSWORD`

4. **Deploy!**
   - Automatic deployment on every push to main
   - Live at: `https://your-app-name.railway.app`

### Render (Alternative)

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

## 🎯 Recent Enhancements

- ✅ Multiple file upload support
- ✅ Real-time upload progress tracking
- ✅ Enhanced admin panel with statistics
- ✅ Interactive cat mascot with sound effects
- ✅ Improved scrollbar visibility
- ✅ File type indicators and preview
- ✅ Responsive mobile design
- ✅ Clean UI without vendor branding

## 🔮 Future Enhancements

- [ ] User authentication for chat interface
- [ ] Document versioning and updates
- [ ] Document deletion functionality
- [ ] Analytics and usage tracking
- [ ] Multi-language support
- [ ] Export conversations
- [ ] Advanced search filters
- [ ] Document tagging and categorization

## License

MIT