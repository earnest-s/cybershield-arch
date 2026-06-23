import json
from typing import List, Dict, Any
from backend.security.security_catalog import SECURITY_CATALOG

def detect_missing_security_components(nodes: List[Dict[str, Any]], edges: List[Dict[str, Any]]) -> List[str]:
    """
    Inspects architecture nodes to determine which security controls are missing.
    """
    required_components = set()
    
    # Rule: Monitoring is always required
    required_components.add("Monitoring")

    has_frontend = False
    has_backend = False
    has_db = False
    has_public_api = False

    # Extract keywords from the architecture definition
    for node in nodes:
        # Convert the node to a lowercase JSON string for permissive matching
        try:
            node_str = json.dumps(node).lower()
        except TypeError:
            node_str = str(node).lower()
            
        # Check UI / frontend
        if any(kw in node_str for kw in ["ui", "frontend", "client"]):
            has_frontend = True
            
        # Check backend / service / api
        if any(kw in node_str for kw in ["backend", "service", "api"]):
            has_backend = True
            
        # Check database
        if any(kw in node_str for kw in ["database", "db", "storage"]):
            has_db = True
            
        # Check public API/backend presence
        if any(kw in node_str for kw in ["api", "backend", "public"]):
            has_public_api = True

    # Rule: If architecture contains UI/frontend and backend/service
    if has_frontend and has_backend:
        required_components.update(["Authentication", "RBAC"])
        
    # Rule: If architecture contains database
    if has_db:
        required_components.update(["Audit Logging", "Encryption Service"])
        
    # Rule: If architecture contains public API/backend
    if has_public_api:
        required_components.update(["API Gateway", "WAF"])

    # Determine which required components are already present in the architecture
    existing_components = set()
    for node in nodes:
        try:
            node_str = json.dumps(node).lower()
        except TypeError:
            node_str = str(node).lower()
            
        for comp_name in required_components:
            if comp_name.lower() in node_str:
                existing_components.add(comp_name)

    missing_components = required_components - existing_components
    return list(missing_components)


def validate_architecture_security(nodes: List[Dict[str, Any]], edges: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Wraps detection and returns structured results categorizing risk levels.
    """
    missing_names = detect_missing_security_components(nodes, edges)
    
    result: Dict[str, List[Dict[str, Any]]] = {
        "missing_components": [],
        "critical": [],
        "high": [],
        "medium": []
    }
    
    for name in missing_names:
        component = SECURITY_CATALOG.get(name)
        if component:
            result["missing_components"].append(component)
            
            # Risk levels are fetched from the updated SECURITY_CATALOG
            risk_level = component.get("risk_level", "medium").lower()
            if risk_level == "critical":
                result["critical"].append(component)
            elif risk_level == "high":
                result["high"].append(component)
            else:
                result["medium"].append(component)
                
    return result
