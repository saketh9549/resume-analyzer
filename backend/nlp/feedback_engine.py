from typing import Dict, List, Any
from nlp.action_verb_analyzer import analyze_experience_verbs
from nlp.rewrite_recommendations import find_rewrite_suggestions

class FeedbackEngine:
    @classmethod
    def generate_feedback(cls, parsed_data: Dict[str, Any], raw_text: str) -> Dict[str, Any]:
        """
        Synthesizes raw resume content and parsing structures into 7 categories of feedback.
        """
        skills = parsed_data.get("skills", [])
        experience = parsed_data.get("experience", [])
        projects = parsed_data.get("projects", [])
        education = parsed_data.get("education", [])
        contact = parsed_data.get("contact", {})
        
        # 1. Action Verb Analysis
        responsibilities = []
        for exp in experience:
            responsibilities.extend(exp.get("responsibilities", []))
        verb_res = analyze_experience_verbs(responsibilities)
        
        # 2. Rewrite suggestions search
        text_lower = raw_text.lower()
        rewrite_pairs = find_rewrite_suggestions(raw_text)
        rewrite_suggs = [p["recommended"] for p in rewrite_pairs]
        if not rewrite_suggs:
            # default suggestions
            rewrite_suggs = [
                "Rephrased 'helped developer' -> 'Partnered with senior engineers to build scalable react applications.'",
                "Rephrased 'worked on db' -> 'Optimized complex SQL query paths, slashing backend lookup latency by 35%.'"
            ]
            
        # 3. Missing skills (Skill Gaps)
        from services.scoring_engine import CORE_RECOMMENDED_SKILLS
        skill_gaps = [s for s in CORE_RECOMMENDED_SKILLS if s not in skills]
        
        # 4. Resume completeness metrics
        completeness_tips = []
        if not contact.get("github"):
            completeness_tips.append("Add a GitHub profile link to showcase open-source repositories.")
        if not contact.get("linkedin"):
            completeness_tips.append("Add your LinkedIn profile link to help recruiters find you online.")
        if not education:
            completeness_tips.append("Ensure your Education history is populated with degree titles and years.")
        if not projects:
            completeness_tips.append("List at least 1-2 major technical projects to demonstrate hands-on practice.")
            
        # 5. Experience enhancement tips
        exp_tips = []
        if len(experience) < 2:
            exp_tips.append("Include details of prior internships, freelance roles, or co-ops to establish career depth.")
        for exp in experience:
            if len(exp.get("responsibilities", [])) < 3:
                exp_tips.append(f"Add more description bullets for your role at {exp.get('company', 'Employer')} (aim for 3-5 bullets).")
                
        # 6. Quantification suggestions
        quant_tips = []
        number_count = len(re.findall(r'\b\d+%\b|\$\d+|\b\d+\+\b', raw_text))
        if number_count < 3:
            quant_tips.append("Add numeric metrics to describe results (e.g. 'reduced latency by 40%', 'managed team of 5').")
            quant_tips.append("Highlight quantitative outcomes in your latest job role's bullet points.")
        else:
            quant_tips.append("Maintain the excellent habit of quantifying project achievements with numbers.")
            
        # 7. Semantic optimization tips
        semantic_tips = [
            "Tailor experience statement wording to align with the core vocabulary of targeted job postings.",
            "Use clear, readable sans-serif fonts to ensure ATS parser engines read your sentences without parsing errors."
        ]
        
        # Compile into 7 distinct categories
        return {
            "skill_gaps": skill_gaps if skill_gaps else ["No critical skill gaps found for core roles."],
            "rewrite_suggestions": rewrite_suggs[:3],
            "completeness_feedback": completeness_tips if completeness_tips else ["Resume completeness is 100%."],
            "experience_enhancement": exp_tips if exp_tips else ["Your professional experience section is robust."],
            "action_verb_upgrades": verb_res["suggestions"] if verb_res["suggestions"] else ["Good variety of strong action verbs detected."],
            "quantification_suggestions": quant_tips,
            "semantic_optimization": semantic_tips,
            "verb_score": verb_res["verb_score"]
        }
import re
