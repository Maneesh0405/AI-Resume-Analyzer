import PyPDF2
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re

# Load English tokenizer, tagger, parser and NER
nlp = spacy.load("en_core_web_sm")

JOB_DESCRIPTIONS = {
    "software_engineer": """
        We are looking for a Software Engineer with experience in Python, Java, or C++.
        Knowledge of web frameworks like Django, Flask, or Spring Boot is required.
        Experience with databases (SQL, NoSQL), Git, and cloud services (AWS, Azure, GCP) is a plus.
        Strong problem-solving skills, data structures, algorithms, and object-oriented design.
        Agile methodologies, CI/CD, and Docker/Kubernetes containerization.
    """,
    "data_scientist": """
        Seeking a Data Scientist proficient in Python, R, and SQL.
        Experience with machine learning libraries such as Scikit-learn, TensorFlow, PyTorch, Keras, and Pandas.
        Strong background in statistics, deep learning, NLP, and data visualization (Tableau, PowerBI, Matplotlib).
        Ability to build predictive models, design experiments, and perform A/B testing.
        Data mining and feature engineering skills are essential.
    """,
    "frontend_developer": """
        Frontend Developer needed with expertise in HTML, CSS, JavaScript, and TypeScript.
        Experience with modern frameworks like React, Angular, or Vue.js.
        Knowledge of state management (Redux, Context API), responsive design, UI/UX principles, and CSS preprocessors (SASS, LESS).
        Familiarity with Webpack, Babel, REST APIs, and version control (Git).
        Cross-browser compatibility testing and performance optimization.
    """,
    "marketing_manager": """
        Marketing Manager responsible for digital marketing, SEO, SEM, content strategy, and social media campaigns.
        Experience with Google Analytics, CRM software (Salesforce, HubSpot), and email marketing tools (Mailchimp).
        Strong communication, market research, brand management, and data-driven decision-making skills.
        B2B and B2C marketing strategies, ROI analysis, and lead generation.
    """,
    "backend_developer": """
        Backend Developer with deep knowledge of Node.js, Python, or Go.
        Experience building RESTful APIs, GraphQL, and microservices architecture.
        Strong database knowledge including PostgreSQL, MongoDB, Redis, and message queues (RabbitMQ, Kafka).
        Focus on scalability, performance tuning, and security best practices.
        Familiarity with serverless architecture and cloud platforms.
    """,
    "full_stack_developer": """
        Full Stack Developer adept at both frontend (React, Vue, HTML/CSS) and backend (Node.js, Flask, Spring).
        Experience with end-to-end web application development and database design.
        Proficient in Git, CI/CD pipelines, Docker, and agile development processes.
        Ability to write clean, maintainable, and testable code across the entire stack.
    """,
    "devops_engineer": """
        DevOps Engineer with expertise in Linux administration, shell scripting, and automation.
        Deep knowledge of CI/CD pipelines (Jenkins, GitLab CI, GitHub Actions) and infrastructure as code (Terraform, Ansible).
        Extensive experience with Docker, Kubernetes, and cloud providers (AWS, Azure, GCP).
        Monitoring and logging systems (Prometheus, Grafana, ELK stack).
    """,
    "cybersecurity_analyst": """
        Cybersecurity Analyst experienced in network security, threat intelligence, and vulnerability assessment.
        Familiarity with penetration testing tools, firewalls, IDS/IPS, and security protocols.
        Knowledge of incident response procedures, SIEM tools, and cryptography.
        Ability to identify security gaps and perform risk management and compliance audits.
    """,
    "machine_learning_engineer": """
        Machine Learning Engineer focused on deploying AI models to production.
        Strong programming in Python and C++, with experience in TensorFlow, PyTorch, and ONNX.
        Expertise in model optimization, MLOps, edge deploying, and GPU programming (CUDA).
        Data pipeline engineering, distributed computing (Spark), and continuous model monitoring.
    """,
    "ui_ux_designer": """
        UI/UX Designer with a strong portfolio showcasing user-centered design and modern web/app aesthetics.
        Proficient in design tools such as Figma, Sketch, Adobe XD, and Illustrator.
        Experience creating wireframes, prototypes, user flows, and conducting user research.
        Understanding of accessibility standards, interaction design, and collaboration with frontend teams.
    """
}

