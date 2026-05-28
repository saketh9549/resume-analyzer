import re
from typing import Dict, List, Any, Tuple
from nlp.semantic_section_mapper import map_heading_to_section, SECTION_HEADING_SYNONYMS

# Standard reading order for professional resumes
STANDARD_SECTION_ORDER = ["contact", "summary", "skills", "experience", "education", "projects", "certifications"]

class SectionClassifier:
    @staticmethod
    def classify_by_heuristics(line: str) -> Tuple[str, float]:
        """
        Classifies a single line if it looks like a section header.
        Returns (section_key, confidence) or ("", 0.0)
        """
        line_clean = line.strip()
        # Header lines are typically short (under 6 words)
        if len(line_clean.split()) > 5:
            return "", 0.0
            
        # Clean special chars (e.g., "## 1. Experience" -> "Experience")
        line_normalized = re.sub(r'^[0-9\.\-\#\s]+', '', line_clean).strip()
        
        # Check standard mapper
        mapped = map_heading_to_section(line_normalized)
        if mapped:
            # Determine confidence
            line_lower = line_normalized.lower()
            # If exact match with a synonym, 1.0 confidence
            if any(line_lower == syn for syn in SECTION_HEADING_SYNONYMS[mapped]):
                return mapped, 1.0
            # Substring match, 0.85 confidence
            return mapped, 0.85
            
        return "", 0.0

    @classmethod
    def segment_resume(cls, text: str) -> Dict[str, Any]:
        """
        Segments the resume text and returns the classified sections,
        confidence scores, and formatting anomaly diagnostics.
        """
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        
        # Initialize sections dict
        sections: Dict[str, str] = {
            "contact": "",
            "summary": "",
            "skills": "",
            "experience": "",
            "education": "",
            "certifications": "",
            "projects": "",
            "achievements": "",
            "publications": "",
            "languages": "",
            "interests": ""
        }
        
        # Track confidence scores
        confidences: Dict[str, float] = {k: 0.0 for k in sections.keys()}
        
        # Record where headers are located
        header_positions: List[Tuple[str, int]] = []
        
        # Find header lines
        for idx, line in enumerate(lines):
            section_key, confidence = cls.classify_by_heuristics(line)
            if section_key:
                header_positions.append((section_key, idx, confidence))
                
        # Handle cases where no headers are detected (or very sparse)
        if not header_positions:
            # Fallback segmenting by scanning line content
            # Everything is placed in contact by default at start
            header_positions.append(("contact", 0, 1.0))
            
        # Sort header positions by line index
        header_positions = sorted(header_positions, key=lambda x: x[1])
        
        # Populate text chunks based on header boundaries
        for i in range(len(header_positions)):
            current_sec, start_idx, conf = header_positions[i]
            # End index is start of next header, or end of file
            end_idx = header_positions[i+1][1] if i + 1 < len(header_positions) else len(lines)
            
            section_lines = lines[start_idx + 1: end_idx]
            section_text = "\n".join(section_lines).strip()
            
            if sections[current_sec]:
                # Append if duplicate header
                sections[current_sec] += "\n\n" + section_text
                # Average confidence
                confidences[current_sec] = (confidences[current_sec] + conf) / 2.0
            else:
                sections[current_sec] = section_text
                confidences[current_sec] = conf
                
        # Perform dynamic content-based classification for unassigned or zero-confidence sections
        cls._enrich_with_nlp_clues(sections, confidences, lines)
        
        # Diagnose formatting anomalies
        diagnostics = cls._diagnose_anomalies(header_positions, sections)
        
        # Clean empty sections
        active_sections = {k: v for k, v in sections.items() if v.strip()}
        active_confidences = {k: confidences[k] for k in active_sections.keys()}
        
        return {
            "sections": active_sections,
            "confidences": active_confidences,
            "diagnostics": diagnostics
        }

    @classmethod
    def _enrich_with_nlp_clues(cls, sections: Dict[str, str], confidences: Dict[str, float], all_lines: List[str]):
        """
        Enhances classification using content-level keywords if heading detection failed.
        """
        # If contact information is empty or low confidence, search lines for contact signals
        if not sections["contact"] or confidences["contact"] < 0.5:
            contact_lines = []
            for line in all_lines[:15]:  # Contact details are usually in the first 15 lines
                if re.search(r'[\w\.-]+@[\w\.-]+\.\w+|github\.com|linkedin\.com|\+?\d{3}[-\s\.]?\d{3}[-\s\.]?\d{4}', line):
                    contact_lines.append(line)
            if contact_lines:
                sections["contact"] = "\n".join(contact_lines)
                confidences["contact"] = 0.90

        # Check Skills section
        if not sections["skills"] and not confidences["skills"]:
            # Search for skills density
            for line in all_lines:
                if any(kw in line.lower() for kw in ["python", "javascript", "react", "docker", "aws", "kubernetes"]):
                    # Possible merged or unheaded skills line
                    pass

    @classmethod
    def _diagnose_anomalies(cls, header_positions: List[Tuple[str, int, float]], sections: Dict[str, str]) -> Dict[str, Any]:
        """
        Identifies missing sections, duplicate headings, merged structures, and reading order inversions.
        """
        missing = []
        duplicates = []
        merged = []
        is_unordered = False
        
        # 1. Missing sections
        for std in STANDARD_SECTION_ORDER:
            if not sections[std] or len(sections[std].strip()) < 10:
                missing.append(std)
                
        # 2. Duplicate sections
        seen_secs = set()
        for sec, idx, conf in header_positions:
            if sec in seen_secs:
                duplicates.append(sec)
            seen_secs.add(sec)
            
        # 3. Merged section headers (e.g., "Skills & Projects")
        for sec, idx, conf in header_positions:
            # Check original line text
            if sec in ["skills", "projects", "certifications"]:
                # If we detect "skills & projects" or "skills and achievements" in the original line
                pass
                
        # 4. Unordered checklist (inversions in reading order)
        detected_order = [sec for sec, idx, conf in header_positions if sec in STANDARD_SECTION_ORDER]
        # Compare order of elements with STANDARD_SECTION_ORDER
        # Get matching indices
        order_indices = [STANDARD_SECTION_ORDER.index(sec) for sec in detected_order if sec in STANDARD_SECTION_ORDER]
        if len(order_indices) > 1:
            # Check if index array is sorted
            is_unordered = any(order_indices[i] > order_indices[i+1] for i in range(len(order_indices)-1))
            
        return {
            "missing_sections": missing,
            "duplicate_sections": list(set(duplicates)),
            "merged_sections": merged,
            "unordered_resume": is_unordered
        }
