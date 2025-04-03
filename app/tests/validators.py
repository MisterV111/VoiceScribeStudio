"""
Cross-Template Testing Suite - Validators

This module provides validation functions for testing script outputs.
"""

import re
import logging
import os
import json

# Configure logging
logger = logging.getLogger("cross_template_testing")

def validate_script(script, test_case):
    """Validate a generated script against test case expectations.
    
    Args:
        script: The generated script text
        test_case: Dictionary containing test parameters and expectations
        
    Returns:
        Dictionary with validation results
    """
    result = {
        'is_valid': True,
        'errors': [],
        'warnings': [],
        'metrics': {},
        'checks': {}
    }
    
    # Run all validation checks
    checks = [
        check_length,
        check_sections,
        check_keywords,
        check_no_template_markers,
        check_audience_appropriate,
        check_tone_consistency
    ]
    
    for check_func in checks:
        check_result = check_func(script, test_case)
        result['checks'][check_func.__name__] = check_result
        
        if not check_result['pass']:
            # Only template markers should cause hard failures
            # All other failures become warnings
            if check_func.__name__ == 'check_no_template_markers':
                result['is_valid'] = False
                result['errors'].append(check_result['message'])
            else:
                result['warnings'].append(check_result['message'])
    
    # Calculate word count
    words = len(script.split())
    result['metrics']['word_count'] = words
    
    return result

def check_length(script, test_case):
    """Check if the script length is within expected range.
    
    Args:
        script: The generated script text
        test_case: Dictionary containing test parameters and expectations
        
    Returns:
        Dictionary with check results
    """
    words = len(script.split())
    min_words = test_case['min_words']
    max_words = test_case['max_words']
    
    result = {
        'pass': min_words <= words <= max_words,
        'message': f"Script length ({words} words) is {'below' if words < min_words else 'above' if words > max_words else 'within'} expected range ({min_words}-{max_words} words)",
        'details': {
            'actual_words': words,
            'min_words': min_words,
            'max_words': max_words
        }
    }
    
    return result

def check_sections(script, test_case):
    """Check if the script contains expected sections.
    
    Args:
        script: The generated script text
        test_case: Dictionary containing test parameters and expectations
        
    Returns:
        Dictionary with check results
    """
    expected_sections = test_case['expected_sections']
    found_sections = []
    missing_sections = []
    
    # For each expected section, look for its presence
    for section in expected_sections:
        # Look for the section using various patterns
        patterns = [
            rf"\b{re.escape(section)}[\s:]",  # Section followed by space or colon
            rf"^{re.escape(section)}[\s:]",   # Section at start of line
            rf"\*\*{re.escape(section)}\*\*"  # Section in bold markdown
        ]
        
        found = False
        for pattern in patterns:
            if re.search(pattern, script, re.IGNORECASE | re.MULTILINE):
                found = True
                break
                
        if found:
            found_sections.append(section)
        else:
            missing_sections.append(section)
    
    # Calculate completeness percentage
    if expected_sections:
        completeness = len(found_sections) / len(expected_sections) * 100
    else:
        completeness = 100
        
    result = {
        'pass': len(missing_sections) == 0,
        'warning': len(missing_sections) > 0 and len(missing_sections) <= len(expected_sections) / 3,  # Warning if missing <= 1/3 of sections
        'message': f"Found {len(found_sections)}/{len(expected_sections)} expected sections ({completeness:.1f}%)" + 
                  (f". Missing: {', '.join(missing_sections)}" if missing_sections else ""),
        'details': {
            'found_sections': found_sections,
            'missing_sections': missing_sections,
            'completeness': completeness
        }
    }
    
    return result

