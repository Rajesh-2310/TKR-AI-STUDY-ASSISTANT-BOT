// TKR College Chatbot - Frontend JavaScript
// API Configuration
const API_BASE_URL = 'http://localhost:5000/api';

// State Management
let currentTab = 'chat';
let sessionId = generateSessionId();
let subjects = [];
let currentSubjectFilter = null;
let isAdmin = false;
let adminEmail = '';
let adminSessionToken = '';

// Initialize Application
document.addEventListener('DOMContentLoaded', () => {
    initializeApp();
});

async function initializeApp() {
    await checkAdminAuth();  // Check admin authentication first
    setupEventListeners();
    await loadSubjects();
    await loadMaterials();
    await loadImportantQuestions();
}

// Generate Session ID
function generateSessionId() {
    return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
}

// Event Listeners Setup
function setupEventListeners() {
    // Navigation tabs
    document.querySelectorAll('.nav-tab').forEach(tab => {
        tab.addEventListener('click', () => switchTab(tab.dataset.tab));
    });

    // Chat form
    const chatForm = document.getElementById('chat-form');
    chatForm.addEventListener('submit', handleChatSubmit);

    // Upload form
    const uploadForm = document.getElementById('upload-form');
    uploadForm.addEventListener('submit', handleUploadSubmit);

    // File upload area
    const fileUploadArea = document.getElementById('file-upload-area');
    const fileInput = document.getElementById('file-input');

    fileUploadArea.addEventListener('click', () => fileInput.click());
    fileInput.addEventListener('change', handleFileSelect);

    // Drag and drop
    fileUploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        fileUploadArea.style.borderColor = 'var(--primary-blue)';
    });

    fileUploadArea.addEventListener('dragleave', () => {
        fileUploadArea.style.borderColor = 'var(--light-gray)';
    });

    fileUploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        fileUploadArea.style.borderColor = 'var(--light-gray)';
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            fileInput.files = files;
            handleFileSelect();
        }
    });

    // Subject filters
    document.getElementById('chat-subject-filter').addEventListener('change', (e) => {
        currentSubjectFilter = e.target.value ? parseInt(e.target.value) : null;
    });

    document.getElementById('materials-subject-filter').addEventListener('change', (e) => {
        loadMaterials(e.target.value ? parseInt(e.target.value) : null);
    });

    document.getElementById('syllabus-subject-filter').addEventListener('change', (e) => {
        if (e.target.value) {
            loadSyllabus(parseInt(e.target.value));
        } else {
            showEmptyState('syllabus-content', 'Select a subject to view its syllabus');
        }
    });

    document.getElementById('questions-subject-filter').addEventListener('change', () => {
        loadImportantQuestions();
    });

    document.getElementById('questions-type-filter').addEventListener('change', () => {
        loadImportantQuestions();
    });

    // Admin button
    document.getElementById('admin-btn').addEventListener('click', handleAdminClick);

    // Upload type tabs
    document.querySelectorAll('.upload-tab-btn').forEach(btn => {
        btn.addEventListener('click', () => switchUploadType(btn.dataset.uploadType));
    });

    // Syllabus form
    const syllabusForm = document.getElementById('syllabus-form');
    if (syllabusForm) {
        syllabusForm.addEventListener('submit', handleSyllabusSubmit);
    }

    // Question form
    const questionForm = document.getElementById('question-form');
    if (questionForm) {
        questionForm.addEventListener('submit', handleQuestionSubmit);
    }
}

// Upload Type Switching
function switchUploadType(type) {
    // Update tab buttons
    document.querySelectorAll('.upload-tab-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.uploadType === type);
    });

    // Update form containers
    document.querySelectorAll('.upload-form-container').forEach(container => {
        container.classList.remove('active');
    });

    document.getElementById(`${type}-upload`).classList.add('active');
}

// Tab Switching
function switchTab(tabName) {
    currentTab = tabName;

    // Update nav tabs
    document.querySelectorAll('.nav-tab').forEach(tab => {
        tab.classList.toggle('active', tab.dataset.tab === tabName);
    });

    // Update content
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.toggle('active', content.id === `${tabName}-tab`);
    });
}

