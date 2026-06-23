from typing import List, Dict, Any
from backend.security.security_catalog import SECURITY_CATALOG
from backend.security.security_validator import validate_architecture_security

RECOMMENDATIONS: Dict[str, str] = {
    "Authentication": "Add Authentication service to protect user access.",
    "RBAC": "Implement role-based access control.",
    "API Gateway": "Add API Gateway to secure and manage external traffic.",
    "WAF": "Deploy a Web Application Firewall.",
    "Audit Logging": "Enable centralized audit logging.",
    "Monitoring": "Add monitoring and observability.",
    "Encryption Service": "Encrypt sensitive data at rest and in transit.",
    "Secrets Manager": "Use a secrets management solution.",
    "SIEM": "Deploy a SIEM for security event aggregation and threat detection.",
    "IDS": "Implement an Intrusion Detection System.",
    "IPS": "Implement an Intrusion Prevention System.",
    "MFA": "Require Multi-Factor Authentication for user access."
}

def calculate_security_score(validation_result: Dict[str, Any]) -> int:
    """
    Calculate the security score based on missing components.
    Starts at 100.
    Critical: -20, High: -10, Medium: -5.
    """
    score = 100
    score -= len(validation_result.get("critical", [])) * 20
    score -= len(validation_result.get("high", [])) * 10
    score -= len(validation_result.get("medium", [])) * 5
    return max(0, min(100, score))


def generate_recommendations(missing_components: List[Dict[str, Any]]) -> List[str]:
    """
    Generate actionable recommendations based on missing security components.
    """
    recommendations = []
    for comp in missing_components:
        name = comp.get("name", "")
        if name in RECOMMENDATIONS:
            recommendations.append(RECOMMENDATIONS[name])
        else:
            recommendations.append(f"Add {name}.")
    return recommendations


def generate_security_report(nodes: List[Dict[str, Any]], edges: List[Dict[str, Any]], validation_result: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Generate a full security report containing validation results,
    security score, risk level, and recommendations.
    """
    if validation_result is None:
        validation_result = validate_architecture_security(nodes, edges)
    
    security_score = calculate_security_score(validation_result)
    
    if security_score >= 80:
        risk_level = "LOW"
    elif security_score >= 50:
        risk_level = "MEDIUM"
    else:
        risk_level = "HIGH"
        
    recommendations = generate_recommendations(validation_result.get("missing_components", []))
    
    return {
        "security_score": security_score,
        "risk_level": risk_level,
        "missing_components": validation_result.get("missing_components", []),
        "critical": validation_result.get("critical", []),
        "high": validation_result.get("high", []),
        "medium": validation_result.get("medium", []),
        "recommendations": recommendations
    }
