import json
from typing import List, Dict, Any
from backend.security.security_catalog import SECURITY_CATALOG
from backend.security.security_validator import validate_architecture_security
from backend.security.security_report import generate_security_report

def detect_architecture_types(nodes: List[Dict[str, Any]]) -> List[str]:
    types = set()
    for node in nodes:
        try:
            node_str = json.dumps(node).lower()
        except TypeError:
            node_str = str(node).lower()
        
        if any(kw in node_str for kw in ["bank", "finance", "payment", "transaction"]):
            types.add("banking_system")
        if any(kw in node_str for kw in ["health", "medical", "patient", "clinic"]):
            types.add("healthcare_system")
        if any(kw in node_str for kw in ["cyber", "security", "threat", "soc"]):
            types.add("cybersecurity_system")
        if any(kw in node_str for kw in ["ecommerce", "shop", "cart", "retail", "store"]):
            types.add("ecommerce_system")
        if any(kw in node_str for kw in ["microservice", "event bus", "message queue"]):
            types.add("microservices")
        if any(kw in node_str for kw in ["web", "frontend", "ui"]):
            types.add("web_application")
    return list(types)

def build_security_summary(report: Dict[str, Any]) -> str:
    nodes = report.get("_nodes", [])
    has_frontend = any(any(kw in str(n).lower() for kw in ["ui", "frontend", "client", "react", "app"]) for n in nodes)
    has_api = any(any(kw in str(n).lower() for kw in ["api", "backend", "service"]) for n in nodes)
    has_db = any(any(kw in str(n).lower() for kw in ["db", "database", "postgres", "storage"]) for n in nodes)
    
    components = []
    if has_frontend: components.append("a frontend")
    if has_api: components.append("an API service")
    if has_db: components.append("a database")
    
    contains_str = "contains "
    if not components:
        contains_str += "various components"
    elif len(components) == 1:
        contains_str += components[0]
    else:
        contains_str += f"{', '.join(components[:-1])} and {components[-1]}"
        
    missing = [c.get("name") for c in report.get("missing_components", [])]
    if missing:
        missing_str = ", ".join(missing[:-1]) + f" and {missing[-1]}" if len(missing) > 1 else missing[0]
        action = "requires immediate remediation." if report.get("risk_level") in ["HIGH", "MEDIUM"] else "is acceptable."
        return f"Architecture {contains_str} but lacks {missing_str}. Overall security posture is {report.get('risk_level')} RISK and {action}"
    else:
        return f"Architecture {contains_str} and meets all baseline security requirements. Overall security posture is {report.get('risk_level')} RISK."

def analyze_architecture_security(nodes: List[Dict[str, Any]], edges: List[Dict[str, Any]]) -> Dict[str, Any]:
    # 1. Base validation
    validation_result = validate_architecture_security(nodes, edges)
    
    # 2. Detect types
    arch_types = detect_architecture_types(nodes)
    
    # 3. Apply domain rules
    required_controls = set()
    if "banking_system" in arch_types:
         required_controls.update(["MFA", "Encryption Service", "Audit Logging", "SIEM"])
    if "healthcare_system" in arch_types:
         required_controls.update(["MFA", "Encryption Service", "Audit Logging"])
    if "cybersecurity_system" in arch_types:
         required_controls.update(["SIEM", "IDS", "IPS", "Monitoring"])
    if "ecommerce_system" in arch_types:
         required_controls.update(["Authentication", "RBAC", "WAF", "API Gateway"])
         
    # Check what is already physically in the nodes to satisfy those
    existing_components = set()
    for node in nodes:
        try:
            node_str = json.dumps(node).lower()
        except TypeError:
            node_str = str(node).lower()
        for comp_name in required_controls:
            if comp_name.lower() in node_str:
                existing_components.add(comp_name)
                
    missing = required_controls - existing_components
    current_missing = {c['name'] for c in validation_result['missing_components']}
    missing_to_add = missing - current_missing
    
    for name in missing_to_add:
        component = SECURITY_CATALOG.get(name)
        if component:
            validation_result["missing_components"].append(component)
            risk_level = component.get("risk_level", "medium").lower()
            if risk_level == "critical":
                validation_result["critical"].append(component)
            elif risk_level == "high":
                validation_result["high"].append(component)
            else:
                validation_result["medium"].append(component)
                
    # 4. Generate report with the combined validation results
    report = generate_security_report(nodes, edges, validation_result)
    report["_nodes"] = nodes
    
    # 5. Build summary
    summary = build_security_summary(report)
    
    # Clean up proxy variable
    if "_nodes" in report:
        del report["_nodes"]
    
    # 6. Format Return output
    return {
        "security_score": report["security_score"],
        "risk_level": report["risk_level"],
        "missing_components": report["missing_components"],
        "recommendations": report["recommendations"],
        "security_summary": summary
    }
