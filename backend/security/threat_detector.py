from typing import List, Dict, Any, Set
from backend.security.security_catalog import SECURITY_CATALOG
from backend.security.security_validator import validate_architecture_security
from backend.security.security_report import generate_security_report
from backend.security.security_analyzer import analyze_architecture_security

THREAT_KNOWLEDGE_BASE: Dict[str, Dict[str, str]] = {
    "Unauthorized Access": {"name": "Unauthorized Access", "severity": "CRITICAL", "description": "Attackers can access systems or data without proper identity verification."},
    "Privilege Escalation": {"name": "Privilege Escalation", "severity": "HIGH", "description": "Users or attackers can gain higher access rights than they are supposed to have."},
    "Credential Stuffing": {"name": "Credential Stuffing", "severity": "HIGH", "description": "Automated injection of breached username/password pairs."},
    "SQL Injection": {"name": "SQL Injection", "severity": "CRITICAL", "description": "Attackers can execute malicious SQL statements that control a web application's database server."},
    "Data Leakage": {"name": "Data Leakage", "severity": "CRITICAL", "description": "Sensitive data is exposed in transit or at rest."},
    "Data Tampering": {"name": "Data Tampering", "severity": "HIGH", "description": "Data is maliciously modified."},
    "DDoS": {"name": "DDoS", "severity": "HIGH", "description": "Distributed Denial of Service attacking service availability."},
    "Session Hijacking": {"name": "Session Hijacking", "severity": "HIGH", "description": "Attackers take over an active user session."},
    "Insider Threat": {"name": "Insider Threat", "severity": "MEDIUM", "description": "Malicious or negligent actions by internal users."},
    "Log Evasion": {"name": "Log Evasion", "severity": "MEDIUM", "description": "Attackers can perform actions without generating audit trails."},
    "Lateral Movement": {"name": "Lateral Movement", "severity": "HIGH", "description": "Attackers move through the network searching for key assets."}
}

THREAT_MAPPING: Dict[str, List[str]] = {
    "Authentication": ["Unauthorized Access", "Credential Stuffing"],
    "RBAC": ["Privilege Escalation", "Insider Threat"],
    "WAF": ["SQL Injection", "DDoS"],
    "Audit Logging": ["Log Evasion"],
    "Encryption Service": ["Data Leakage", "Data Tampering"],
    "Monitoring": ["Lateral Movement"],
    "API Gateway": ["DDoS", "Session Hijacking"],
    "MFA": ["Credential Stuffing", "Unauthorized Access"],
    "SIEM": ["Lateral Movement"]
}

CONTROL_TO_NODE_TYPES: Dict[str, List[str]] = {
    "WAF": ["api", "gateway", "service"],
    "API Gateway": ["api", "gateway", "service"],
    "Authentication": ["frontend", "ui", "client", "api", "service"],
    "MFA": ["frontend", "ui", "client", "api", "service"],
    "RBAC": ["api", "service", "admin"],
    "Encryption Service": ["database", "db", "storage", "postgres", "mysql", "mongo"],
    "Audit Logging": ["api", "service", "database", "db"],
    "Secrets Manager": ["api", "service", "backend"],
    "Monitoring": ["api", "service", "database", "db", "frontend", "ui"],
    "IDS": ["api", "service", "gateway"],
    "IPS": ["api", "service", "gateway"],
    "SIEM": ["api", "service", "database", "db"],
}

THREAT_SEVERITY_COLORS: Dict[str, str] = {
    "CRITICAL": "danger",
    "HIGH": "warning",
    "MEDIUM": "info",
    "LOW": "success"
}

def get_affected_node_ids(nodes: List[Dict[str, Any]], missing_control: str) -> List[str]:
    """Get node IDs affected by a specific missing security control."""
    affected: List[str] = []
    target_keywords = CONTROL_TO_NODE_TYPES.get(missing_control, [])
    
    if not target_keywords:
        return affected
    
    for node in nodes:
        node_id = node.get("id", "")
        node_type = node.get("type", "")
        try:
            node_str = (node_id + " " + node_type).lower()
        except:
            node_str = str(node).lower()
        
        if any(kw in node_str for kw in target_keywords):
            affected.append(node_id)
    
    return affected

