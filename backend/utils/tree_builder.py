"""Build a nested skill tree from a flat list of skills."""

from typing import Dict, List


def build_skill_tree(skills: list) -> list:
    """
    Convert a flat list of skill dicts into a nested tree structure.
    Tree levels: l1 (大类) -> l2 (中类) -> l3 (小类) -> skill

    Each node: {key, title, type, children: [], skill?: {...}}
    """
    tree = []

    # Group by category_l1
    l1_groups: Dict[str, list] = {}
    for skill in skills:
        l1 = skill.get("category_l1", "其他")
        if l1 not in l1_groups:
            l1_groups[l1] = []
        l1_groups[l1].append(skill)

    for l1_name, l1_skills in sorted(l1_groups.items()):
        l1_node = {
            "key": f"l1:{l1_name}",
            "title": l1_name,
            "type": "l1",
            "children": [],
        }

        # Group by category_l2 within this l1
        l2_groups: Dict[str, list] = {}
        for skill in l1_skills:
            l2 = skill.get("category_l2", "其他")
            if l2 not in l2_groups:
                l2_groups[l2] = []
            l2_groups[l2].append(skill)

        for l2_name, l2_skills in sorted(l2_groups.items()):
            l2_node = {
                "key": f"l2:{l1_name}/{l2_name}",
                "title": l2_name,
                "type": "l2",
                "children": [],
            }

            # Group by category_l3 within this l2
            l3_groups: Dict[str, list] = {}
            for skill in l2_skills:
                l3 = skill.get("category_l3", "") or "其他"
                if l3 not in l3_groups:
                    l3_groups[l3] = []
                l3_groups[l3].append(skill)

            for l3_name, l3_skills in sorted(l3_groups.items()):
                if l3_name == "其他" and len(l3_skills) <= 1:
                    # Skip "其他" l3 if only one skill — put skill directly under l2
                    for skill in l3_skills:
                        l2_node["children"].append({
                            "key": f"skill:{skill['id']}",
                            "title": skill["name"],
                            "type": "skill",
                            "skill": skill,
                            "children": [],
                        })
                else:
                    l3_node = {
                        "key": f"l3:{l1_name}/{l2_name}/{l3_name}",
                        "title": l3_name,
                        "type": "l3",
                        "children": [],
                    }
                    for skill in l3_skills:
                        l3_node["children"].append({
                            "key": f"skill:{skill['id']}",
                            "title": skill["name"],
                            "type": "skill",
                            "skill": skill,
                            "children": [],
                        })
                    l2_node["children"].append(l3_node)

            l1_node["children"].append(l2_node)

        tree.append(l1_node)

    return tree