def check_keywords(script, test_case):
    """Check if the script contains expected keywords.
    
    Args:
        script: The generated script text
        test_case: Dictionary containing test parameters and expectations
        
    Returns:
        Dictionary with check results
    """
    expected_keywords = test_case['keywords']
    found_keywords = []
    missing_keywords = []
    
    # Check for each keyword
    for keyword in expected_keywords:
        if re.search(rf"\b{re.escape(keyword)}\w*\b", script, re.IGNORECASE):
            found_keywords.append(keyword)
        else:
            missing_keywords.append(keyword)
    
    # Calculate keyword presence percentage
    if expected_keywords:
        keyword_presence = len(found_keywords) / len(expected_keywords) * 100
    else:
        keyword_presence = 100
        
    # Calculate keyword density
    words = len(script.split())
    keyword_instances = 0
    for keyword in found_keywords:
        keyword_instances += len(re.findall(rf"\b{re.escape(keyword)}\w*\b", script, re.IGNORECASE))
    
    keyword_density = keyword_instances / words * 100 if words > 0 else 0
        
    result = {
        'pass': True,
        'warning': len(found_keywords) < len(expected_keywords),
        'message': f"Found {len(found_keywords)}/{len(expected_keywords)} expected keywords ({keyword_presence:.1f}%)" + 
                  (f". Missing: {', '.join(missing_keywords)}" if missing_keywords else ""),
        'details': {
            'found_keywords': found_keywords,
            'missing_keywords': missing_keywords,
            'keyword_presence': keyword_presence,
            'keyword_density': keyword_density
        }
    }
    
    return result

def check_no_template_markers(script, test_case):
    """Check if the script doesn't contain template markers.
    
    Args:
        script: The generated script text
        test_case: Dictionary containing test parameters and expectations
        
    Returns:
        Dictionary with check results
    """
    section_markers = test_case.get('section_markers', [])
    found_markers = []
    
    # Look for section markers in brackets/braces
    for marker in section_markers:
        patterns = [
            rf"\[{re.escape(marker)}\]",
            rf"\{{.{re.escape(marker)}.\}}",
            rf"<{re.escape(marker)}>"
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, script, re.IGNORECASE)
            if matches:
                found_markers.extend(matches)
    
    # Look for typical markers like [SECTION_NAME]
    additional_patterns = [
        r"\[\s*[A-Z_]+\s*\]",
        r"\{\s*[A-Z_]+\s*\}",
        r"<\s*[A-Z_]+\s*>"
    ]
    
    for pattern in additional_patterns:
        matches = re.findall(pattern, script)
        if matches:
            # Filter out any legitimate markdown or formatting
            filtered_matches = [m for m in matches if not re.match(r"(\[\d+\]|\[[a-z ]+\]|\{\})", m, re.IGNORECASE)]
            found_markers.extend(filtered_matches)
    
    result = {
        'pass': len(found_markers) == 0,
        'message': "No template markers found in script" if len(found_markers) == 0 else f"Found {len(found_markers)} template markers: {', '.join(found_markers[:5])}" + ("..." if len(found_markers) > 5 else ""),
        'details': {
            'found_markers': found_markers
        }
    }
    
    return result

def check_audience_appropriate(script, test_case):
    """Check if the script is appropriate for the target audience.
    
    Args:
        script: The generated script text
        test_case: Dictionary containing test parameters and expectations
        
    Returns:
        Dictionary with check results
    """
    audience = test_case['audience']
    
    # Simple heuristics for audience appropriateness
    checks = {
        'beginner': {
            'simple_language': _check_simple_language(script),
            'explanations': _check_explanations(script),
            'no_jargon': _check_no_advanced_jargon(script)
        },
        'intermediate': {
            'moderate_complexity': _check_moderate_complexity(script),
            'some_details': _check_some_details(script)
        },
        'expert': {
            'advanced_language': _check_advanced_language(script),
            'depth': _check_depth(script),
            'technical': _check_technical_content(script)
        }
    }
    
    # Get the checks for the selected audience
    audience_checks = checks.get(audience, {})
    
    # Calculate percentage of passed checks
    passed = sum(1 for check, result in audience_checks.items() if result['pass'])
    total = len(audience_checks)
    percentage = passed / total * 100 if total > 0 else 0
    
    result = {
        'pass': percentage >= 70,  # Pass if at least 70% of audience checks pass
        'warning': 50 <= percentage < 70,
        'message': f"Script is {percentage:.1f}% appropriate for {audience} audience",
        'details': {
            'audience_checks': audience_checks,
            'audience_appropriateness': percentage
        }
    }
    
    return result

def _check_simple_language(script):
    """Check if the script uses simple language for beginners."""
    # Check average word length
    words = script.split()
    avg_word_length = sum(len(word) for word in words) / len(words) if words else 0
    
    # Check for complex sentence structure
    sentences = re.split(r'[.!?]+', script)
    avg_sentence_length = sum(len(sentence.split()) for sentence in sentences) / len(sentences) if sentences else 0
    
    return {
        'pass': avg_word_length < 5.5 and avg_sentence_length < 20,
        'details': {
            'avg_word_length': avg_word_length,
            'avg_sentence_length': avg_sentence_length
        }
    }

