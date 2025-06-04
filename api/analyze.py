from http.server import BaseHTTPRequestHandler
import json
import cgi
import io
import pdfplumber
import textstat
from collections import Counter
import re

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            # Parse multipart form data
            content_type = self.headers.get('content-type')
            if not content_type or 'multipart/form-data' not in content_type:
                self.send_error(400, "Invalid content type")
                return

            # Get boundary from content-type header
            boundary = content_type.split('boundary=')[1].encode()
            
            # Read the form data
            content_length = int(self.headers.get('Content-Length', 0))
            form_data = self.rfile.read(content_length)
            
            # Extract PDF file from form data
            pdf_data = self.extract_pdf_from_form(form_data, boundary)
            
            if not pdf_data:
                self.send_json_response({'error': 'No PDF file found'}, 400)
                return

            # Analyze the resume
            result = self.analyze_resume(pdf_data)
            
            # Send response
            self.send_json_response(result)
            
        except Exception as e:
            self.send_json_response({'error': f'Server error: {str(e)}'}, 500)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def extract_pdf_from_form(self, form_data, boundary):
        try:
            # Split form data by boundary
            parts = form_data.split(b'--' + boundary)
            
            for part in parts:
                if b'filename=' in part and b'.pdf' in part:
                    # Find the start of file content
                    header_end = part.find(b'\r\n\r\n')
                    if header_end != -1:
                        file_content = part[header_end + 4:]
                        # Remove trailing boundary markers
                        if file_content.endswith(b'\r\n'):
                            file_content = file_content[:-2]
                        return io.BytesIO(file_content)
            return None
        except:
            return None

    def analyze_resume(self, pdf_data):
        # Extract text from PDF
        text = self.extract_text_from_pdf(pdf_data)
        if not text:
            return {'error': 'Could not extract text from PDF'}

        # Calculate scores
        keyword_score = self.get_keyword_score(text)
        readability_score = self.get_readability_score(text)
        section_score, section_details = self.check_sections(text)
        length_score = self.get_length_score(text)
        
        total_score = round(keyword_score + readability_score + section_score + length_score, 1)
        word_count = len(text.split())
        
        # Generate suggestions
        suggestions = self.generate_suggestions(
            keyword_score, readability_score, section_score, 
            section_details, length_score, word_count
        )
        
        return {
            'total_score': total_score,
            'keyword_score': round(keyword_score, 1),
            'readability_score': round(readability_score, 1),
            'section_score': round(section_score, 1),
            'length_score': round(length_score, 1),
            'word_count': word_count,
            'section_details': section_details,
            'suggestions': suggestions,
            'text_preview': text[:500] + "..." if len(text) > 500 else text
        }

    def extract_text_from_pdf(self, pdf_file):
        try:
            text = ""
            with pdfplumber.open(pdf_file) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            return text.strip()
        except:
            return ""

    def get_keyword_score(self, text):
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
        words = re.findall(r"\b\w+\b", text.lower())
        word_freq = Counter(words)
        
        keyword_matches = sum([word_freq.get(keyword, 0) for keyword in all_keywords])
        unique_keywords_found = sum([1 for keyword in all_keywords if keyword in words])
        
        base_score = min(keyword_matches * 0.8, 20)
        diversity_bonus = min(unique_keywords_found * 0.5, 10)
        
        return min(base_score + diversity_bonus, 30)

    def get_readability_score(self, text):
        try:
            if len(text.strip()) < 50:
                return 0
                
            flesch_score = textstat.flesch_reading_ease(text)
            
            if 60 <= flesch_score <= 70:
                return 25
            elif 50 <= flesch_score < 60 or 70 < flesch_score <= 80:
                return 20
            elif 40 <= flesch_score < 50 or 80 < flesch_score <= 90:
                return 15
            else:
                return 10
        except:
            return 15

    def check_sections(self, text):
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
        
        section_score = (sections_found / len(essential_sections)) * 25
        return section_score, section_details

    def get_length_score(self, text):
        word_count = len(text.split())
        
        if 300 <= word_count <= 800:
            return 20
        elif 200 <= word_count < 300 or 800 < word_count <= 1200:
            return 15
        elif 100 <= word_count < 200 or 1200 < word_count <= 1500:
            return 10
        else:
            return 5

    def generate_suggestions(self, keyword_score, readability_score, section_score, section_details, length_score, word_count):
        suggestions = []
        
        if keyword_score < 15:
            suggestions.append({
                "type": "warning",
                "title": "Low Keyword Density",
                "message": "Consider adding more relevant technical skills and industry keywords. Include specific technologies, programming languages, and tools you've used."
            })
        elif keyword_score < 25:
            suggestions.append({
                "type": "info",
                "title": "Keyword Optimization",
                "message": "Good keyword usage! You could enhance it further by adding more specific technical skills and soft skills relevant to your target role."
            })
        
        if readability_score < 15:
            suggestions.append({
                "type": "warning",
                "title": "Readability Concerns",
                "message": "Your resume might be too complex or too simple. Aim for clear, professional language that's easy to scan quickly."
            })
        
        missing_sections = [section for section, found in section_details.items() if not found]
        if missing_sections:
            suggestions.append({
                "type": "error",
                "title": "Missing Sections",
                "message": f"Consider adding these important sections: {', '.join(missing_sections).title()}"
            })
        
        if length_score < 15:
            if word_count < 300:
                suggestions.append({
                    "type": "info",
                    "title": "Resume Length",
                    "message": "Your resume seems quite brief. Consider adding more details about your experiences, achievements, and skills."
                })
            elif word_count > 1200:
                suggestions.append({
                    "type": "info",
                    "title": "Resume Length",
                    "message": "Your resume is quite lengthy. Consider condensing information and focusing on the most relevant and impactful details."
                })
        
        return suggestions

    def send_json_response(self, data, status_code=200):
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())