def get_affected_edge_ids(edges: List[Dict[str, Any]], missing_control: str, nodes: List[Dict[str, Any]]) -> List[str]:
    """Get edge IDs affected by a specific missing security control."""
    affected: List[str] = []
    target_keywords = CONTROL_TO_NODE_TYPES.get(missing_control, [])
    
    if not target_keywords:
        return affected
    
    node_types: Dict[str, str] = {}
    for node in nodes:
        node_id = node.get("id", "")
        node_type = node.get("type", "")
        node_types[node_id] = (node_id + " " + node_type).lower()
    
    for edge in edges:
        source_id = edge.get("source", "")
        target_id = edge.get("target", "")
        
        source_type = node_types.get(source_id, "")
        target_type = node_types.get(target_id, "")
        
        if any(kw in source_type for kw in target_keywords) or any(kw in target_type for kw in target_keywords):
            edge_id = edge.get("id", f"{source_id}->{target_id}")
            affected.append(edge_id)
    
    return affected

def build_threat_node_mapping(nodes: List[Dict[str, Any]], edges: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Build a mapping of threats to affected node/edge IDs for visualization.
    Returns a dict with threats, node_threats, and edge_threats.
    """
    analysis = analyze_architecture_security(nodes, edges)
    missing_controls = [comp.get("name") for comp in analysis.get("missing_components", [])]
    
    detected_threats: Dict[str, Dict[str, Any]] = {}
    node_threats: Dict[str, List[Dict[str, Any]]] = {}
    edge_threats: Dict[str, List[Dict[str, Any]]] = {}
    
    for comp in missing_controls:
        threat_names = THREAT_MAPPING.get(comp, [])
        affected_nodes = get_affected_node_ids(nodes, comp)
        affected_edges = get_affected_edge_ids(edges, comp, nodes)
        
        for t_name in threat_names:
            if t_name not in detected_threats and t_name in THREAT_KNOWLEDGE_BASE:
                threat_info = THREAT_KNOWLEDGE_BASE[t_name].copy()
                threat_info["missing_control"] = comp
                threat_info["severity"] = THREAT_KNOWLEDGE_BASE[t_name]["severity"]
                threat_info["severity_level"] = THREAT_SEVERITY_COLORS.get(threat_info["severity"], "")
                detected_threats[t_name] = threat_info
                
                for node_id in affected_nodes:
                    if node_id not in node_threats:
                        node_threats[node_id] = []
                    node_threats[node_id].append({
                        "threat": t_name,
                        "severity": threat_info["severity"],
                        "missing_control": comp,
                        "severity_level": threat_info["severity_level"]
                    })
                
                for edge_id in affected_edges:
                    if edge_id not in edge_threats:
                        edge_threats[edge_id] = []
                    edge_threats[edge_id].append({
                        "threat": t_name,
                        "severity": threat_info["severity"],
                        "missing_control": comp,
                        "severity_level": threat_info["severity_level"]
                    })
    
    return {
        "threats": list(detected_threats.values()),
        "node_threats": node_threats,
        "edge_threats": edge_threats
    }

def calculate_attack_surface(nodes: List[Dict[str, Any]], edges: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calculate the attack surface metrics.
    """
    public_endpoints = 0
    databases = 0
    services = 0
    
    for node in nodes:
        try:
            node_str = str(node).lower()
        except:
            continue
            
        if any(kw in node_str for kw in ["frontend", "ui", "public", "api"]):
            public_endpoints += 1
        if any(kw in node_str for kw in ["db", "database", "postgres", "storage", "redis"]):
            databases += 1
        if any(kw in node_str for kw in ["service", "backend", "api"]):
            services += 1
            
    # Simple scoring logic: more exposed elements means higher surface score
    score = (public_endpoints * 10) + (services * 5) + (databases * 10)
    
    return {
        "attack_surface_score": min(100, score),
        "public_endpoints": public_endpoints,
        "databases": databases,
        "services": services
    }

def detect_threats(nodes: List[Dict[str, Any]], edges: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Infers threats from the missing security controls identified by architecture analysis.
    Returns threats with node/edge mappings for visualization.
    """
    return build_threat_node_mapping(nodes, edges)

def generate_threat_summary(threats: List[Dict[str, str]]) -> str:
    """
    Generates a readable summary of detected threats.
    """
    if not threats:
        return "The architecture is well-protected against common threats."
        
    names = [t.get("name") for t in threats]
    
    if len(names) == 1:
        names_str = names[0]
    else:
        names_str = ", ".join(names[:-1]) + f" and {names[-1]}"
        
    return f"The architecture is vulnerable to {names_str} because critical security controls are missing."