def _check_explanations(script):
    """Check if the script includes explanations for concepts."""
    explanation_patterns = [
        r"means\s",
        r"refers to\s",
        r"is defined as\s",
        r"in other words",
        r"to put it simply",
        r"for example",
        r"such as"
    ]
    
    matches = 0
    for pattern in explanation_patterns:
        matches += len(re.findall(pattern, script, re.IGNORECASE))
    
    return {
        'pass': matches >= 3,
        'details': {
            'explanation_count': matches
        }
    }

def _check_no_advanced_jargon(script):
    """Check if the script avoids advanced jargon."""
    # This is a simplistic check - would need to be customized per domain
    advanced_jargon_patterns = [
        r"\b[a-z]{12,}\b",  # Very long words
        r"\bacronyms?\b",
        r"\btechnical terms?\b"
    ]
    
    matches = 0
    for pattern in advanced_jargon_patterns:
        matches += len(re.findall(pattern, script, re.IGNORECASE))
    
    return {
        'pass': matches <= 2,
        'details': {
            'jargon_count': matches
        }
    }

def _check_moderate_complexity(script):
    """Check if the script has moderate complexity for intermediate audience."""
    words = script.split()
    avg_word_length = sum(len(word) for word in words) / len(words) if words else 0
    
    sentences = re.split(r'[.!?]+', script)
    avg_sentence_length = sum(len(sentence.split()) for sentence in sentences) / len(sentences) if sentences else 0
    
    return {
        'pass': 5 <= avg_word_length <= 7 and 15 <= avg_sentence_length <= 25,
        'details': {
            'avg_word_length': avg_word_length,
            'avg_sentence_length': avg_sentence_length
        }
    }

def _check_some_details(script):
    """Check if the script includes some detailed explanations."""
    detail_patterns = [
        r"specifically",
        r"in particular",
        r"importantly",
        r"details",
        r"aspects"
    ]
    
    matches = 0
    for pattern in detail_patterns:
        matches += len(re.findall(pattern, script, re.IGNORECASE))
    
    return {
        'pass': matches >= 2,
        'details': {
            'detail_indicator_count': matches
        }
    }

def _check_advanced_language(script):
    """Check if the script uses advanced language for experts."""
    words = script.split()
    avg_word_length = sum(len(word) for word in words) / len(words) if words else 0
    
    sentences = re.split(r'[.!?]+', script)
    avg_sentence_length = sum(len(sentence.split()) for sentence in sentences) / len(sentences) if sentences else 0
    
    return {
        'pass': avg_word_length > 6 and avg_sentence_length > 20,
        'details': {
            'avg_word_length': avg_word_length,
            'avg_sentence_length': avg_sentence_length
        }
    }

def _check_depth(script):
    """Check if the script provides in-depth content for experts."""
    depth_patterns = [
        r"advanced",
        r"complex",
        r"sophisticated",
        r"in depth",
        r"detailed analysis"
    ]
    
    matches = 0
    for pattern in depth_patterns:
        matches += len(re.findall(pattern, script, re.IGNORECASE))
    
    return {
        'pass': matches >= 2,
        'details': {
            'depth_indicator_count': matches
        }
    }

def _check_technical_content(script):
    """Check if the script includes technical content for experts."""
    technical_patterns = [
        r"technical",
        r"specialized",
        r"methodology",
        r"algorithm",
        r"procedure"
    ]
    
    matches = 0
    for pattern in technical_patterns:
        matches += len(re.findall(pattern, script, re.IGNORECASE))
    
    return {
        'pass': matches >= 2,
        'details': {
            'technical_indicator_count': matches
        }
    }