// Load Subjects
async function loadSubjects() {
    try {
        const response = await fetch(`${API_BASE_URL}/subjects`);
        const data = await response.json();

        if (data.success) {
            subjects = data.subjects;
            populateSubjectSelects();
        }
    } catch (error) {
        console.error('Error loading subjects:', error);
        showToast('Failed to load subjects', 'error');
    }
}

// Populate Subject Dropdowns
function populateSubjectSelects() {
    const selects = [
        'chat-subject-filter',
        'materials-subject-filter',
        'syllabus-subject-filter',
        'questions-subject-filter',
        'upload-subject',
        'syllabus-subject',
        'question-subject'
    ];

    selects.forEach(selectId => {
        const select = document.getElementById(selectId);
        const currentValue = select.value;

        // Clear existing options except first
        while (select.options.length > 1) {
            select.remove(1);
        }

        // Add subject options
        subjects.forEach(subject => {
            const option = document.createElement('option');
            option.value = subject.id;
            option.textContent = `${subject.subject_code} - ${subject.subject_name}`;
            select.appendChild(option);
        });

        // Restore previous value if exists
        if (currentValue) {
            select.value = currentValue;
        }
    });
}

// Chat Functions
async function handleChatSubmit(e) {
    e.preventDefault();

    const input = document.getElementById('chat-input');
    const message = input.value.trim();

    if (!message) return;

    // Clear input
    input.value = '';

    // Add user message to chat
    addMessageToChat('user', message);

    // Show typing indicator
    showTypingIndicator();

    try {
        const response = await fetch(`${API_BASE_URL}/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                message: message,
                subject_id: currentSubjectFilter,
                session_id: sessionId
            })
        });

        const data = await response.json();

        hideTypingIndicator();

        if (data.success) {
            addMessageToChat('bot', data.answer, data.sources, data.confidence);
        } else {
            addMessageToChat('bot', 'Sorry, I encountered an error. Please try again.');
        }
    } catch (error) {
        hideTypingIndicator();
        console.error('Chat error:', error);
        addMessageToChat('bot', 'Sorry, I could not connect to the server. Please try again later.');
    }
}

function addMessageToChat(sender, text, sources = null, confidence = null) {
    const messagesContainer = document.getElementById('chat-messages');

    // Remove welcome message if exists
    const welcomeMessage = messagesContainer.querySelector('.welcome-message');
    if (welcomeMessage) {
        welcomeMessage.remove();
    }

    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}`;

    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.textContent = sender === 'user' ? 'U' : 'AI';

    const content = document.createElement('div');
    content.className = 'message-content';

    const messageText = document.createElement('div');
    messageText.className = 'message-text';

    // Render markdown for bot messages, plain text for user messages
    if (sender === 'bot') {
        // Configure marked for safe rendering
        if (typeof marked !== 'undefined') {
            marked.setOptions({
                breaks: true,        // Convert \n to <br>
                gfm: true,          // GitHub Flavored Markdown
                headerIds: false,   // Don't add IDs to headers
                mangle: false       // Don't escape email addresses
            });
            messageText.innerHTML = marked.parse(text);
        } else {
            // Fallback if marked is not loaded
            messageText.textContent = text;
        }
    } else {
        messageText.textContent = text;  // Keep user messages as plain text
    }

    content.appendChild(messageText);

    // Add sources if available
    if (sources && sources.length > 0) {
        const sourcesDiv = document.createElement('div');
        sourcesDiv.className = 'message-sources';

        const sourcesTitle = document.createElement('strong');
        sourcesTitle.textContent = 'Sources:';
        sourcesDiv.appendChild(sourcesTitle);

        sources.forEach(source => {
            const sourceItem = document.createElement('div');
            sourceItem.className = 'source-item';
            sourceItem.textContent = `📄 ${source.material} (Page ${source.page})`;
            sourcesDiv.appendChild(sourceItem);
        });

        content.appendChild(sourcesDiv);
    }

    messageDiv.appendChild(avatar);
    messageDiv.appendChild(content);

    messagesContainer.appendChild(messageDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

function showTypingIndicator() {
    document.getElementById('typing-indicator').style.display = 'flex';
}

function hideTypingIndicator() {
    document.getElementById('typing-indicator').style.display = 'none';
}

// Materials Functions
async function loadMaterials(subjectId = null) {
    try {
        const url = subjectId
            ? `${API_BASE_URL}/materials?subject_id=${subjectId}`
            : `${API_BASE_URL}/materials`;

        const response = await fetch(url);
        const data = await response.json();

        if (data.success) {
            displayMaterials(data.materials);
        }
    } catch (error) {
        console.error('Error loading materials:', error);
        showToast('Failed to load materials', 'error');
    }
}

function displayMaterials(materials) {
    const grid = document.getElementById('materials-grid');
    grid.innerHTML = '';

    if (materials.length === 0) {
        showEmptyState('materials-grid', 'No materials available');
        return;
    }

    materials.forEach(material => {
        const card = createMaterialCard(material);
        grid.appendChild(card);
    });
}

function createMaterialCard(material) {
    const card = document.createElement('div');
    card.className = 'material-card';

    const uploadDate = new Date(material.upload_date).toLocaleDateString();
    const fileSize = formatFileSize(material.file_size);

    const deleteButton = isAdmin ? `
        <button class="btn btn-danger" onclick="deleteMaterial(${material.id}, '${escapeHtml(material.title).replace(/'/g, "\\'")}')">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="3 6 5 6 21 6"></polyline>
                <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
            </svg>
            Delete
        </button>
    ` : '';

    card.innerHTML = `
        <div class="material-icon">
            <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                <polyline points="14 2 14 8 20 8"></polyline>
            </svg>
        </div>
        <h3>${escapeHtml(material.title)}</h3>
        <div class="material-meta">
            <span>📅 ${uploadDate}</span>
            <span>📦 ${fileSize}</span>
        </div>
        <p class="material-description">${escapeHtml(material.description || 'No description')}</p>
        <div class="material-actions">
            <button class="btn btn-primary" onclick="downloadMaterial(${material.id}, '${escapeHtml(material.title)}')">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                    <polyline points="7 10 12 15 17 10"></polyline>
                    <line x1="12" y1="15" x2="12" y2="3"></line>
                </svg>
                Download
            </button>
            ${deleteButton}
        </div>
    `;

    return card;
}

async function downloadMaterial(materialId, title) {
    try {
        const response = await fetch(`${API_BASE_URL}/materials/${materialId}/download`);
        const blob = await response.blob();

        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${title}.pdf`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);

        showToast('Download started', 'success');
    } catch (error) {
        console.error('Download error:', error);
        showToast('Download failed', 'error');
    }
}


// Syllabus Functions
async function loadSyllabus(subjectId) {
    try {
        const response = await fetch(`${API_BASE_URL}/syllabus?subject_id=${subjectId}`);
        const data = await response.json();

        if (data.success) {
            displaySyllabus(data.syllabus);
        }
    } catch (error) {
        console.error('Error loading syllabus:', error);
        showToast('Failed to load syllabus', 'error');
    }
}

function displaySyllabus(syllabusItems) {
    const container = document.getElementById('syllabus-content');
    container.innerHTML = '';

    if (syllabusItems.length === 0) {
        showEmptyState('syllabus-content', 'No syllabus available for this subject');
        return;
    }

    syllabusItems.forEach(item => {
        const unitDiv = document.createElement('div');
        unitDiv.className = 'syllabus-unit';

        unitDiv.innerHTML = `
            <h3>Unit ${item.unit_number}: ${escapeHtml(item.unit_name)}</h3>
            <h4>Topics:</h4>
            <p>${escapeHtml(item.topics)}</p>
            ${item.learning_outcomes ? `
                <h4>Learning Outcomes:</h4>
                <p>${escapeHtml(item.learning_outcomes)}</p>
            ` : ''}
        `;

        container.appendChild(unitDiv);
    });
}

// Important Questions Functions
async function loadImportantQuestions() {
    try {
        const subjectId = document.getElementById('questions-subject-filter').value;
        const questionType = document.getElementById('questions-type-filter').value;

        let url = `${API_BASE_URL}/important-questions`;
        const params = [];

        if (subjectId) params.push(`subject_id=${subjectId}`);
        if (questionType) params.push(`type=${questionType}`);

        if (params.length > 0) {
            url += '?' + params.join('&');
        }

        const response = await fetch(url);
        const data = await response.json();

        if (data.success) {
            displayQuestions(data.questions);
        }
    } catch (error) {
        console.error('Error loading questions:', error);
        showToast('Failed to load questions', 'error');
    }
}

function displayQuestions(questions) {
    const container = document.getElementById('questions-list');
    container.innerHTML = '';

    if (questions.length === 0) {
        showEmptyState('questions-list', 'No questions available');
        return;
    }

    questions.forEach(question => {
        const card = createQuestionCard(question);
        container.appendChild(card);
    });
}

function createQuestionCard(question) {
    const card = document.createElement('div');
    card.className = 'question-card';

    const deleteButton = isAdmin ? `
        <button class="btn btn-danger btn-sm" onclick="deleteQuestion(${question.id}, '${escapeHtml(question.question).replace(/'/g, "\\'")}')">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="3 6 5 6 21 6"></polyline>
                <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
            </svg>
            Delete
        </button>
    ` : '';

    card.innerHTML = `
        <div class="question-header">
            <div>
                <strong style="color: var(--gray); font-size: 0.875rem;">
                    ${escapeHtml(question.subject_name)}
                    ${question.unit_number ? ` - Unit ${question.unit_number}` : ''}
                </strong>
            </div>
            <div class="question-badges">
                <span class="badge badge-type">${escapeHtml(question.question_type)}</span>
                <span class="badge badge-difficulty">${escapeHtml(question.difficulty)}</span>
                ${deleteButton}
            </div>
        </div>
        <div class="question-text">${escapeHtml(question.question)}</div>
        ${question.answer ? `
            <div class="question-answer">
                <strong style="color: var(--primary-blue); display: block; margin-bottom: 0.5rem;">Answer:</strong>
                ${escapeHtml(question.answer)}
            </div>
        ` : ''}
    `;

    return card;
}

// Upload Functions
function handleFileSelect() {
    const fileInput = document.getElementById('file-input');
    const fileInfo = document.getElementById('file-info');

    if (fileInput.files.length > 0) {
        const file = fileInput.files[0];
        fileInfo.style.display = 'block';
        fileInfo.textContent = `Selected: ${file.name} (${formatFileSize(file.size)})`;
    }
}

async function handleUploadSubmit(e) {
    e.preventDefault();

    const subjectId = document.getElementById('upload-subject').value;
    const title = document.getElementById('upload-title').value;
    const description = document.getElementById('upload-description').value;
    const fileInput = document.getElementById('file-input');

    if (!fileInput.files.length) {
        showToast('Please select a file', 'error');
        return;
    }

    const formData = new FormData();
    formData.append('file', fileInput.files[0]);
    formData.append('subject_id', subjectId);
    formData.append('title', title);
    formData.append('description', description);

    const uploadButton = document.getElementById('upload-button');
    const uploadProgress = document.getElementById('upload-progress');
    const progressFill = document.getElementById('progress-fill');
    const progressText = document.getElementById('progress-text');

    uploadButton.disabled = true;
    uploadProgress.style.display = 'block';
    progressFill.style.width = '0%';
    progressText.textContent = 'Uploading...';

    try {
        // Simulate progress
        let progress = 0;
        const progressInterval = setInterval(() => {
            progress += 10;
            if (progress <= 90) {
                progressFill.style.width = progress + '%';
            }
        }, 200);

        const response = await fetch(`${API_BASE_URL}/upload`, {
            method: 'POST',
            body: formData
        });

        clearInterval(progressInterval);

        const data = await response.json();

        if (data.success) {
            progressFill.style.width = '100%';
            progressText.textContent = 'Processing PDF...';

            setTimeout(() => {
                showToast('Material uploaded successfully!', 'success');
                uploadProgress.style.display = 'none';
                uploadButton.disabled = false;

                // Reset form
                e.target.reset();
                document.getElementById('file-info').style.display = 'none';

                // Reload materials
                loadMaterials();

                // Show info about processing
                if (data.chunks_created) {
                    showToast(`Processed ${data.chunks_created} text chunks and ${data.images_extracted} images`, 'success');
                }
            }, 1000);
        } else {
            throw new Error(data.error || 'Upload failed');
        }
    } catch (error) {
        console.error('Upload error:', error);
        showToast('Upload failed: ' + error.message, 'error');
        uploadProgress.style.display = 'none';
        uploadButton.disabled = false;
    }
}

// Syllabus Upload
async function handleSyllabusSubmit(e) {
    e.preventDefault();

    const subjectId = document.getElementById('syllabus-subject').value;
    const unitNumber = document.getElementById('syllabus-unit-number').value;
    const unitName = document.getElementById('syllabus-unit-name').value;
    const topics = document.getElementById('syllabus-topics').value;
    const learningOutcomes = document.getElementById('syllabus-outcomes').value;

    try {
        const response = await fetch(`${API_BASE_URL}/upload/syllabus`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                subject_id: parseInt(subjectId),
                unit_number: parseInt(unitNumber),
                unit_name: unitName,
                topics: topics,
                learning_outcomes: learningOutcomes
            })
        });

        const data = await response.json();

        if (data.success) {
            showToast('Syllabus unit added successfully!', 'success');
            e.target.reset();

            // Reload syllabus if viewing that subject
            const currentSubject = document.getElementById('syllabus-subject-filter').value;
            if (currentSubject === subjectId) {
                loadSyllabus(parseInt(subjectId));
            }
        } else {
            throw new Error(data.error || 'Upload failed');
        }
    } catch (error) {
        console.error('Syllabus upload error:', error);
        showToast('Upload failed: ' + error.message, 'error');
    }
}

// Question Upload
async function handleQuestionSubmit(e) {
    e.preventDefault();

    const subjectId = document.getElementById('question-subject').value;
    const unitNumber = document.getElementById('question-unit').value;
    const questionType = document.getElementById('question-type').value;
    const difficulty = document.getElementById('question-difficulty').value;
    const questionText = document.getElementById('question-text').value;
    const answer = document.getElementById('question-answer').value;

    try {
        const response = await fetch(`${API_BASE_URL}/upload/question`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                subject_id: parseInt(subjectId),
                unit_number: unitNumber ? parseInt(unitNumber) : null,
                question_type: questionType,
                difficulty: difficulty,
                question: questionText,
                answer: answer
            })
        });

        const data = await response.json();

        if (data.success) {
            showToast('Question added successfully!', 'success');
            e.target.reset();

            // Reload questions
            loadImportantQuestions();
        } else {
            throw new Error(data.error || 'Upload failed');
        }
    } catch (error) {
        console.error('Question upload error:', error);
        showToast('Upload failed: ' + error.message, 'error');
    }
}

// Utility Functions
function showEmptyState(containerId, message) {
    const container = document.getElementById(containerId);
    container.innerHTML = `
        <div class="empty-state">
            <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <circle cx="12" cy="12" r="10"></circle>
                <line x1="12" y1="8" x2="12" y2="12"></line>
                <line x1="12" y1="16" x2="12.01" y2="16"></line>
            </svg>
            <h3>${escapeHtml(message)}</h3>
        </div>
    `;
}

function showToast(message, type = 'info') {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.className = `toast ${type} show`;

    setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// ==================== ADMIN AUTHENTICATION ====================

async function checkAdminAuth() {
    const sessionToken = localStorage.getItem('admin_session');

    if (!sessionToken) {
        updateAdminUI(false);
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/admin/check-auth`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ session_token: sessionToken })
        });

        const data = await response.json();

        if (data.authenticated) {
            isAdmin = true;
            adminEmail = data.email;
            adminSessionToken = sessionToken;
            updateAdminUI(true);
        } else {
            localStorage.removeItem('admin_session');
            localStorage.removeItem('admin_email');
            updateAdminUI(false);
        }
    } catch (error) {
        console.error('Auth check failed:', error);
        updateAdminUI(false);
    }
}

