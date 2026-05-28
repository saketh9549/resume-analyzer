from typing import Dict, Any, List

class SemanticResumeGraph:
    @staticmethod
    def build_graph(resume_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Builds a co-occurrence graph representing the relationships 
        between skills, projects, and roles from the candidate's resume.
        """
        nodes = []
        edges = []
        node_ids = set()
        
        # Add a root node for the resume
        filename = resume_data.get("filename", "Resume")
        nodes.append({"id": "root", "label": filename, "type": "resume", "val": 20})
        
        # Extract skills
        skills = resume_data.get("skills", [])
        for skill in skills:
            skill_id = f"skill:{skill.lower()}"
            if skill_id not in node_ids:
                nodes.append({"id": skill_id, "label": skill, "type": "skill", "val": 10})
                node_ids.add(skill_id)
                # Link skill to root
                edges.append({"source": "root", "target": skill_id, "type": "has_skill", "weight": 1.0})
                
        # Extract experience roles
        experience = resume_data.get("experience", [])
        for idx, exp in enumerate(experience):
            role = exp.get("job_title", "")
            company = exp.get("company", "")
            if role:
                role_id = f"role:{role.lower()}_{idx}"
                nodes.append({"id": role_id, "label": f"{role} at {company}" if company else role, "type": "role", "val": 15})
                edges.append({"source": "root", "target": role_id, "type": "worked_as", "weight": 1.5})
                
                # Try linking skills in experience text to this role
                exp_desc = " ".join(exp.get("responsibilities", []))
                for skill in skills:
                    if skill.lower() in exp_desc.lower() or skill.lower() in role.lower():
                        skill_id = f"skill:{skill.lower()}"
                        edges.append({"source": role_id, "target": skill_id, "type": "used_skill", "weight": 1.2})
                        
        # Extract projects
        projects = resume_data.get("projects", [])
        for idx, proj in enumerate(projects):
            name = proj.get("name", "")
            desc = proj.get("description", "")
            tech = proj.get("technologies", [])
            
            if name:
                proj_id = f"project:{name.lower()}_{idx}"
                nodes.append({"id": proj_id, "label": name, "type": "project", "val": 12})
                edges.append({"source": "root", "target": proj_id, "type": "completed_project", "weight": 1.3})
                
                # Link explicitly declared tech
                for t in tech:
                    t_id = f"skill:{t.lower()}"
                    if t_id in node_ids:
                        edges.append({"source": proj_id, "target": t_id, "type": "built_with", "weight": 1.5})
                    else:
                        nodes.append({"id": t_id, "label": t, "type": "skill", "val": 10})
                        node_ids.add(t_id)
                        edges.append({"source": proj_id, "target": t_id, "type": "built_with", "weight": 1.5})
                        
                # Link skills based on text co-occurrence
                for skill in skills:
                    if skill.lower() in desc.lower():
                        skill_id = f"skill:{skill.lower()}"
                        edges.append({"source": proj_id, "target": skill_id, "type": "uses_skill", "weight": 1.2})
                        
        return {
            "nodes": nodes,
            "edges": edges
        }
