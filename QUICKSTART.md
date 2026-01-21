# TKR College Chatbot - Quick Start Guide

## ✅ Setup Complete!

Your TKR College AI Chatbot is now fully configured and ready to use!

## 🎯 What's Working

✅ Database created with 7 tables
✅ Sample subjects loaded (6 subjects)
✅ Backend dependencies installed
✅ Frontend interface verified
✅ MySQL credentials configured

## 🚀 How to Start

### Backend Server

The backend is currently starting up. On first run, it downloads AI models (~100MB), which takes a few minutes.

**If not already running:**
```powershell
cd "c:\projects\TKR CHAT BOT\backend"
python app.py
```

You should see:
```
* Running on http://0.0.0.0:5000
* Database connection established
```

### Frontend Interface

The frontend is already accessible! Open in your browser:

**Option 1: Direct File**
```
file:///c:/projects/TKR CHAT BOT/frontend/index.html
```

**Option 2: Local Server (Recommended)**
```powershell
cd "c:\projects\TKR CHAT BOT\frontend"
python -m http.server 8000
```
Then visit: http://localhost:8000

## 📚 First Steps

### 1. Upload Study Materials

1. Click the **Upload** tab
2. Select a subject from the dropdown
3. Enter a title (e.g., "Chapter 1 - Introduction")
4. Add a description (optional)
5. Choose a PDF file
6. Click "Upload Material"
7. Wait for processing (shows progress)

The system will:
- Extract all text from the PDF
- Extract all images
- Generate AI embeddings for search
- Store everything in the database

### 2. Ask Questions

1. Go to the **Chat** tab
2. Type a question like:
   - "What is covered in Unit 1?"
   - "Explain normalization in databases"
   - "What are the important topics?"
3. Press Enter or click Send
4. Get AI-powered answers with sources!

### 3. Browse Materials

1. Click the **Materials** tab
2. See all uploaded PDFs
3. Filter by subject
4. Download PDFs or view extracted images

### 4. View Syllabus

1. Click the **Syllabus** tab
2. Select a subject
3. View organized units with topics

### 5. Important Questions

1. Click the **Questions** tab
2. Filter by subject or type
3. View questions with answers

## 🎨 Interface Features

- **Blue & Yellow Theme** - TKR College colors
- **Modern Design** - Gradients and smooth animations
- **Responsive** - Works on desktop, tablet, and mobile
- **Easy Navigation** - Tab-based interface
- **Real-time Feedback** - Progress indicators and notifications

## 🔧 Troubleshooting

### Backend won't start
- Check if port 5000 is available
- Verify MySQL is running
- Check `.env` file has correct credentials

### Frontend shows errors
- Make sure backend is running on port 5000
- Check browser console (F12) for errors
- Try using a local server instead of opening file directly

### PDF upload fails
- Check file size (max 50MB)
- Ensure PDF is not corrupted
- Verify sufficient disk space

### Chat not responding
- Wait for backend to finish loading AI models (first run only)
- Upload at least one PDF first
- Check backend console for errors

## 📊 System Status

**Database:** ✅ Ready (tkr_chatbot)
**Backend:** 🔄 Starting (downloading models on first run)
**Frontend:** ✅ Ready and verified
**Sample Data:** ✅ 6 subjects loaded

## 🎓 Sample Subjects Available

1. CS101 - Programming in C (Semester 1)
2. CS201 - Data Structures (Semester 2)
3. CS301 - Database Management Systems (Semester 3)
4. CS401 - Machine Learning (Semester 4)
5. EC101 - Basic Electronics (Semester 1)
6. ME101 - Engineering Mechanics (Semester 1)

## 📖 Documentation

- **README.md** - Full project documentation
- **SETUP.md** - Detailed setup instructions
- **Walkthrough.md** - Complete system overview

## 🎉 You're All Set!

Your TKR College AI Chatbot is ready to help students with:
- Study materials management
- Question answering from PDFs
- Syllabus information
- Important questions database

**Happy Learning! 🚀**

---

**Need Help?**
- Check the README.md for detailed information
- Review SETUP.md for troubleshooting
- Check backend console for error messages
- Verify all services are running