function updateAdminUI(authenticated) {
    const adminBtn = document.getElementById('admin-btn');
    const adminBtnText = document.getElementById('admin-btn-text');
    const uploadTabBtn = document.getElementById('upload-tab-btn');

    if (authenticated) {
        adminBtnText.textContent = 'Logout';
        adminBtn.classList.add('admin-logged-in');
        uploadTabBtn.style.display = 'flex';  // Show upload tab for admins

        // Reload materials to show delete buttons
        loadMaterials();
        loadImportantQuestions();
    } else {
        adminBtnText.textContent = 'Admin';
        adminBtn.classList.remove('admin-logged-in');
        uploadTabBtn.style.display = 'none';  // Hide upload tab
    }
}

function handleAdminClick() {
    if (isAdmin) {
        // Logout
        if (confirm('Are you sure you want to logout?')) {
            logout();
        }
    } else {
        // Redirect to login page
        window.location.href = 'admin-login.html';
    }
}

async function logout() {
    try {
        await fetch(`${API_BASE_URL}/admin/logout`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ session_token: adminSessionToken })
        });
    } catch (error) {
        console.error('Logout error:', error);
    }

    // Clear local storage
    localStorage.removeItem('admin_session');
    localStorage.removeItem('admin_email');

    // Reset state
    isAdmin = false;
    adminEmail = '';
    adminSessionToken = '';

    // Update UI
    updateAdminUI(false);
    showToast('Logged out successfully', 'success');
}

