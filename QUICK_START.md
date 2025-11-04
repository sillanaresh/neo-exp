# Neo RAG Chatbot - Quick Start Guide

## What You Have

A fully functional RAG (Retrieval Augmented Generation) chatbot that:
- Stores knowledge documents in Pinecone (cloud-hosted, never loses data)
- Uses OpenAI for embeddings and OpenRouter for LLM responses
- Has a beautiful chat interface and admin panel
- Remembers conversation context
- Shows which documents were used to answer questions

## How to Run Locally

### 1. Start the Server

```bash
./start.sh
```

Or manually:
```bash
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 2. Access the Application

Open your browser and go to:

- **Chat Interface**: http://localhost:8000/chat
- **Admin Panel**: http://localhost:8000/admin
- **API Docs**: http://localhost:8000/docs

## Uploading Your First Document

1. Go to http://localhost:8000/admin
2. Enter the admin password: `neo-admin-2024`
3. Click "Choose file" and select your Shell auth guide markdown file
4. Optionally give it a name like "Shell Authentication Guide"
5. Click "Upload Document"
6. Wait a few seconds for processing
7. Done! The document is now in the knowledge base

## Testing the Chat

1. Go to http://localhost:8000/chat
2. Try asking:
   - "Can Neo handle OAuth authentication?"
   - "How does Shell implement authentication?"
   - "What authentication methods are supported?"
3. The bot will search the uploaded documents and answer based on real examples

## Adding More Documents

Just repeat the upload process! You can add:
- Indigo's use case documentation
- Other brands' implementation guides
- Technical specifications
- Any markdown, PDF, or text files

All documents are automatically:
- Chunked into searchable pieces
- Embedded and stored in Pinecone
- Immediately available for queries

## Deploying to Render (Making it Public)

### Step 1: Push to GitHub

```bash
git add .
git commit -m "Add Neo RAG chatbot"
git push origin stuttgart
```

### Step 2: Create Render Web Service

1. Go to https://dashboard.render.com/
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Render will auto-detect the `render.yaml` file

### Step 3: Set Environment Variables

In the Render dashboard, add these environment variables:
- `OPENROUTER_API_KEY`: Your OpenRouter key
- `OPENAI_API_KEY`: Your OpenAI key
- `PINECONE_API_KEY`: Your Pinecone key
- `ADMIN_PASSWORD`: Choose a secure password

### Step 4: Deploy!

Click "Create Web Service" and wait 2-3 minutes.

Your app will be live at: `https://your-app-name.onrender.com`

## Sharing with Your Team

Once deployed on Render:

1. **For Chat Users**: Share `https://your-app-name.onrender.com/chat`
   - Anyone can ask questions
   - Everyone sees the same knowledge base

2. **For Admins**: Share `https://your-app-name.onrender.com/admin`
   - Only those with the password can upload documents
   - Documents are immediately available to all users

## Important Notes

### Free Tier Limitations
- Render free tier: Server sleeps after 15 min of inactivity
- First request after sleep takes 30-60 seconds to wake up
- **Pinecone data is NEVER lost** (it's cloud-hosted)

### To Avoid Sleep Issues
- Upgrade to Render paid plan ($7/month) for always-on
- Or use a free uptime monitor like UptimeRobot to ping it every 10 minutes

## Cost Breakdown

For a POC with light usage:

- **Pinecone**: $0 (free tier, 100K vectors)
- **OpenAI Embeddings**: ~$0.50/month (for queries)
- **OpenRouter (Claude)**: ~$2-5/month (for chat responses)
- **Render**: $0 (free tier) or $7/month (paid, recommended)

**Total**: ~$3-8/month depending on usage

## Troubleshooting

### Server won't start
```bash
# Make sure dependencies are installed
pip install -r requirements.txt
```

### Chat gives errors
- Check that all API keys in `.env` are correct
- Check Pinecone index was created (might take 30 seconds first time)

### Documents not uploading
- Make sure file is .md, .txt, or .pdf
- Check admin password is correct
- Check server logs for errors

## Next Steps

1. **Test locally** - Upload Shell doc, ask questions
2. **Deploy to Render** - Make it accessible to your team
3. **Add more documents** - Indigo, other brands
4. **Customize** - Change passwords, models, styling

## Questions?

Everything is set up and ready to go. The system will:
- Auto-create the Pinecone index on first run
- Handle all document processing automatically
- Scale as you add more documents

Just start uploading documents and asking questions!
