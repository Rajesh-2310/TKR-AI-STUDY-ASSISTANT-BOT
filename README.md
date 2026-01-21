# TKR College AI Chatbot

An intelligent chatbot system for TKR College of Engineering and Technology that provides study materials, syllabus information, and answers questions using AI-powered RAG (Retrieval Augmented Generation).

## Features

✨ **AI-Powered Question Answering** - Ask questions and get answers from your study materials using local AI models

📚 **Study Materials Management** - Upload, organize, and download PDF study materials by subject

📖 **Syllabus Viewer** - Browse complete course syllabus organized by units

❓ **Important Questions** - Access curated important questions with answers

🖼️ **PDF Image Extraction** - Automatically extract images from uploaded PDFs

🎨 **Modern UI** - Beautiful interface with TKR's blue and yellow branding

## Technology Stack

### Backend
- **Python 3.8+** with Flask web framework
- **MySQL 8.0+** for data storage
- **Sentence Transformers** for local embeddings
- **PyPDF2 & pdfplumber** for PDF processing
- **RAG Engine** with semantic search

### Frontend
- **HTML5** with semantic markup
- **CSS3** with modern gradients and animations
- **Vanilla JavaScript** for API integration
- **Responsive Design** for all devices

## Project Structure

```
TKR CHAT BOT/
├── backend/
│   ├── app.py                 # Flask application
│   ├── config.py              # Configuration
│   ├── database.py            # Database utilities
│   ├── models.py              # Database models
│   ├── pdf_processor.py       # PDF processing
│   ├── rag_engine.py          # RAG implementation
│   ├── requirements.txt       # Python dependencies
│   └── .env.example           # Environment template
├── frontend/
│   ├── index.html             # Main HTML
│   ├── style.css              # Styles
│   └── script.js              # JavaScript
├── database/
│   └── schema.sql             # Database schema
└── uploads/                   # PDF storage (auto-created)
    └── images/                # Extracted images
```

## Quick Start

See [SETUP.md](SETUP.md) for detailed installation instructions.

### Prerequisites
- Python 3.8 or higher
- MySQL 8.0 or higher
- 4GB+ RAM (for AI models)

### Basic Setup

1. **Clone or navigate to the project directory**
   ```bash
   cd "c:\projects\TKR CHAT BOT"
   ```

2. **Set up MySQL database**
   - Create a MySQL user and database
   - Import the schema: `mysql -u root -p < database/schema.sql`

3. **Configure backend**
   ```bash
   cd backend
   copy .env.example .env
   # Edit .env with your database credentials
   ```

4. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Run the backend**
   ```bash
   python app.py
   ```

6. **Open the frontend**
   - Open `frontend/index.html` in a web browser
   - Or serve with a local server: `python -m http.server 8000`

## Usage Guide

### Uploading Materials
1. Go to the **Upload** tab
2. Select a subject
3. Enter title and description
4. Choose a PDF file
5. Click "Upload Material"
6. The system will automatically process the PDF and extract text/images

### Asking Questions
1. Go to the **Chat** tab
2. Optionally filter by subject
3. Type your question
4. Get AI-powered answers with source references

### Browsing Materials
1. Go to the **Materials** tab
2. Filter by subject if needed
3. Download PDFs or view extracted images

### Viewing Syllabus
1. Go to the **Syllabus** tab
2. Select a subject
3. View organized syllabus by units

### Important Questions
1. Go to the **Questions** tab
2. Filter by subject and question type
3. View questions with answers

## API Endpoints

### Subjects
- `GET /api/subjects` - Get all subjects
- `POST /api/subjects` - Create new subject

### Materials
- `GET /api/materials` - Get all materials
- `POST /api/upload` - Upload PDF material
- `GET /api/materials/<id>/download` - Download material
- `GET /api/materials/<id>/images` - Get extracted images

### Syllabus
- `GET /api/syllabus?subject_id=<id>` - Get syllabus
- `POST /api/syllabus` - Create syllabus entry

### Questions
- `GET /api/important-questions` - Get questions
- `POST /api/important-questions` - Create question

### Chat
- `POST /api/chat` - Send message and get AI response
- `GET /api/chat/history` - Get chat history

## Configuration

Edit `backend/.env` to configure:

```env
# Database
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=tkr_chatbot

# Application
FLASK_ENV=development
SECRET_KEY=your_secret_key

# File Storage
UPLOAD_FOLDER=../uploads
MAX_FILE_SIZE=50000000

# AI Model
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
```

## Adding Data

### Add Subjects
Use the API or insert directly into MySQL:
```sql
INSERT INTO subjects (subject_code, subject_name, semester, department)
VALUES ('CS501', 'Artificial Intelligence', 5, 'Computer Science');
```

### Add Syllabus
Use the API or insert into the syllabus table with unit information.

### Add Important Questions
Use the API or insert into the important_questions table.

## Troubleshooting

**Database connection failed**
- Verify MySQL is running
- Check credentials in `.env`
- Ensure database exists

**PDF processing fails**
- Check file size (max 50MB)
- Ensure PDF is not corrupted
- Verify sufficient disk space

**AI model loading slow**
- First run downloads the model (~100MB)
- Subsequent runs use cached model
- Ensure stable internet for first run

**CORS errors**
- Backend must be running on port 5000
- Frontend can be on any port
- CORS is enabled in Flask app

## Performance Tips

- **Database Indexing**: Already optimized in schema
- **Chunking**: Adjust `CHUNK_SIZE` in config.py for better results
- **Caching**: Consider Redis for production
- **Model**: Use GPU-enabled PyTorch for faster embeddings

## Security Notes

⚠️ **For Development Only**
- Change `SECRET_KEY` in production
- Use environment variables for sensitive data
- Implement authentication for production
- Validate and sanitize all inputs
- Use HTTPS in production

## Contributing

This is a college project. To extend:
1. Add more AI models (GPT, LLaMA)
2. Implement user authentication
3. Add more file types (DOCX, PPTX)
4. Create mobile app
5. Add voice interaction

## License

Educational project for TKR College of Engineering and Technology.

## Support

For issues or questions:
- Check the [SETUP.md](SETUP.md) guide
- Review API documentation above
- Check console logs for errors

## Credits

Developed for TKR College of Engineering and Technology
- Backend: Python, Flask, MySQL
- AI: Sentence Transformers (Local Models)
- Frontend: HTML, CSS, JavaScript
