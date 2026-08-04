"""Candidate-sample generator for the CyberShield-Arch dataset.

Two modes:

- ``template`` (default): deterministic, zero-GPU synthesis of architectures
  from the domain templates in ``dataset/templates``. Produces both an
  insecure variant (no controls embedded) and a hardened variant (domain
  controls embedded as nodes) per (domain, difficulty) pair, giving the
  dataset genuine security-label diversity.
- ``model``: runs the local Gemma 3 generator (``backend.core.inference``) on
  the template seed instructions. Requires GPU and a cached model.

Security labels are always computed with the application's own security
engine, so generated samples are consistent with the production /explain
pipeline automatically.

Usage:
    python -m backend.dataset.dataset_generator --mode template
    python -m backend.dataset.dataset_generator --mode model --domains banking healthcare
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

from backend.dataset.models import Architecture, Edge, Metadata, Node, Sample
from backend.dataset.schema import (
    DIFFICULTIES,
    DOCS_DIR,
    GENERATED_DIR,
    PROMPTS_DIR,
    TEMPLATES_DIR,
    load_json,
    load_samples_from_dir,
    write_json,
)
from backend.dataset.security import compute_security_section

VARIANT_INSTRUCTIONS = {
    "insecure": {
        "prefix": "Design the initial, unprotected version of the following system.",
        "suffix": "Do not add any security appliances to this version.",
    },
    "hardened": {
        "prefix": "Design a fully secured version of the following system.",
        "suffix": "Embed the required security controls directly into the architecture.",
    },
}


def load_domain_template(domain: str) -> dict[str, Any]:
    path = TEMPLATES_DIR / f"domain_{domain}.json"
    if not path.exists():
        raise FileNotFoundError(f"domain template not found: {path}")
    return load_json(path)


def load_prompt_template(name: str) -> dict[str, Any]:
    path = PROMPTS_DIR / f"{name}.json"
    if not path.exists():
        raise FileNotFoundError(f"prompt template not found: {path}")
    return load_json(path)


def render_prompt(template: dict[str, Any], **kwargs: Any) -> str:
    text = template["template"]
    for placeholder in template.get("placeholders", []):
        value = str(kwargs.get(placeholder, f"{{{placeholder}}}"))
        text = text.replace("{{" + placeholder + "}}", value)
    return text


def build_architecture(
    template: dict[str, Any],
    difficulty: str,
    embed_controls: bool,
) -> Architecture:
    """Deterministically synthesize an architecture from a domain template.

    The node budget follows ``difficulty_map`` (4/6/8). The hardened variant
    reserves most of the budget for security controls, ordered by impact
    (critical controls first), so it produces meaningfully higher scores.
    """
    target = int(template["difficulty_map"][difficulty])
    services = list(template["services"])
    databases = list(template["databases"])

    nodes: list[Node] = [Node(id="web", type="ui")]
    edges: list[Edge] = []
    seen: set[tuple[str, str]] = set()

    def add_edge(source: str, target: str, label: str) -> None:
        key = (source, target)
        if source != target and key not in seen:
            seen.add(key)
            edges.append(Edge(source=source, target=target, label=label))

    if embed_controls:
        svc_count = min(len(services), 2 if target >= 6 else 1)
        db_count = min(1, len(databases)) if target >= 5 else 0
        service_names = services[:svc_count]
        db_names = databases[:db_count]

        nodes.extend(Node(id=s.replace("-", "_"), type="service") for s in service_names)
        nodes.extend(Node(id=d.replace("-", "_"), type="database") for d in db_names)

        control_slots = target - len(nodes)
        if control_slots > 0:
            for control in _ordered_controls(template.get("expected_security_controls", []))[:control_slots]:
                control_id = _CONTROL_IDS.get(control, control.lower())
                nodes.append(Node(id=control_id, type="service"))
                add_edge("web", control_id, "HTTP")

        for s in service_names:
            svc = s.replace("-", "_")
            add_edge("web", svc, "HTTP")
            for d in db_names:
                add_edge(svc, d.replace("-", "_"), "DB Query")
        return Architecture(nodes=nodes, edges=edges)

    db_count = min(2, len(databases)) if target >= 5 else min(1, len(databases))
    service_count = max(1, min(len(services), target - 1 - db_count))
    service_names = services[:service_count]
    db_names = databases[:db_count]

    nodes.extend(Node(id=s.replace("-", "_"), type="service") for s in service_names)
    nodes.extend(Node(id=d.replace("-", "_"), type="database") for d in db_names)

    for service in service_names:
        svc = service.replace("-", "_")
        add_edge("web", svc, "HTTP")
        for db in db_names:
            add_edge(svc, db.replace("-", "_"), "DB Query")

    return Architecture(nodes=nodes[: target], edges=edges)


def _ordered_controls(controls: list[str]) -> list[str]:
    """Order controls by security impact (critical, high, medium then name)."""
    rank = {"critical": 0, "high": 1, "medium": 2}
    from backend.security.security_catalog import SECURITY_CATALOG

    def sort_key(control: str) -> tuple[int, str]:
        return rank.get(SECURITY_CATALOG.get(control, {}).get("risk_level", "medium"), 2), control

    return sorted(controls, key=sort_key)


_CONTROL_IDS: dict[str, str] = {
    "Authentication": "authentication",
    "RBAC": "rbac",
    "API Gateway": "api gateway",
    "Audit Logging": "audit logging",
    "Monitoring": "monitoring",
    "Secrets Manager": "secrets manager",
    "SIEM": "siem",
    "WAF": "waf",
    "IDS": "ids",
    "IPS": "ips",
    "Encryption Service": "encryption service",
    "MFA": "mfa",
}


def build_instruction(
    template: dict[str, Any],
    prompt: dict[str, Any],
    architecture: Architecture,
    variant: str,
) -> str:
    domain = template["domain"]
    services = ", ".join(template["services"][:3])
    databases = ", ".join(template["databases"][:2])
    base = (
        f"Design a {domain} system where {services} work together, "
        f"backed by {databases}, with a user-facing entry point."
    )
    prefix = VARIANT_INSTRUCTIONS[variant]["prefix"]
    suffix = VARIANT_INSTRUCTIONS[variant]["suffix"]
    task = f"{prefix}\n{base}\n{suffix}"

    controls = ", ".join(template.get("expected_security_controls", []))
    return render_prompt(
        prompt,
        instruction=task,
        controls=controls,
        architecture=architecture.to_dict(),
    )


def _sample_from_architecture(
    sample_id: str,
    domain: str,
    difficulty: str,
    instruction: str,
    architecture: Architecture,
    generated_by: str,
) -> Sample:
    security = compute_security_section(
        [node.to_dict() for node in architecture.nodes],
        [edge.to_dict() for edge in architecture.edges],
    )
    return Sample(
        id=sample_id,
        domain=domain,
        difficulty=difficulty,
        instruction=instruction,
        architecture=architecture,
        security=security,
        metadata=Metadata(
            source="synthetic" if generated_by == "template-v1" else "model",
            generated_by=generated_by,
            reviewed=False,
            version="1.0",
        ),
    )


def generate_template_samples(
    domains: list[str],
    difficulties: list[str],
    prompt_name: str,
    force: bool,
) -> list[Sample]:
    prompt = load_prompt_template(prompt_name)
    samples: list[Sample] = []
    existing = {path.stem for path in load_samples_from_dir(GENERATED_DIR)}

    for domain in domains:
        template = load_domain_template(domain)
        for difficulty in difficulties:
            for variant in ("insecure", "hardened"):
                sample_id = f"{domain}-{difficulty}-{variant}"
                out_path = GENERATED_DIR / f"{sample_id}.json"
                if not force and sample_id in existing:
                    continue
                architecture = build_architecture(template, difficulty, embed_controls=(variant == "hardened"))
                instruction = build_instruction(template, prompt, architecture, variant)
                sample = _sample_from_architecture(
                    sample_id, domain, difficulty, instruction, architecture, "template-v1"
                )
                write_json(out_path, sample.to_dict())
                samples.append(sample)
    return samples


def generate_model_samples(
    domains: list[str],
    prompt_name: str,
    force: bool,
) -> list[Sample]:
    """Generate samples through the local Gemma 3 generator (GPU required)."""
    try:
        from backend.core.inference import generate_architecture
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError("model mode requires backend.core.inference (GPU + torch)") from exc

    prompt = load_prompt_template(prompt_name)
    samples: list[Sample] = []
    existing = {path.stem for path in load_samples_from_dir(GENERATED_DIR)}

    for domain in domains:
        template = load_domain_template(domain)
        for seed in template.get("seed_instructions", []):
            sample_id = f"{domain}-model-{abs(hash(seed)) % 10000:04d}"
            out_path = GENERATED_DIR / f"{sample_id}.json"
            if not force and sample_id in existing:
                continue
            instruction = render_prompt(prompt, instruction=seed, controls=", ".join(template.get("expected_security_controls", [])))
            architecture_dict, _raw = generate_architecture(instruction, deterministic=True)
            architecture = Architecture(
                nodes=[Node(**node) for node in architecture_dict.get("nodes", [])],
                edges=[Edge(**edge) for edge in architecture_dict.get("edges", [])],
            )
            sample = _sample_from_architecture(
                sample_id, domain, "medium", instruction, architecture, "gemma-3-4b"
            )
            write_json(out_path, sample.to_dict())
            samples.append(sample)
    return samples


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate candidate dataset samples.")
    parser.add_argument(
        "--mode",
        choices=["template", "model"],
        default="template",
        help="template = deterministic synthesis (no GPU); model = local Gemma 3.",
    )
    parser.add_argument("--domains", nargs="+", default=None, help="Domains to generate; defaults to all templates.")
    parser.add_argument(
        "--difficulty",
        nargs="+",
        choices=sorted(DIFFICULTIES),
        default=["easy", "medium", "hard"],
        help="Difficulty tiers to generate.",
    )
    parser.add_argument("--prompt", default="architecture_generation", help="Prompt template from dataset/prompts.")
    parser.add_argument("--force", action="store_true", help="Overwrite existing generated files.")
    return parser.parse_args(argv)


def generate_samples(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if args.domains is None:
        args.domains = sorted(path.stem.removeprefix("domain_") for path in TEMPLATES_DIR.glob("domain_*.json"))

    if args.mode == "template":
        samples = generate_template_samples(args.domains, args.difficulty, args.prompt, args.force)
    else:
        samples = generate_model_samples(args.domains, args.prompt, args.force)

    print(f"[generator] wrote {len(samples)} candidate samples to {GENERATED_DIR.relative_to(Path.cwd())}")
    return 0


if __name__ == "__main__":
    sys.exit(generate_samples())