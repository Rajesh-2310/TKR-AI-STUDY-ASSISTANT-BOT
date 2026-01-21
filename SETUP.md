# TKR College Chatbot - Setup Guide

This guide will walk you through setting up the TKR College AI Chatbot system from scratch.

## Prerequisites

Before you begin, ensure you have:

- **Python 3.8 or higher** - [Download Python](https://www.python.org/downloads/)
- **MySQL 8.0 or higher** - [Download MySQL](https://dev.mysql.com/downloads/)
- **4GB+ RAM** - Required for AI models
- **2GB+ free disk space** - For models and uploaded files
- **Windows/Linux/Mac** - Any OS with Python support

## Step 1: Install MySQL

### Windows
1. Download MySQL Installer from [MySQL Downloads](https://dev.mysql.com/downloads/installer/)
2. Run the installer and choose "Developer Default"
3. Set a root password (remember this!)
4. Complete the installation

### Verify Installation
Open Command Prompt/Terminal and run:
```bash
mysql --version
```

## Step 2: Create Database

1. **Login to MySQL**
   ```bash
   mysql -u root -p
   ```
   Enter your root password when prompted.

2. **Create Database**
   ```sql
   CREATE DATABASE tkr_chatbot CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   EXIT;
   ```

3. **Import Schema**
   Navigate to the project directory:
   ```bash
   cd "c:\projects\TKR CHAT BOT"
   mysql -u root -p tkr_chatbot < database/schema.sql
   ```
   Enter your password when prompted.

## Step 3: Set Up Python Backend

1. **Navigate to Backend Directory**
   ```bash
   cd backend
   ```

2. **Create Virtual Environment (Recommended)**
   ```bash
   python -m venv venv
   ```

3. **Activate Virtual Environment**
   
   **Windows:**
   ```bash
   venv\Scripts\activate
   ```
   
   **Linux/Mac:**
   ```bash
   source venv/bin/activate
   ```

4. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```
   
   This will take several minutes as it downloads AI models (~100MB).

5. **Configure Environment**
   ```bash
   copy .env.example .env
   ```
   
   Edit `.env` file with your settings:
   ```env
   DB_HOST=localhost
   DB_PORT=3306
   DB_USER=root
   DB_PASSWORD=YOUR_MYSQL_PASSWORD
   DB_NAME=tkr_chatbot
   
   FLASK_ENV=development
   FLASK_DEBUG=True
   SECRET_KEY=change-this-to-random-string
   
   UPLOAD_FOLDER=../uploads
   MAX_FILE_SIZE=50000000
   
   EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
   ```

## Step 4: Initialize Database (Optional)

If you want to use the API to initialize:

1. **Start the backend**
   ```bash
   python app.py
   ```

2. **In another terminal, call the init endpoint**
   ```bash
   curl -X POST http://localhost:5000/api/init-db
   ```

## Step 5: Run the Application

### Start Backend Server

From the `backend` directory:
```bash
python app.py
```

You should see:
```
* Running on http://0.0.0.0:5000
* Database connection established
```

### Open Frontend

**Option 1: Direct File**
- Navigate to `frontend` folder
- Double-click `index.html`

**Option 2: Local Server (Recommended)**
```bash
cd frontend
python -m http.server 8000
```
Then open: http://localhost:8000

## Step 6: Add Initial Data

### Add Subjects

You can add subjects via API or directly in MySQL:

**Via MySQL:**
```sql
USE tkr_chatbot;

INSERT INTO subjects (subject_code, subject_name, semester, department) VALUES
('CS101', 'Programming in C', 1, 'Computer Science'),
('CS201', 'Data Structures', 2, 'Computer Science'),
('CS301', 'Database Management Systems', 3, 'Computer Science'),
('CS401', 'Machine Learning', 4, 'Computer Science');
```

**Via API (using curl):**
```bash
curl -X POST http://localhost:5000/api/subjects \
  -H "Content-Type: application/json" \
  -d "{\"subject_code\":\"CS101\",\"subject_name\":\"Programming in C\",\"semester\":1,\"department\":\"Computer Science\"}"
```

### Add Syllabus (Optional)

```sql
INSERT INTO syllabus (subject_id, unit_number, unit_name, topics, learning_outcomes) VALUES
(1, 1, 'Introduction to C', 'History of C, Basic structure, Data types, Variables', 'Understand C basics and write simple programs'),
(1, 2, 'Control Structures', 'If-else, Switch, Loops (for, while, do-while)', 'Implement decision making and iteration');
```

### Add Important Questions (Optional)

```sql
INSERT INTO important_questions (subject_id, question, answer, question_type, difficulty, unit_number) VALUES
(1, 'What is a variable in C?', 'A variable is a named storage location in memory that holds a value.', 'short', 'easy', 1),
(1, 'Explain the difference between while and do-while loops.', 'While loop checks condition first, do-while executes at least once before checking.', 'long', 'medium', 2);
```

## Step 7: Upload Study Materials

1. Open the frontend in your browser
2. Go to the **Upload** tab
3. Select a subject
4. Enter title and description
5. Choose a PDF file
6. Click "Upload Material"

The system will:
- Upload the PDF
- Extract text content
- Extract images
- Generate embeddings for semantic search
- Store everything in the database

## Verification

### Test Chat
1. Go to **Chat** tab
2. Upload a PDF first (if you haven't)
3. Ask a question like "What is covered in Unit 1?"
4. You should get an AI-generated answer with sources

### Test Materials
1. Go to **Materials** tab
2. You should see uploaded PDFs
3. Click "Download" to test download
4. Click "Images" to see extracted images

### Test Syllabus
1. Go to **Syllabus** tab
2. Select a subject
3. View the syllabus units

### Test Questions
1. Go to **Questions** tab
2. Filter by subject or type
3. View important questions

## Troubleshooting

### Backend won't start

**Error: "ModuleNotFoundError"**
```bash
pip install -r requirements.txt
```

**Error: "Database connection failed"**
- Check MySQL is running: `mysql -u root -p`
- Verify credentials in `.env`
- Ensure database exists: `SHOW DATABASES;`

**Error: "Port 5000 already in use"**
- Change port in `app.py`: `app.run(port=5001)`
- Update frontend `script.js`: `API_BASE_URL = 'http://localhost:5001/api'`

### Frontend issues

**CORS errors**
- Ensure backend is running
- Check API_BASE_URL in `script.js`
- Use a local server instead of opening file directly

**No data showing**
- Check browser console (F12) for errors
- Verify backend is running on port 5000
- Check network tab for failed requests

### PDF Processing fails

**Upload successful but not processed**
- Check backend console for errors
- Verify sufficient RAM (4GB+)
- Check disk space for uploads folder
- Try a smaller PDF first

**Images not extracted**
- Some PDFs have embedded images that are hard to extract
- Try a different PDF
- Check `uploads/images` folder for extracted files

### AI Model issues

**First run very slow**
- Normal! Model downloads on first run (~100MB)
- Subsequent runs use cached model
- Ensure stable internet connection

**Out of memory errors**
- Close other applications
- Reduce `CHUNK_SIZE` in `config.py`
- Use a smaller embedding model

## Production Deployment

For production use:

1. **Security**
   - Change `SECRET_KEY` to a strong random string
   - Set `FLASK_DEBUG=False`
   - Implement user authentication
   - Use HTTPS

2. **Database**
   - Create a dedicated MySQL user (not root)
   - Set strong password
   - Configure backups

3. **Server**
   - Use Gunicorn or uWSGI instead of Flask dev server
   - Set up Nginx as reverse proxy
   - Configure firewall

4. **Performance**
   - Add Redis for caching
   - Use GPU for faster embeddings
   - Optimize database indexes

## Updating the System

### Update Python packages
```bash
pip install --upgrade -r requirements.txt
```

### Update database schema
```bash
mysql -u root -p tkr_chatbot < database/schema.sql
```

### Backup database
```bash
mysqldump -u root -p tkr_chatbot > backup.sql
```

## Getting Help

1. Check the [README.md](README.md) for general information
2. Review error messages in:
   - Backend console
   - Browser console (F12)
   - MySQL logs
3. Verify all prerequisites are installed
4. Ensure all services are running

## Next Steps

Once setup is complete:

1. **Add your subjects** - Use the subjects table or API
2. **Upload PDFs** - Add study materials for each subject
3. **Add syllabus** - Populate syllabus information
4. **Add questions** - Create important questions database
5. **Test the chatbot** - Ask questions and verify answers
6. **Customize** - Modify colors, add features, etc.

## System Requirements Summary

| Component | Requirement |
|-----------|-------------|
| Python | 3.8+ |
| MySQL | 8.0+ |
| RAM | 4GB+ |
| Disk Space | 2GB+ |
| OS | Windows/Linux/Mac |
| Browser | Chrome, Firefox, Edge (latest) |

## File Locations

- **Backend**: `c:\projects\TKR CHAT BOT\backend\`
- **Frontend**: `c:\projects\TKR CHAT BOT\frontend\`
- **Database**: `c:\projects\TKR CHAT BOT\database\`
- **Uploads**: `c:\projects\TKR CHAT BOT\uploads\`
- **Images**: `c:\projects\TKR CHAT BOT\uploads\images\`

## Default Ports

- **Backend API**: http://localhost:5000
- **Frontend**: http://localhost:8000 (if using local server)

---

**Congratulations!** Your TKR College AI Chatbot is now set up and ready to use! 🎉
