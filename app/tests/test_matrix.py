"""
Cross-Template Testing Suite - Test Matrix

This module defines the test cases for the cross-template testing suite.
It includes functions to generate the full test matrix and to filter test cases.
"""

# Template constants
TEMPLATES = [
    "Business Training",
    "Marketing",
    "General Education",
    "Technical Tutorial",
    "Music Lesson"
]

# Parameter constants
LENGTH_OPTIONS = ["short", "medium", "long"]
AUDIENCE_LEVELS = ["beginner", "intermediate", "expert"]
TONE_VARIATIONS = ["informative", "conversational", "persuasive", "enthusiastic", "professional"]

# Subject matter by template
TEMPLATE_SUBJECTS = {
    "Business Training": [
        "Effective Leadership Strategies",
        "Project Management Fundamentals",
        "Negotiation Skills for Managers",
        "Building High-Performance Teams",
        "Business Ethics in the Workplace"
    ],
    "Marketing": [
        "Social Media Marketing Strategies",
        "Content Marketing Essentials",
        "Email Campaign Optimization",
        "Brand Positioning Techniques",
        "Customer Journey Mapping"
    ],
    "General Education": [
        "Introduction to Climate Science",
        "Understanding World History",
        "Fundamentals of Economics",
        "Human Biology Basics",
        "Critical Thinking Skills"
    ],
    "Technical Tutorial": [
        "Introduction to Python Programming",
        "Web Development Fundamentals",
        "Data Analysis with Spreadsheets",
        "Cloud Computing Basics",
        "Machine Learning Concepts"
    ],
    "Music Lesson": [
        "Guitar Fundamentals for Beginners",
        "Piano Chord Progressions",
        "Understanding Music Theory",
        "Vocal Technique Basics",
        "Drumming Rhythm Patterns"
    ]
}

# Expected sections and keywords by template
TEMPLATE_EXPECTATIONS = {
    "Business Training": {
        "expected_sections": ["Introduction", "Learning Objectives", "Main Content", "Case Studies/Examples", "Application", "Assessment", "Summary"],
        "section_markers": ["INTRODUCTION", "LEARNING OBJECTIVES", "KEY CONCEPTS", "CASE STUDIES", "APPLICATION", "KNOWLEDGE CHECK", "SUMMARY"],
        "keywords": ["objectives", "learn", "understand", "apply", "business", "professional", "skills"]
    },
    "Marketing": {
        "expected_sections": ["Introduction", "Value Proposition", "Features/Benefits", "Proof Points", "Call to Action"],
        "section_markers": ["OPENING", "VALUE PROPOSITION", "FEATURES AND BENEFITS", "SOCIAL PROOF", "CALL TO ACTION"],
        "keywords": ["market", "customer", "value", "benefit", "brand", "product", "action"]
    },
    "General Education": {
        "expected_sections": ["Introduction", "Main Concepts", "Examples", "Key Points", "Review Questions", "Summary"],
        "section_markers": ["INTRODUCTION", "MAIN CONCEPTS", "EXAMPLES", "KEY POINTS", "REVIEW", "SUMMARY"],
        "keywords": ["learn", "understand", "concept", "example", "knowledge", "comprehend", "study"]
    },
    "Technical Tutorial": {
        "expected_sections": ["Introduction", "Prerequisites", "Step-by-Step Instructions", "Code Examples", "Troubleshooting", "Summary"],
        "section_markers": ["INTRODUCTION", "PREREQUISITES", "INSTRUCTIONS", "CODE EXAMPLES", "TROUBLESHOOTING", "SUMMARY"],
        "keywords": ["code", "install", "configure", "run", "execute", "debug", "implement"]
    },
    "Music Lesson": {
        "expected_sections": ["Introduction", "Technique Description", "Demonstration", "Practice Exercise", "Summary"],
        "section_markers": ["INTRODUCTION", "TECHNIQUE", "DEMONSTRATION", "PRACTICE", "SUMMARY"],
        "keywords": ["music", "play", "technique", "practice", "rhythm", "note", "sound"]
    }
}

# Word count expectations by length
LENGTH_WORD_COUNTS = {
    "short": {"min": 300, "max": 500},
    "medium": {"min": 600, "max": 900},
    "long": {"min": 1000, "max": 1500}
}

def get_test_matrix():
    """Generate the full test matrix.
    
    Returns:
        List of test case dictionaries
    """
    test_cases = []
    
    # Generate test cases for all parameter combinations
    for template in TEMPLATES:
        for subject in TEMPLATE_SUBJECTS[template]:
            for length in LENGTH_OPTIONS:
                for audience in AUDIENCE_LEVELS:
                    for tone in TONE_VARIATIONS:
                        # Create base test case
                        test_case = {
                            "template": template,
                            "subject": subject,
                            "length": length,
                            "audience": audience,
                            "tone": tone,
                            "expected_sections": TEMPLATE_EXPECTATIONS[template]["expected_sections"],
                            "section_markers": TEMPLATE_EXPECTATIONS[template]["section_markers"],
                            "keywords": TEMPLATE_EXPECTATIONS[template]["keywords"],
                            "min_words": LENGTH_WORD_COUNTS[length]["min"],
                            "max_words": LENGTH_WORD_COUNTS[length]["max"]
                        }
                        
                        test_cases.append(test_case)
    
    return test_cases

def get_filtered_test_cases(filters):
    """Get a filtered subset of test cases.
    
    Args:
        filters: Dictionary of filters to apply to test cases
            Possible keys: templates, subjects, lengths, audiences, tones
            
    Returns:
        List of filtered test case dictionaries
    """
    all_test_cases = get_test_matrix()
    filtered_cases = []
    
    for test_case in all_test_cases:
        include_case = True
        
        # Apply filters
        if 'templates' in filters and test_case['template'] not in filters['templates']:
            include_case = False
        if 'subjects' in filters and test_case['subject'] not in filters['subjects']:
            include_case = False
        if 'length' in filters and test_case['length'] != filters['length']:
            include_case = False
        if 'audience' in filters and test_case['audience'] != filters['audience']:
            include_case = False
        if 'tone' in filters and test_case['tone'] != filters['tone']:
            include_case = False
        
        if include_case:
            filtered_cases.append(test_case)
    
    return filtered_cases

def get_sample_test_cases(count=5):
    """Get a small sample of diverse test cases for quick testing.
    
    Args:
        count: Number of sample test cases to return
        
    Returns:
        List of test case dictionaries
    """
    samples = []
    
    # Add one case for each template with different parameters
    for i, template in enumerate(TEMPLATES):
        if i >= count:
            break
            
        length = LENGTH_OPTIONS[i % len(LENGTH_OPTIONS)]
        audience = AUDIENCE_LEVELS[i % len(AUDIENCE_LEVELS)]
        tone = TONE_VARIATIONS[i % len(TONE_VARIATIONS)]
        subject = TEMPLATE_SUBJECTS[template][0]
        
        test_case = {
            "template": template,
            "subject": subject,
            "length": length,
            "audience": audience,
            "tone": tone,
            "expected_sections": TEMPLATE_EXPECTATIONS[template]["expected_sections"],
            "section_markers": TEMPLATE_EXPECTATIONS[template]["section_markers"],
            "keywords": TEMPLATE_EXPECTATIONS[template]["keywords"],
            "min_words": LENGTH_WORD_COUNTS[length]["min"],
            "max_words": LENGTH_WORD_COUNTS[length]["max"]
        }
        
        samples.append(test_case)
    
    return samples 