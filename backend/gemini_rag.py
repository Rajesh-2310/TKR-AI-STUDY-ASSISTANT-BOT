"""
Gemini-powered RAG Engine for TKR Chatbot
Uses Google's Gemini AI with retrieval augmented generation
"""
from sentence_transformers import SentenceTransformer
import numpy as np
import json
from database import get_db
import logging
import google.generativeai as genai
import os
from dotenv import load_dotenv

# Force reload .env to avoid caching issues
load_dotenv(override=True)

logger = logging.getLogger(__name__)

class GeminiRAGEngine:
    """RAG Engine using Gemini AI for answer generation"""
    
    def __init__(self, model_name='all-MiniLM-L6-v2', gemini_api_key=None):
        """Initialize RAG engine with embedding model and Gemini"""
        try:
            # Load embedding model for semantic search
            self.embedding_model = SentenceTransformer(model_name)
            logger.info(f"Loaded embedding model: {model_name}")
            
            # Configure Gemini - force reload env vars
            load_dotenv(override=True)
            api_key = gemini_api_key or os.getenv('GEMINI_API_KEY')
            if not api_key:
                raise ValueError("GEMINI_API_KEY not found in environment")
            
            genai.configure(api_key=api_key)
            self.gemini_model = genai.GenerativeModel(os.getenv('GEMINI_MODEL', 'gemini-pro'))
            logger.info("Initialized Gemini AI model")
            
        except Exception as e:
            logger.error(f"Failed to initialize Gemini RAG engine: {e}")
            raise
    
    def generate_embedding(self, text):
        """Generate embedding vector for text"""
        try:
            embedding = self.embedding_model.encode(text, convert_to_numpy=True)
            return embedding.tolist()
        except Exception as e:
            logger.error(f"Embedding generation failed: {e}")
            raise
    
    def store_embeddings(self, material_id, chunks):
        """Store document chunks and their embeddings"""
        try:
            db = get_db()
            embeddings_data = []
            
            for idx, chunk in enumerate(chunks):
                embedding = self.generate_embedding(chunk['text'])
                embeddings_data.append((
                    material_id,
                    chunk['text'],
                    idx,
                    chunk.get('page', 0),
                    json.dumps(embedding)
                ))
            
            query = """
                INSERT INTO document_embeddings 
                (material_id, chunk_text, chunk_index, page_number, embedding_vector)
                VALUES (%s, %s, %s, %s, %s)
            """
            
            db.execute_many(query, embeddings_data)
            logger.info(f"Stored {len(embeddings_data)} embeddings for material {material_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to store embeddings: {e}")
            raise
    
    def cosine_similarity(self, vec1, vec2):
        """Calculate cosine similarity between two vectors"""
        vec1 = np.array(vec1)
        vec2 = np.array(vec2)
        return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
    
    def search_similar_chunks(self, query, subject_id=None, top_k=5):
        """Search for most similar document chunks"""
        try:
            db = get_db()
            
            # Generate query embedding
            query_embedding = self.generate_embedding(query)
            
            # Get all embeddings (with optional subject filter)
            if subject_id:
                sql = """
                    SELECT de.*, m.title, m.subject_id
                    FROM document_embeddings de
                    JOIN materials m ON de.material_id = m.id
                    WHERE m.subject_id = %s
                """
                embeddings = db.execute_query(sql, (subject_id,))
            else:
                sql = """
                    SELECT de.*, m.title, m.subject_id
                    FROM document_embeddings de
                    JOIN materials m ON de.material_id = m.id
                """
                embeddings = db.execute_query(sql)
            
            # Calculate similarities
            results = []
            for emb in embeddings:
                stored_embedding = json.loads(emb['embedding_vector'])
                
                # Skip empty embeddings
                if not stored_embedding or len(stored_embedding) == 0:
                    continue
                
                similarity = self.cosine_similarity(query_embedding, stored_embedding)
                
                results.append({
                    'chunk_text': emb['chunk_text'],
                    'page_number': emb['page_number'],
                    'material_id': emb['material_id'],
                    'material_title': emb['title'],
                    'similarity': float(similarity)
                })
            
            # Sort by similarity and return top k
            results.sort(key=lambda x: x['similarity'], reverse=True)
            return results[:top_k]
            
        except Exception as e:
            logger.error(f"Similarity search failed: {e}")
            return []
    
    def generate_answer_with_gemini(self, query, context_chunks):
        """Generate answer using Gemini AI with retrieved context"""
        try:
            if not context_chunks:
                # No context found - alert about missing content
                prompt = f"""Act as a Senior Engineering Professor and Exam Evaluator at TKR College of Engineering and Technology.

Student's Question: {query}

⚠️ IMPORTANT: No relevant content was found in the uploaded study materials (syllabus, notes, PDFs, or PYQs).

FORMATTING REQUIREMENTS:
- Use markdown formatting with headers (##, ###)
- Use emojis to make it engaging (📚, 🎓, ⚡, 💡, etc.)
- Use bullet points and numbered lists
- Use **bold** for key terms
- Use `code blocks` for technical terms
- Create clear visual hierarchy

Response Structure:
1. Start with: "## ⚠️ Topic Not Found in Your Materials"
2. Explain what's missing
3. Ask: "### 🤔 Would you like me to provide standard reference material?"
4. If providing answer, use this structure:
   - ## 📖 Definition
   - ## 🔍 Detailed Explanation  
   - ## 📝 Key Points
   - ## 📐 Formulas (in LaTeX: $$formula$$)
   - ## ✅ Advantages/Applications

Generate a beautifully formatted response:"""
                
                response = self.gemini_model.generate_content(prompt)
                return {
                    'answer': response.text,
                    'sources': [],
                    'confidence': 0.3
                }
            
            # Combine context from retrieved chunks with source citations
            context_parts = []
            for chunk in context_chunks:
                source_ref = f"[Ref: {chunk['material_title']}, Page {chunk['page_number']}]"
                context_parts.append(f"{source_ref}:\n{chunk['chunk_text']}")
            
            context = "\n\n---\n\n".join(context_parts)
            
            # Calculate average confidence
            avg_confidence = sum(chunk['similarity'] for chunk in context_chunks) / len(context_chunks)
            
            # Create enhanced prompt for conversational, direct answers like ChatGPT/Gemini
            prompt = f"""You are a helpful AI tutor for TKR College of Engineering and Technology students. Answer questions directly and conversationally using the knowledge from the provided study materials.

CORE PRINCIPLES:
1. **Answer directly** - Don't say "According to the material..." or "The PDF states...". Just answer the question naturally.
2. **Use source knowledge** - Base your answer ONLY on the provided materials, but present it as if you're explaining it yourself.
3. **Be conversational** - Write like ChatGPT or Gemini would - clear, friendly, and helpful.
4. **Always cite sources** - Include source references at the end (this is MANDATORY, not optional).
5. **Beautiful formatting** - Use markdown, emojis, and structure to make answers engaging.

STUDY MATERIALS PROVIDED:
{context}

STUDENT'S QUESTION: {query}

RESPONSE GUIDELINES:

**Tone & Style:**
- Write naturally and conversationally (like explaining to a friend)
- Don't describe what's in the PDF - just answer the question directly
- Use "we", "let's", "you can" to make it engaging
- Be clear, concise, and helpful

**Formatting (Make it beautiful like ChatGPT/Gemini):**
- Use ## for main sections with emojis (📖, 🔍, 💡, ⚡, 📝, ✅, 🎯, 📊)
- Use ### for subsections
- **Bold** for key terms and important concepts
- `code style` for technical terms, formulas, variable names
- > blockquotes for important definitions or notes
- Numbered lists for steps/procedures
- Bullet points (•) for features/characteristics
- Tables for comparisons (when helpful)
- LaTeX for ALL mathematical formulas: $$formula$$
- Horizontal rules (---) between major sections

**Structure your answer naturally:**

Start with a clear, direct answer to the question. Then elaborate with:

## 📖 Core Concept
[Explain the main concept directly - no "according to..." just explain it]

## 🔍 Detailed Explanation
[Break down the concept step-by-step in a natural, conversational way]

## 💡 Key Points to Remember
• **Point 1**: Brief explanation
• **Point 2**: Brief explanation
• **Point 3**: Brief explanation

## 📐 Formulas (if applicable)
$$formula$$

Where:
- Variable: meaning
- Variable: meaning

## ✅ Applications/Advantages (if applicable)
[Explain where/how this is used]

## 🎯 Exam Tips (if relevant)
[Quick tips for answering this in exams]

---

## 📚 Sources
**Referenced from:**
- Material: [Name], Pages: [X, Y, Z]
- Unit/Chapter: [If mentioned]

**CRITICAL RULES:**
- ❌ DON'T say "The material states..." or "According to page X..."
- ✅ DO answer directly: "Machine learning is a method where..."
- ❌ DON'T describe the PDF content
- ✅ DO use the PDF knowledge to answer naturally
- ✅ ALWAYS include source references at the end (MANDATORY)
- ✅ If something is NOT in the materials, clearly state: "⚠️ This topic is not covered in your uploaded materials"

Generate a helpful, beautifully formatted answer:"""
            
            # Generate response with Gemini
            response = self.gemini_model.generate_content(prompt)
            
            # Extract sources
            sources = []
            for chunk in context_chunks:
                source_info = {
                    'material': chunk['material_title'],
                    'page': chunk['page_number'],
                    'material_id': chunk['material_id']
                }
                if source_info not in sources:
                    sources.append(source_info)
            
            return {
                'answer': response.text,
                'sources': sources,
                'confidence': float(avg_confidence),
                'context_chunks': context_chunks
            }
            
        except Exception as e:
            logger.error(f"Gemini answer generation failed: {e}")
            return {
                'answer': f"I encountered an error while generating the answer: {str(e)}",
                'sources': [],
                'confidence': 0.0
            }
    
    def answer_question(self, question, subject_id=None, top_k=5):
        """Complete RAG pipeline: retrieve and generate answer with Gemini"""
        try:
            # Search for relevant chunks
            similar_chunks = self.search_similar_chunks(question, subject_id, top_k)
            
            # Generate answer using Gemini
            result = self.generate_answer_with_gemini(question, similar_chunks)
            
            return result
            
        except Exception as e:
            logger.error(f"Question answering failed: {e}")
            return {
                'answer': "An error occurred while processing your question. Please try again.",
                'sources': [],
                'confidence': 0.0
            }

# Global Gemini RAG engine instance
gemini_rag_engine = None

def get_gemini_rag_engine():
    """Get or create Gemini RAG engine instance"""
    global gemini_rag_engine
    if gemini_rag_engine is None:
        gemini_rag_engine = GeminiRAGEngine()
    return gemini_rag_engine
