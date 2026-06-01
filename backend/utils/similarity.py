"""Skill similarity computation using difflib."""

import difflib
from typing import Optional, Dict, Any


def compute_skill_similarity(name1: str, name2: str, desc1: str = "", desc2: str = "") -> float:
    """
    Weighted similarity between two skills.
    - 70% weight on name match
    - 30% weight on description match
    Returns a float between 0.0 and 1.0.
    """
    name_sim = difflib.SequenceMatcher(None, name1.lower().strip(), name2.lower().strip()).ratio()

    if desc1 and desc2:
        desc_sim = difflib.SequenceMatcher(None, desc1.lower().strip(), desc2.lower().strip()).ratio()
    else:
        desc_sim = name_sim  # fallback to name similarity if no descriptions

    return 0.7 * name_sim + 0.3 * desc_sim


def find_best_match(new_name: str, new_desc: str, existing_skills: list, threshold: float = 0.80) -> Optional[Dict[str, Any]]:
    """
    Find the best matching existing skill for a new skill name/description.
    Returns {"skill": existing_skill_dict, "similarity": float} or None.
    """
    best = None
    best_score = 0.0

    for skill in existing_skills:
        score = compute_skill_similarity(new_name, skill["name"], new_desc, skill.get("description", ""))
        if score > best_score:
            best_score = score
            best = skill

    if best and best_score >= threshold:
        return {"skill": best, "similarity": best_score}

    return None