def check_tone_consistency(script, test_case):
    """Check if the script maintains the requested tone.
    
    Args:
        script: The generated script text
        test_case: Dictionary containing test parameters and expectations
        
    Returns:
        Dictionary with check results
    """
    tone = test_case['tone']
    
    # Define tone indicators for each tone
    tone_indicators = {
        'informative': [
            r"fact",
            r"study",
            r"research",
            r"according to",
            r"evidence",
            r"shows that",
            r"demonstrates"
        ],
        'conversational': [
            r"you'll",
            r"let's",
            r"we'll",
            r"you know",
            r"actually",
            r"basically",
            r"right\?"
        ],
        'persuasive': [
            r"should",
            r"must",
            r"need to",
            r"important",
            r"significant",
            r"benefit",
            r"advantage"
        ],
        'enthusiastic': [
            r"amazing",
            r"exciting",
            r"fantastic",
            r"wonderful",
            r"great",
            r"incredible",
            r"!"
        ],
        'professional': [
            r"effectively",
            r"efficiently",
            r"properly",
            r"appropriate",
            r"objective",
            r"standard",
            r"protocol"
        ]
    }
    
    # Get indicators for requested tone
    requested_indicators = tone_indicators.get(tone, [])
    
    # Check for indicators of the requested tone
    requested_matches = 0
    for pattern in requested_indicators:
        requested_matches += len(re.findall(pattern, script, re.IGNORECASE))
    
    # Check for indicators of other tones
    other_tones_matches = {}
    for other_tone, patterns in tone_indicators.items():
        if other_tone != tone:
            matches = 0
            for pattern in patterns:
                matches += len(re.findall(pattern, script, re.IGNORECASE))
            other_tones_matches[other_tone] = matches
    
    # Calculate tone consistency percentage
    total_matches = requested_matches + sum(other_tones_matches.values())
    consistency = requested_matches / total_matches * 100 if total_matches > 0 else 0
    
    result = {
        'pass': consistency >= 60,  # Pass if at least 60% of tone indicators match requested tone
        'warning': 40 <= consistency < 60,
        'message': f"Script maintains {consistency:.1f}% consistency with '{tone}' tone",
        'details': {
            'requested_tone': tone,
            'requested_tone_matches': requested_matches,
            'other_tones_matches': other_tones_matches,
            'tone_consistency': consistency
        }
    }
    
    return result

def format_validation_results(validation):
    """Format validation results as markdown for better readability."""
    if not validation:
        return "No validation results available."
    
    md_lines = []
    
    # Overall status with icon
    success = validation.get('is_valid', False)
    status_icon = "✅" if success else "❌"
    md_lines.append(f"## Overall Result: {status_icon} {'PASSED' if success else 'FAILED'}")
    md_lines.append("")
    
    # Word count
    word_count = validation.get('metrics', {}).get('word_count', 0)
    md_lines.append(f"**Word Count:** {word_count}")
    md_lines.append("")
    
    # Add errors section
    errors = validation.get('errors', [])
    if errors:
        md_lines.append(f"### ❌ Errors ({len(errors)})")
        for i, error in enumerate(errors, 1):
            md_lines.append(f"{i}. {error}")
        md_lines.append("")
    
    # Add warnings section  
    warnings = validation.get('warnings', [])
    if warnings:
        md_lines.append(f"### ⚠️ Warnings ({len(warnings)})")
        for i, warning in enumerate(warnings, 1):
            md_lines.append(f"{i}. {warning}")
        md_lines.append("")
    
    # Add check results
    checks = validation.get('checks', {})
    if checks:
        md_lines.append("### Validation Checks")
        
        for check_name, check_result in checks.items():
            # Format the check name
            readable_name = check_name.replace('check_', '').replace('_', ' ').title()
            
            # Add pass/fail icon
            check_icon = "✅" if check_result.get('pass', False) else "❌"
            
            # Add the check description
            check_desc = check_result.get('message', readable_name)
            md_lines.append(f"- {check_icon} **{readable_name}**: {check_desc}")
        
        md_lines.append("")
    
    return "\n".join(md_lines)

def update_test_details(test_id, run_id):
    if not test_id or not run_id:
        return [None, "", "", None]
    
    # Extract the clean run ID from the dropdown label if needed
    clean_run_id = run_id.split(' - ')[0] if ' - ' in run_id else run_id
    
    # Get test details
    file_path = os.path.join(TEST_RESULTS_DIR, clean_run_id, f"{test_id}.json")
    if not os.path.exists(file_path):
        return [None, "", "", None]
    
    with open(file_path, 'r') as f:
        details = json.load(f)
    
    # Extract relevant information
    config = details.get('test_case', {})
    script = details.get('generated_script', '')
    validation = details.get('validation', {})
    
    # Format validation results for better readability
    validation_md = format_validation_results(validation)
    
    return [config, script, validation_md, validation] 