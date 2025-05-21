"""
Skill Matcher Module (Simplified Version)
Uses basic NLP techniques to extract skills from resumes and job descriptions
and compare them using text similarity
"""
import re
import logging
from collections import Counter
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SkillMatcher:
    def __init__(self):
        """
        Initialize the SkillMatcher with skill detection capabilities
        """
        # Common technical skills to detect
        self.common_tech_skills = {
            "python", "java", "javascript", "typescript", "c++", "c#", "ruby", "php", "swift",
            "kotlin", "Golang", "Go", "rust", "html", "css", "react", "angular", "vue", "node.js", "express",
            "django", "flask", "spring", "hibernate", "docker", "kubernetes", "aws", "azure", 
            "gcp", "terraform", "jenkins", "github actions", "circleci", "travis", "git", "svn",
            "sql", "mysql", "postgresql", "mongodb", "redis", "elasticsearch", "kafka", "rabbitmq",
            "tensorflow", "pytorch", "scikit-learn", "pandas", "numpy", "matplotlib", "tableau",
            "power bi", "excel", "jira", "confluence", "agile", "scrum", "kanban", "rest api",
            "graphql", "oauth", "jwt", "microservices", "devops", "ci/cd", "machine learning",
            "deep learning", "nlp", "data analysis", "data science", "big data", "hadoop", "spark"
        }
        
        # Additional skill categories and terms
        self.skill_categories = {
            "programming_languages": {
                "python", "java", "c++", "c#", "javascript", "typescript", "ruby", "go", "rust", 
                "php", "scala", "kotlin", "swift", "r", "perl", "bash", "powershell", "sql"
            },
            "frontend": {
                "html", "css", "javascript", "react", "angular", "vue", "redux", "bootstrap", 
                "tailwind", "jquery", "webpack", "sass", "less", "typescript", "next.js", "gatsby"
            },
            "backend": {
                "node.js", "express", "django", "flask", "spring", "laravel", "ruby on rails", 
                "asp.net", "fastapi", "graphql", "rest api", "websockets", "microservices"
            },
            "databases": {
                "sql", "mysql", "postgresql", "mongodb", "sqlite", "oracle", "dynamodb", "redis", 
                "cassandra", "elasticsearch", "firebase", "mariadb", "neo4j", "couchbase"
            },
            "devops": {
                "docker", "kubernetes", "jenkins", "gitlab ci", "github actions", "terraform", 
                "ansible", "puppet", "chef", "aws", "azure", "gcp", "ci/cd", "prometheus", "grafana"
            },
            "data_science": {
                "python", "r", "pandas", "numpy", "matplotlib", "scikit-learn", "tensorflow", 
                "pytorch", "keras", "jupyter", "tableau", "power bi", "machine learning", 
                "deep learning", "statistics", "data visualization", "big data", "data mining"
            },
            "soft_skills": {
                "leadership", "communication", "teamwork", "problem solving", "critical thinking", 
                "time management", "project management", "creativity", "adaptability", "collaboration"
            }
        }
        
        # Create a flattened set of all skills
        self.all_skills = set()
        for category in self.skill_categories.values():
            self.all_skills.update(category)
        self.all_skills.update(self.common_tech_skills)
        
        # Initialize vectorizer for text similarity
        self.vectorizer = CountVectorizer()
        
    def extract_skills(self, text):
        """
        Extract skills from text using pattern matching
        
        Args:
            text (str): The text to extract skills from
            
        Returns:
            set: A set of skills extracted from the text
        """
        if not text:
            return set()
        
        text_lower = text.lower()
        skills = set()
        
        # Extract skills using pattern matching for known skills
        for skill in self.all_skills:
            # Use regex to find whole word matches
            pattern = r'\b' + re.escape(skill) + r'\b'
            if re.search(pattern, text_lower):
                skills.add(skill)
        
        # Look for capitalized abbreviations that might be technologies or languages
        abbrev_pattern = r'\b[A-Z][A-Z]+\b'
        for match in re.finditer(abbrev_pattern, text):
            skill_abbr = match.group().lower()
            if len(skill_abbr) >= 2:  # Only consider abbreviations with 2+ letters
                skills.add(skill_abbr)
        
        # Look for phrases that might be skills (simple noun phrases)
        # This is a simplified approach that doesn't need spaCy
        words = re.findall(r'\b[a-zA-Z][a-zA-Z\-\.]+\b', text_lower)
        bigrams = [' '.join(words[i:i+2]) for i in range(len(words)-1)]
        trigrams = [' '.join(words[i:i+3]) for i in range(len(words)-2)]
        
        # Check if any of these n-grams are known skills
        for phrase in bigrams + trigrams:
            if phrase in self.all_skills:
                skills.add(phrase)
        
        return skills

    def calculate_similarity(self, resume_text, job_text):
        """
        Calculate the similarity between resume text and job description text
        
        Args:
            resume_text (str): Text from the resume
            job_text (str): Text from the job description
            
        Returns:
            float: Similarity score between 0 and 1
        """
        if not resume_text or not job_text:
            return 0.0
        
        # Create a document-term matrix
        documents = [resume_text.lower(), job_text.lower()]
        try:
            X = self.vectorizer.fit_transform(documents)
            # Calculate cosine similarity
            similarity = cosine_similarity(X)[0, 1]
            return similarity
        except Exception as e:
            logger.error(f"Error calculating similarity: {str(e)}")
            return 0.0
            
    def find_matching_skills(self, resume_skills, job_skills):
        """
        Find the skills that match between resume and job description
        
        Args:
            resume_skills (set): Skills extracted from the resume
            job_skills (set): Skills required in the job description
            
        Returns:
            set: Matching skills
        """
        # Direct intersection of skills
        return resume_skills.intersection(job_skills)

    def find_missing_skills(self, resume_skills, job_skills, matching_skills):
        """
        Find the skills mentioned in the job description but missing from the resume
        
        Args:
            resume_skills (set): Skills extracted from the resume
            job_skills (set): Skills required in the job description
            matching_skills (set): Skills that match between resume and job
            
        Returns:
            set: Missing skills
        """
        return job_skills - matching_skills

    def analyze(self, resume_text, job_desc_text):
        """
        Analyze a resume against a job description
        
        Args:
            resume_text (str): Text extracted from the resume
            job_desc_text (str): Text extracted from the job description
            
        Returns:
            dict: Analysis results including match percentage and skills
        """
        # Extract skills from both documents
        resume_skills = self.extract_skills(resume_text)
        job_skills = self.extract_skills(job_desc_text)
        
        # Find matching and missing skills
        matching_skills = self.find_matching_skills(resume_skills, job_skills)
        missing_skills = self.find_missing_skills(resume_skills, job_skills, matching_skills)
        
        # Calculate text similarity
        text_similarity = self.calculate_similarity(resume_text, job_desc_text)
        
        # Calculate match percentage
        # We use a weighted approach: 50% based on similarity, 50% based on coverage
        if job_skills:
            coverage = len(matching_skills) / len(job_skills)
        else:
            coverage = 0
            
        match_percentage = (text_similarity * 0.5 + coverage * 0.5) * 100
        
        # Format results
        results = {
            "match_percentage": round(match_percentage, 2),
            "resume_skills": sorted(list(resume_skills)),
            "job_required_skills": sorted(list(job_skills)),
            "matching_skills": sorted(list(matching_skills)),
            "missing_skills": sorted(list(missing_skills)),
            "skill_count": {
                "resume": len(resume_skills),
                "job_description": len(job_skills),
                "matching": len(matching_skills),
                "missing": len(missing_skills)
            }
        }
        
        return results