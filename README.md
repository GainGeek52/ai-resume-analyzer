# 📄 AI-Powered Resume Analyzer

An intelligent Streamlit web application that analyzes PDF resumes and provides comprehensive feedback with actionable improvement suggestions. Perfect for job seekers looking to optimize their resumes for better ATS compatibility and recruiter appeal.

## 🚀 Live Demo

[Try the live demo here](https://your-app-url.streamlit.app) *(Deploy to get your URL)*

## ✨ Features

### 📊 Comprehensive Scoring System (100 Points Total)
- **Keywords & Skills Analysis** (30 pts) - Evaluates technical and soft skills density
- **Readability Assessment** (25 pts) - Ensures professional, scannable language  
- **Section Completeness** (25 pts) - Verifies essential resume components
- **Length Optimization** (20 pts) - Checks for appropriate resume length

### 🔍 Advanced Analysis Engine
- **Smart PDF Processing** - Extracts text from any PDF resume format
- **NLP-Powered Keyword Detection** - Identifies 50+ technical and soft skills
- **Multi-Metric Readability** - Uses Flesch Reading Ease and grade-level analysis
- **Section Intelligence** - Automatically detects standard resume sections
- **Length Analytics** - Optimal word count analysis (300-800 words ideal)

### 💡 Actionable Insights
- **Personalized Suggestions** - Tailored improvement recommendations
- **Visual Score Breakdown** - Interactive progress bars and metrics
- **Missing Section Alerts** - Identifies gaps in resume structure
- **Real-Time Processing** - Analysis completed in under 5 seconds
- **Text Preview** - Transparent extraction preview

### 🎯 Professional UI/UX
- **Clean Interface** - Intuitive, distraction-free design
- **Mobile Responsive** - Works perfectly on all devices
- **Error Handling** - Graceful handling of malformed PDFs
- **Progress Indicators** - Clear feedback during processing
- **Accessibility** - WCAG compliant design

## 🛠️ Tech Stack

- **Frontend**: Streamlit (Python web framework)
- **PDF Processing**: pdfplumber (robust PDF text extraction)
- **NLP Analysis**: textstat (readability metrics)
- **Data Processing**: Python collections, regex
- **Deployment**: Streamlit Cloud ready

## 📦 Installation

### Quick Start
```bash
# Clone the repository
git clone https://github.com/yourusername/ai-resume-analyzer.git
cd ai-resume-analyzer

# Install dependencies
pip install -r requirements.txt

# Run the application
streamlit run app.py
```

### Alternative Installation (with uv)
```bash
# Install uv (fast Python package manager)
pip install uv

# Install dependencies
uv add streamlit pdfplumber textstat

# Run the application
streamlit run app.py
```

## 🖥️ Usage

1. **Upload Resume**: Click "Browse files" and select your PDF resume
2. **Wait for Analysis**: The app will process your resume in 3-5 seconds
3. **Review Score**: Get your overall score out of 100 points
4. **Read Suggestions**: Follow personalized improvement recommendations
5. **Check Details**: Expand sections for detailed analysis

## 📊 Scoring Breakdown

| Component | Max Points | What It Measures |
|-----------|------------|------------------|
| Keywords & Skills | 30 | Technical skills, programming languages, soft skills density |
| Readability | 25 | Professional language, clarity, ATS compatibility |
| Section Completeness | 25 | Contact info, experience, education, skills, projects |
| Length Optimization | 20 | Word count optimization (300-800 words ideal) |

## 🎯 Sample Results

**Before Optimization**: 45/100
- Missing technical keywords
- No projects section
- Too brief (180 words)

**After Following Suggestions**: 78/100
- Added relevant skills
- Included projects section
- Expanded experience details

## 📁 Project Structure

```
ai-resume-analyzer/
├── app.py                 # Main Streamlit application
├── .streamlit/
│   └── config.toml        # Streamlit configuration
├── README.md              # Project documentation
├── pyproject.toml         # Python project configuration
├── .gitignore            # Git ignore file
└── requirements.txt       # Python dependencies (if created manually)
```

## 🚀 Deployment

### Streamlit Cloud (Recommended)
1. Fork this repository to your GitHub account
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repository
4. Deploy with one click!

### Local Development
```bash
# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies and run
pip install streamlit pdfplumber textstat
streamlit run app.py
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔮 Future Enhancements

- [ ] Support for DOCX files
- [ ] Job description comparison
- [ ] ATS compatibility scoring
- [ ] Multiple resume formats
- [ ] Export analysis reports
- [ ] Resume templates suggestions
- [ ] Industry-specific keyword analysis

## 📧 Contact

If you have questions or suggestions, feel free to open an issue or reach out!

---

**Built with ❤️ using Streamlit • Perfect for job seekers and career professionals**
