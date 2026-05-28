from typing import Dict, Any
from database.mongodb import users_collection, resumes_collection
from bson import ObjectId

class CareerPreferenceEngine:
    @staticmethod
    def get_preferences(user_email: str) -> Dict[str, Any]:
        if users_collection is None:
            return {}
        user = users_collection.find_one({"email": user_email})
        if not user:
            return {}
        return user.get("career_preferences", {})

    @staticmethod
    def update_preferences(user_email: str, preferences: Dict[str, Any]) -> bool:
        if users_collection is None:
            return False
            
        # Update user profile
        users_collection.update_one(
            {"email": user_email},
            {
                "$set": {
                    "career_preferences": preferences,
                    "preferred_roles": preferences.get("preferred_roles", [])
                }
            }
        )
        
        # Dynamic Trigger: Re-run context engine for user's resumes to recalculate recruiter scores
        if resumes_collection is not None:
            try:
                cursor = resumes_collection.find({"user_email": user_email})
                from nlp.resume_context_engine import ResumeContextEngine
                for doc in cursor:
                    ResumeContextEngine.get_unified_context(str(doc["_id"]), user_email)
            except Exception:
                pass  # avoid breaking the preference save if resume updates fail
                
        return True
