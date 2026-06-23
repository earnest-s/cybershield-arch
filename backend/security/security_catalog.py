from typing import Dict, List, Any, Optional

SECURITY_CATALOG: Dict[str, Dict[str, Any]] = {
    "Authentication": {
        "name": "Authentication",
        "category": "Identity and Access Management",
        "risk_if_missing": "Unauthorized access to applications and sensitive data.",
        "required_for": ["web_app", "api", "mobile_app", "admin_panel"],
        "description": "Verifies the identity of users and services attempting to access systems."
    },
    "RBAC": {
        "name": "RBAC",
        "category": "Identity and Access Management",
        "risk_if_missing": "Privilege escalation and unauthorized data modification.",
        "required_for": ["web_app", "api", "admin_panel"],
        "description": "Role-Based Access Control to enforce authorization policies strictly by roles."
    },
    "API Gateway": {
        "name": "API Gateway",
        "category": "Network Security",
        "risk_if_missing": "Direct exposure of backend services, lack of throttling, and DoS attacks.",
        "required_for": ["microservices", "api", "serverless"],
        "description": "Acts as a single entry point for APIs, providing routing, rate limiting, and unified security."
    },
    "Audit Logging": {
        "name": "Audit Logging",
        "category": "Observability and Compliance",
        "risk_if_missing": "Inability to investigate security incidents and failure to meet compliance standards.",
        "required_for": ["core", "financial", "healthcare", "admin_panel"],
        "description": "Records continuous security-relevant events, operations, and access logs."
    },
    "Monitoring": {
        "name": "Monitoring",
        "category": "Observability and Compliance",
        "risk_if_missing": "Delayed detection of service degradation, system outages, or ongoing attacks.",
        "required_for": ["infrastructure", "microservices", "web_app"],
        "description": "Continuous monitoring of system health, real-time metrics, and security anomalies."
    },
    "Secrets Manager": {
        "name": "Secrets Manager",
        "category": "Data Security",
        "risk_if_missing": "Hardcoded credentials in code leading to complete application compromise.",
        "required_for": ["backend", "microservices", "cicd_pipeline"],
        "description": "Secure storage and dynamic access for API keys, passwords, and digital certificates."
    },
    "SIEM": {
        "name": "SIEM",
        "category": "Security Operations",
        "risk_if_missing": "Failure to correlate cross-system security events and detect complex breaches.",
        "required_for": ["enterprise", "infrastructure"],
        "description": "Security Information and Event Management system for log aggregation and active threat detection."
    },
    "WAF": {
        "name": "WAF",
        "category": "Network Security",
        "risk_if_missing": "Application layer attacks such as SQL Injection (SQLi), XSS, and CSRF.",
        "required_for": ["web_app", "api"],
        "description": "Web Application Firewall designed to protect applications from common internet exploits."
    },
    "IDS": {
        "name": "IDS",
        "category": "Network Security",
        "risk_if_missing": "Unnoticed malicious activities and policy violations silently traversing the network.",
        "required_for": ["infrastructure", "enterprise", "on_prem"],
        "description": "Intrusion Detection System that continuously monitors network traffic for suspicious networking activity."
    },
    "IPS": {
        "name": "IPS",
        "category": "Network Security",
        "risk_if_missing": "Inability to proactively drop malicious traffic before it reaches internal targets.",
        "required_for": ["infrastructure", "enterprise", "on_prem"],
        "description": "Intrusion Prevention System that actively blocks identified network threats in real-time."
    },
    "Encryption Service": {
        "name": "Encryption Service",
        "category": "Data Security",
        "risk_if_missing": "Exposure of sensitive data at rest or in transit.",
        "required_for": ["database", "storage", "microservices", "financial"],
        "description": "Service providing robust cryptographic operations and secure key lifecycle management."
    },
    "MFA": {
        "name": "MFA",
        "category": "Identity and Access Management",
        "risk_if_missing": "Account compromise through credential stuffing, phishing, or password spraying.",
        "required_for": ["web_app", "mobile_app", "admin_panel"],
        "description": "Multi-Factor Authentication requiring multiple pieces of evidence to authenticate user sessions."
    }
}

def get_security_component(name: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve a security component by its exact name.
    
    Args:
        name (str): The name of the security component to retrieve.
        
    Returns:
        Optional[Dict[str, Any]]: The required component dictionary, or None if not found.
    """
    return SECURITY_CATALOG.get(name)

def list_security_components() -> List[Dict[str, Any]]:
    """
    List all available security components in the catalog.
    
    Returns:
        List[Dict[str, Any]]: A list containing all component dictionaries.
    """
    return list(SECURITY_CATALOG.values())

def get_components_for_architecture_type(architecture_type: str) -> List[Dict[str, Any]]:
    """
    Return all security components that are required for a given architecture type.
    
    Args:
        architecture_type (str): The architecture type (e.g., 'web_app', 'api', 'microservices').
        
    Returns:
        List[Dict[str, Any]]: A list of component dictionaries supporting the architecture type.
    """
    return [
        component for component in SECURITY_CATALOG.values()
        if architecture_type in component.get("required_for", [])
    ]
