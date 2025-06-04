import streamlit as st
import pdfplumber
import textstat
from collections import Counter
import re
import io

# --- Page Configuration ---
st.set_page_config(
    page_title="AI Resume Analyzer",
    page_icon="📄",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- Main Title ---
st.title("📄 AI-Powered Resume Analyzer")
st.markdown("**Upload your resume and get instant feedback with actionable improvement suggestions**")
st.markdown("---")

# --- File Upload Section ---
uploaded_file = st.file_uploader(
    "Upload your resume (PDF format only)", 
    type=["pdf"],
    help="Select a PDF file containing your resume for analysis"
)

# --- Utility Functions ---
def extract_text_from_pdf(pdf_file):
    """
    Extract text content from PDF file using pdfplumber
    """
    try:
        text = ""
        with pdfplumber.open(pdf_file) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        return text.strip()
    except Exception as e:
        st.error(f"Error extracting text from PDF: {str(e)}")
        return ""

def get_keyword_score(text):
    """
    Analyze keyword density for job-relevant terms
    Returns score out of 30 points
    """
    # Expanded keyword categories for better analysis
    technical_keywords = [
        "python", "java", "javascript", "sql", "html", "css", "react", "angular", "vue",
        "node.js", "mongodb", "postgresql", "mysql", "git", "docker", "kubernetes",
        "aws", "azure", "gcp", "machine learning", "data analysis", "artificial intelligence",
        "deep learning", "tensorflow", "pytorch", "pandas", "numpy", "scikit-learn"
    ]
    
    soft_skills = [
        "leadership", "teamwork", "communication", "problem solving", "analytical",
        "project management", "collaboration", "mentoring", "strategic planning",
        "critical thinking", "adaptability", "innovation", "creativity"
    ]
    
    all_keywords = technical_keywords + soft_skills
    
    # Clean and tokenize text
    words = re.findall(r"\b\w+\b", text.lower())
    word_freq = Counter(words)
    
    # Calculate keyword matches
    keyword_matches = sum([word_freq.get(keyword, 0) for keyword in all_keywords])
    unique_keywords_found = sum([1 for keyword in all_keywords if keyword in words])
    
    # Scoring: base score + bonus for diversity
    base_score = min(keyword_matches * 0.8, 20)  # Max 20 from frequency
    diversity_bonus = min(unique_keywords_found * 0.5, 10)  # Max 10 for diversity
    
    return min(base_score + diversity_bonus, 30)

def get_readability_score(text):
    """
    Assess text readability and complexity
    Returns score out of 25 points
    """
    try:
        if len(text.strip()) < 50:
            return 0
            
        # Multiple readability metrics
        flesch_score = textstat.flesch_reading_ease(text)
        flesch_kincaid = textstat.flesch_kincaid_grade(text)
        
        # Optimal range for professional documents: 60-70 Flesch score
        if 60 <= flesch_score <= 70:
            readability_points = 25
        elif 50 <= flesch_score < 60 or 70 < flesch_score <= 80:
            readability_points = 20
        elif 40 <= flesch_score < 50 or 80 < flesch_score <= 90:
            readability_points = 15
        else:
            readability_points = 10
            
        return readability_points
        
    except Exception as e:
        st.warning(f"Could not calculate readability score: {str(e)}")
        return 15  # Default moderate score

def check_sections(text):
    """
    Check for presence of essential resume sections
    Returns score out of 25 points
    """
    essential_sections = {
        "contact": ["email", "phone", "linkedin", "contact"],
        "experience": ["experience", "work", "employment", "career", "professional"],
        "education": ["education", "degree", "university", "college", "school"],
        "skills": ["skills", "technologies", "proficient", "expertise", "competencies"],
        "projects": ["projects", "portfolio", "achievements", "accomplishments"]
    }
    
    text_lower = text.lower()
    sections_found = 0
    section_details = {}
    
    for section_name, keywords in essential_sections.items():
        found = any(keyword in text_lower for keyword in keywords)
        section_details[section_name] = found
        if found:
            sections_found += 1
    
    # Score calculation: 5 points per essential section
    section_score = (sections_found / len(essential_sections)) * 25
    
    return section_score, section_details

def get_length_score(text):
    """
    Evaluate resume length appropriateness
    Returns score out of 20 points
    """
    word_count = len(text.split())
    
    if 300 <= word_count <= 800:  # Optimal range
        return 20
    elif 200 <= word_count < 300 or 800 < word_count <= 1200:  # Good range
        return 15
    elif 100 <= word_count < 200 or 1200 < word_count <= 1500:  # Acceptable
        return 10
    else:  # Too short or too long
        return 5

def generate_suggestions(keyword_score, readability_score, section_score, section_details, length_score, word_count):
    """
    Generate personalized improvement suggestions
    """
    suggestions = []
    
    # Keyword suggestions
    if keyword_score < 15:
        suggestions.append({
            "type": "warning",
            "title": "⚠️ Low Keyword Density",
            "message": "Consider adding more relevant technical skills and industry keywords. Include specific technologies, programming languages, and tools you've used."
        })
    elif keyword_score < 25:
        suggestions.append({
            "type": "info",
            "title": "💡 Keyword Optimization",
            "message": "Good keyword usage! You could enhance it further by adding more specific technical skills and soft skills relevant to your target role."
        })
    
    # Readability suggestions
    if readability_score < 15:
        suggestions.append({
            "type": "warning",
            "title": "📖 Readability Concerns",
            "message": "Your resume might be too complex or too simple. Aim for clear, professional language that's easy to scan quickly."
        })
    
    # Section suggestions
    missing_sections = [section for section, found in section_details.items() if not found]
    if missing_sections:
        suggestions.append({
            "type": "error",
            "title": "📋 Missing Sections",
            "message": f"Consider adding these important sections: {', '.join(missing_sections).title()}"
        })
    
    # Length suggestions
    if length_score < 15:
        if word_count < 300:
            suggestions.append({
                "type": "info",
                "title": "📏 Resume Length",
                "message": "Your resume seems quite brief. Consider adding more details about your experiences, achievements, and skills."
            })
        elif word_count > 1200:
            suggestions.append({
                "type": "info",
                "title": "📏 Resume Length",
                "message": "Your resume is quite lengthy. Consider condensing information and focusing on the most relevant and impactful details."
            })
    
    return suggestions

# --- Main Application Logic ---
if uploaded_file is not None:
    try:
        # Show processing indicator
        with st.spinner("🔍 Analyzing your resume... This may take a few seconds."):
            # Extract text from PDF
            raw_text = extract_text_from_pdf(uploaded_file)
            
            if not raw_text:
                st.error("❌ Could not extract text from the PDF. Please ensure the file is not corrupted and contains readable text.")
                st.stop()
            
            # Calculate individual scores
            keyword_score = get_keyword_score(raw_text)
            readability_score = get_readability_score(raw_text)
            section_score, section_details = check_sections(raw_text)
            length_score = get_length_score(raw_text)
            
            # Calculate total score
            total_score = round(keyword_score + readability_score + section_score + length_score, 1)
            word_count = len(raw_text.split())
        
        # Display Results
        st.success("✅ Analysis Complete!")
        st.markdown("---")
        
        # Main Score Display
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.metric(
                label="📊 Overall Resume Score",
                value=f"{total_score}/100",
                delta=f"{total_score - 70:.1f} vs. target (70+)" if total_score != 70 else None
            )
        
        st.markdown("---")
        
        # Detailed Score Breakdown
        st.subheader("📈 Detailed Score Breakdown")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("🔍 Keywords & Skills", f"{keyword_score:.1f}/30")
            st.metric("📖 Readability", f"{readability_score:.1f}/25")
        
        with col2:
            st.metric("📋 Section Completeness", f"{section_score:.1f}/25")
            st.metric("📏 Length Appropriateness", f"{length_score:.1f}/20")
        
        # Progress bars for visual representation
        st.markdown("#### Score Visualization")
        st.progress(keyword_score / 30, text=f"Keywords: {keyword_score:.1f}/30")
        st.progress(readability_score / 25, text=f"Readability: {readability_score:.1f}/25")
        st.progress(section_score / 25, text=f"Sections: {section_score:.1f}/25")
        st.progress(length_score / 20, text=f"Length: {length_score:.1f}/20")
        
        st.markdown("---")
        
        # Generate and display suggestions
        suggestions = generate_suggestions(
            keyword_score, readability_score, section_score, 
            section_details, length_score, word_count
        )
        
        st.subheader("💡 Personalized Improvement Suggestions")
        
        if suggestions:
            for suggestion in suggestions:
                if suggestion["type"] == "error":
                    st.error(f"**{suggestion['title']}**\n\n{suggestion['message']}")
                elif suggestion["type"] == "warning":
                    st.warning(f"**{suggestion['title']}**\n\n{suggestion['message']}")
                else:
                    st.info(f"**{suggestion['title']}**\n\n{suggestion['message']}")
        else:
            st.success("🎉 **Excellent work!** Your resume looks well-optimized. Keep up the great work!")
        
        # Additional Insights
        st.markdown("---")
        st.subheader("📊 Additional Insights")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Word Count", word_count)
        with col2:
            st.metric("Sections Found", f"{sum(section_details.values())}/{len(section_details)}")
        with col3:
            character_count = len(raw_text)
            st.metric("Character Count", character_count)
        
        # Section checklist
        st.markdown("#### ✅ Section Checklist")
        for section, found in section_details.items():
            status = "✅" if found else "❌"
            st.write(f"{status} {section.title()}")
        
        # Text preview
        with st.expander("📄 View Extracted Resume Text", expanded=False):
            st.text_area(
                "Extracted Text (First 2000 characters):",
                raw_text[:2000] + ("..." if len(raw_text) > 2000 else ""),
                height=300,
                disabled=True
            )
            st.info(f"Showing first 2000 characters of {len(raw_text)} total characters extracted.")
    
    except Exception as e:
        st.error(f"❌ An error occurred while analyzing your resume: {str(e)}")
        st.info("Please try uploading a different PDF file or contact support if the issue persists.")

else:
    # Welcome message and instructions
    st.info("👆 Please upload your resume in PDF format to get started with the analysis.")
    
    st.markdown("### 🎯 What This Tool Analyzes:")
    st.markdown("""
    - **Keywords & Skills**: Checks for relevant technical and soft skills
    - **Readability**: Ensures your resume is clear and professional
    - **Section Completeness**: Verifies essential resume sections are present
    - **Length Appropriateness**: Evaluates if your resume is the right length
    """)
    
    st.markdown("### 🚀 How to Get the Best Results:")
    st.markdown("""
    1. Upload a clean, well-formatted PDF resume
    2. Ensure your resume includes standard sections (Experience, Education, Skills, etc.)
    3. Use relevant keywords for your target industry
    4. Keep content professional and easy to read
    """)

# Footer
st.markdown("---")
st.markdown("*Built with ❤️ using Streamlit • AI-Powered Resume Analysis*")