def extract_text_from_pdf(pdf_path):
    """Extract text from a PDF file using PyPDF2."""
    text = ""
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + " "
    except Exception as e:
        print(f"Error extracting PDF: {e}")
    return text.strip()

def preprocess_text(text):
    """Preprocess text by lowercasing, removing special characters, and lemmatizing using Spacy."""
    text = text.lower()
    text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text)
    doc = nlp(text)
    # Lemmatize and remove stop words / punctuation
    tokens = [token.lemma_ for token in doc if not token.is_stop and not token.is_punct and not token.is_space]
    return " ".join(tokens)

def extract_keywords(text):
    """Extract key noun chunks and entities as keywords."""
    doc = nlp(text)
    keywords = set()
    # Extract entities
    for ent in doc.ents:
        if ent.label_ not in ['DATE', 'TIME', 'PERCENT', 'MONEY', 'QUANTITY', 'ORDINAL', 'CARDINAL']:
            keywords.add(ent.text.lower())
    # Extract noun chunks
    for chunk in doc.noun_chunks:
        # Simplify chunk, remove stop words
        cleaned_chunk = " ".join([t.text.lower() for t in chunk if not t.is_stop])
        if cleaned_chunk and len(cleaned_chunk) > 2:
            keywords.add(cleaned_chunk)
            
    # Also add individual alphanumeric tokens longer than 2 chars just in case
    for token in doc:
        if token.is_alpha and not token.is_stop and len(token.text) > 2:
            keywords.add(token.text.lower())
    return keywords

def calculate_ats_score(resume_text, job_role):
    """Calculate the ATS score based on Cosine Similarity and Keyword matching."""
    if job_role not in JOB_DESCRIPTIONS:
        return {"error": "Job role not found"}
        
    jd_raw = JOB_DESCRIPTIONS[job_role]
    
    # Preprocess both
    resume_processed = preprocess_text(resume_text)
    jd_processed = preprocess_text(jd_raw)
    
    if not resume_processed:
         return {"score": 0, "status": "Not Selected", "missing_keywords": ["All"], "keywords_found": []}
         
    # TF-IDF Cosine Similarity
    vectorizer = TfidfVectorizer()
    vectors = vectorizer.fit_transform([jd_processed, resume_processed])
    similarity_matrix = cosine_similarity(vectors)
    cosine_score = similarity_matrix[0][1] * 100
    
    # Keyword Matching
    resume_keywords = extract_keywords(resume_text)
    jd_keywords = extract_keywords(jd_raw)
    
    # Filter jd_keywords to mostly single words and key phrases for better matching
    key_terms = set()
    for kw in jd_keywords:
        for word in kw.split():
            if len(word) > 2:
                key_terms.add(word)
                
    found_keywords = []
    missing_keywords = []
    
    for term in key_terms:
         # simple substring match or token match
         if any(term in r_kw for r_kw in resume_keywords) or term in resume_processed:
             found_keywords.append(term)
         else:
             missing_keywords.append(term)
             
    # Calculate a composite score
    keyword_score = (len(found_keywords) / len(key_terms)) * 100 if len(key_terms) > 0 else 0
    
    # Final Score: 60% Cosine Similarity + 40% Keyword Match
    final_score = (0.6 * cosine_score) + (0.4 * keyword_score)
    final_score = round(final_score, 2)
    
    # Threshold for selection
    threshold = 60.0 # Standard threshold
    status = "Selected" if final_score >= threshold else "Not Selected"
    
    # Limit to top 10 missing to not overwhelm
    missing_keywords = list(set(missing_keywords))[:15]
    found_keywords = list(set(found_keywords))[:15]
    
    return {
        "score": final_score,
        "status": status,
        "missing_keywords": missing_keywords,
        "keywords_found": found_keywords,
        "cosine_similarity": round(cosine_score, 2),
        "keyword_match_percentage": round(keyword_score, 2)
    }

if __name__ == "__main__":
    # Simple test
    test_resume = "I am a solid Python programmer with experience in Flask, Git, and SQL databases. I know data structures and algorithms."
    print("Testing Software Engineer Role:")
    print(calculate_ats_score(test_resume, "software_engineer"))