// ==================== ADMIN DELETE FUNCTIONS ====================

async function deleteMaterial(materialId, title) {
    if (!isAdmin) {
        showToast('Admin access required', 'error');
        return;
    }

    if (!confirm(`Are you sure you want to delete "${title}"?`)) {
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/admin/materials/${materialId}`, {
            method: 'DELETE',
            headers: {
                'X-Session-Token': adminSessionToken
            }
        });

        const data = await response.json();

        if (data.success) {
            showToast('Material deleted successfully', 'success');
            loadMaterials();  // Reload materials
        } else {
            showToast(data.error || 'Delete failed', 'error');
        }
    } catch (error) {
        console.error('Delete error:', error);
        showToast('Delete failed', 'error');
    }
}

async function deleteSyllabus(syllabusId, unitName) {
    if (!isAdmin) {
        showToast('Admin access required', 'error');
        return;
    }

    if (!confirm(`Are you sure you want to delete "${unitName}"?`)) {
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/admin/syllabus/${syllabusId}`, {
            method: 'DELETE',
            headers: {
                'X-Session-Token': adminSessionToken
            }
        });

        const data = await response.json();

        if (data.success) {
            showToast('Syllabus deleted successfully', 'success');
            const subjectId = document.getElementById('syllabus-subject-filter').value;
            if (subjectId) {
                loadSyllabus(parseInt(subjectId));
            }
        } else {
            showToast(data.error || 'Delete failed', 'error');
        }
    } catch (error) {
        console.error('Delete error:', error);
        showToast('Delete failed', 'error');
    }
}

async function deleteQuestion(questionId, questionText) {
    if (!isAdmin) {
        showToast('Admin access required', 'error');
        return;
    }

    const shortText = questionText.substring(0, 50) + '...';
    if (!confirm(`Are you sure you want to delete this question?\n\n"${shortText}"`)) {
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/admin/questions/${questionId}`, {
            method: 'DELETE',
            headers: {
                'X-Session-Token': adminSessionToken
            }
        });

        const data = await response.json();

        if (data.success) {
            showToast('Question deleted successfully', 'success');
            loadImportantQuestions();  // Reload questions
        } else {
            showToast(data.error || 'Delete failed', 'error');
        }
    } catch (error) {
        console.error('Delete error:', error);
        showToast('Delete failed', 'error');
    }
}
