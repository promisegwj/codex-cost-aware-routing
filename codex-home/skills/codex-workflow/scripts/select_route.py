"""Read-only route advice. No agent dispatch, API calls, or model switching."""
import argparse
import json
from pathlib import Path
import sys
import tomllib

DEFAULT_CONTROLS = Path(__file__).resolve().parents[3] / "routing-controls.toml"
TIERS = ("T0", "T1", "T2", "T3", "T4")


def load_policy(path=DEFAULT_CONTROLS):
    with Path(path).open("rb") as stream:
        return tomllib.load(stream)


def select(task, policy):
    """Inputs are evidence-backed classifications, not inferred from free text."""
    if not isinstance(task, dict):
        raise ValueError("Task classification must be a JSON object")
    allowed = {"tier", "role", "complexity", "reasoning", "critical_risk",
               "shared_config", "engineering", "architecture", "high_confidence",
               "failure", "evidence", "previous_profile", "transitions_used",
               "writer_attempts_used"}
    unknown = set(task) - allowed
    if unknown:
        raise ValueError(f"Unknown fields: {sorted(unknown)}")
    tier = task.get("tier", "T1")
    role = task.get("role", "worker")
    complexity = task.get("complexity", "bounded")
    reasoning = task.get("reasoning", "routine")
    failure = task.get("failure", "none")
    evidence = task.get("evidence", "")
    if tier not in TIERS or role not in ("worker", "reviewer", "planner", "final", "explorer", "batch"):
        raise ValueError("Invalid tier or role")
    if complexity not in ("bounded", "integrated", "novel") or reasoning not in ("routine", "multistep", "dense"):
        raise ValueError("Invalid complexity or reasoning classification")
    if failure not in policy["adaptation_policy"]["failure_classes"]:
        raise ValueError("Invalid failure classification")
    if not isinstance(evidence, str):
        raise ValueError("evidence must be text")
    for field in ("critical_risk", "shared_config", "engineering", "architecture", "high_confidence"):
        if field in task and type(task[field]) is not bool:
            raise ValueError(f"{field} must be boolean")
    for field in ("transitions_used", "writer_attempts_used"):
        if type(task.get(field, 0)) is not int or task.get(field, 0) < 0:
            raise ValueError(f"{field} must be a nonnegative integer")
    profiles = policy["execution_profiles"]
    selection = policy["selection_policy"]
    adaptation = policy["adaptation_policy"]
    reasons = []
    if role in ("planner", "final") or task.get("architecture", False):
        tier = "T4"
        reasons.append("Architecture/planning/final closure requires T4 governance")
    elif task.get("critical_risk", False) and TIERS.index(tier) < 3:
        tier = "T3"
        reasons.append("Critical risk requires at least T3 governance")
    elif (task.get("shared_config", False) or task.get("engineering", False)) and TIERS.index(tier) < 2:
        tier = "T2"
        reasons.append("Shared config or engineering overlay requires at least T2")

    if role == "explorer":
        semantic, profile = "explorer", "luna_low"
    elif role == "batch":
        if task.get("critical_risk", False) or complexity != "bounded" or reasoning != "routine":
            raise ValueError("Batch is restricted to explicitly bounded low-risk mechanical scope")
        semantic, profile = "batch_worker", "luna_low"
    elif role == "final":
        semantic, profile = "reviewer_final", selection["final_review_profile"]
    elif role == "planner":
        semantic, profile = "planner_frontier", selection["planner_profile"]
    elif role == "reviewer":
        semantic = "reviewer_frontier" if tier in ("T3", "T4") else "reviewer_risk"
        profile = selection["frontier_default_profile"] if tier in ("T3", "T4") else "sol_medium"
    elif tier in ("T3", "T4"):
        semantic, profile = "worker_frontier", selection["frontier_default_profile"]
    elif tier in ("T0", "T1") and complexity == "bounded" and reasoning != "dense":
        semantic, profile = "root_direct", "luna_medium"
    else:
        tier = "T2"
        profile = selection["bounded_t2_profile"] if complexity == "bounded" and reasoning != "dense" else selection["integrated_t2_profile"]
        semantic = "worker_standard" if profile.startswith("luna_") else "worker_sol"
    if role not in ("batch", "explorer", "final") and reasoning == "dense" and evidence.strip():
        if profile.startswith("astra_"):
            profile = selection["frontier_coupled_profile"]
        else:
            profile = selection["dense_reasoning_profile"]
        reasons.append("Named dense reasoning evidence justifies greater initial effort")
    if complexity == "novel" and role not in ("batch", "explorer"):
        if evidence.strip():
            profile = "astra_medium"
            reasons.append("Named novel/coupled capability need justifies Astra")
        else:
            reasons.append("Novel classification lacks evidence; keep Sol baseline unless risk mandates Astra")
    previous = task.get("previous_profile")
    if previous is not None and previous not in profiles:
        raise ValueError("Unknown previous_profile")
    status = "advice_only"
    action = "execute_after_runtime_mapping_and_availability_checks"
    if failure != "none":
        if not evidence.strip():
            status, action = "needs_evidence", "complete_failure_packet"
        elif failure in adaptation["non_reasoning_failures"]:
            profile = previous or profile
            status, action = "repair_first", "record_capacity_fallback" if failure == "capacity" else "repair_identified_cause"
            reasons.append("No reasoning escalation for context, instruction, tool, environment or a diagnosed ordinary defect")
        elif previous is None:
            status, action = "needs_evidence", "record_actual_previous_profile"
        elif task.get("transitions_used", 0) >= adaptation["max_automatic_transitions"] or (role == "worker" and task.get("writer_attempts_used", 0) >= adaptation["max_total_writer_attempts_per_acceptance"]):
            profile = previous
            status, action = "budget_exhausted", "preserve_progress_and_return_failure_packet"
        elif role == "batch":
            profile = previous
            status, action = "stop", "reclassify_batch_scope_before_nonmechanical_work"
        else:
            if failure == "effort_limit":
                next_profile = adaptation.get(previous + "_effort_next", "stop_and_handoff")
            else:
                family = previous.split("_", 1)[0]
                next_profile = adaptation[family + "_capability_next"]
            if next_profile not in profiles:
                profile = previous
                status, action = "stop", next_profile
            else:
                profile = next_profile
                reasons.append(f"Evidence-backed {failure}: {previous} -> {profile}")
    elif previous is not None:
        raise ValueError("previous_profile is only valid with a classified failure")

    # Governance must never be downgraded by an adaptation path. Read-only T4
    # planning may use Sol; final closure and risk-bearing review/implementation may not.
    frontier_required = semantic in ("worker_frontier", "reviewer_frontier", "reviewer_final") or (task.get("critical_risk", False) and role not in ("explorer", "batch"))
    if frontier_required and not profile.startswith("astra_"):
        profile = selection["frontier_coupled_profile"] if reasoning == "dense" else selection["frontier_default_profile"]
        reasons.append("Preserved critical-risk/frontier capability floor")
    if role == "worker" and semantic not in ("worker_frontier",):
        if profile.startswith("astra_"):
            semantic = "worker_frontier"
        elif profile.startswith("sol_"):
            semantic = "worker_sol"
    chosen = profiles[profile]
    registered = policy["model_roles"].get(semantic, policy["root_default"])
    matches = all(chosen[key] == registered[key] for key in ("model", "model_reasoning_effort"))
    if role in ("worker", "batch") and task.get("writer_attempts_used", 0) >= adaptation["max_total_writer_attempts_per_acceptance"] and status not in ("needs_evidence", "budget_exhausted", "stop"):
        status, action = "budget_exhausted", "preserve_progress_and_return_failure_packet"
    if task.get("high_confidence", False):
        reasons.append("High confidence strengthens acceptance/validation/review; no automatic model promotion")
    if not reasons:
        reasons.append("Selected baseline for tier, role and semantic complexity")
    return {"policy_version": selection["version"], "status": status, "action": action,
            "tier": tier, "semantic_role": semantic, "profile": profile, **chosen,
            "reasons": reasons, "independent_contexts_required": tier in ("T3", "T4"),
            "review_required": role in ("worker", "batch") and (tier in ("T3", "T4") or task.get("high_confidence", False)),
            "remaining_automatic_transitions": max(0, adaptation["max_automatic_transitions"] - task.get("transitions_used", 0)),
            "remaining_writer_attempts": max(0, adaptation["max_total_writer_attempts_per_acceptance"] - task.get("writer_attempts_used", 0)),
            "specialist_gate": "not_evaluated_not_authorized",
            "invocation": "actual_root_profile_check" if semantic == "root_direct" else ("registered_role_after_actual_mapping_check" if matches else "default_child_explicit_model_effort_and_full_role_instructions"),
            "availability": "unverified", "route_executed": False}


def check_policy(policy, home):
    for role, expected in policy["model_roles"].items():
        path = home / "agents" / (role + ".toml")
        with path.open("rb") as stream:
            actual = tomllib.load(stream)
        for key in ("model", "model_reasoning_effort", "sandbox_mode"):
            if expected[key] != actual[key]:
                raise ValueError(f"Role registration mismatch: {role}.{key}")
    root_path = home / "config.toml"
    if not root_path.exists():
        root_path = home / "config-routing-snippet.toml"
    with root_path.open("rb") as stream:
        root = tomllib.load(stream)
    for key in ("model", "model_reasoning_effort"):
        if root[key] != policy["root_default"][key]:
            raise ValueError(f"Root default mismatch: {key}")
    for name, profile in policy["execution_profiles"].items():
        allowed = {"gpt-6-luna": ("low", "medium", "high"), "gpt-6.1-sol": ("medium", "high"), "gpt-6-astra": ("low", "medium", "high")}
        if profile["model_reasoning_effort"] not in allowed.get(profile["model"], ()):
            raise ValueError(f"Invalid automatic profile: {name}")
    for role, fallback in policy["fallback_profiles"].items():
        with (home / fallback["profile"]).open("rb") as stream:
            actual = tomllib.load(stream)
        for key in ("model", "model_reasoning_effort", "sandbox_mode"):
            if actual[key] != fallback[key]:
                raise ValueError(f"Fallback profile mismatch: {role}.{key}")
    for name, role in {"mini": "batch_worker", "worker-high": "worker_standard", "highrisk": "worker_frontier", "planner": "planner_frontier", "reasoning-specialist": "reasoning_specialist"}.items():
        path = home / "profiles" / (name + ".config.toml")
        if path.exists():
            with path.open("rb") as stream:
                actual = tomllib.load(stream)
            if any(actual[key] != policy["model_roles"][role][key] for key in ("model", "model_reasoning_effort")):
                raise ValueError(f"Native convenience profile mismatch: {name}")
    return {"status": "ok", "roles_checked": len(policy["model_roles"]), "profiles_checked": len(policy["execution_profiles"]), "runtime_availability": "not_tested"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--controls", type=Path, default=DEFAULT_CONTROLS)
    parser.add_argument("--task", type=Path, help="UTF-8 JSON classification file")
    parser.add_argument("--check-policy", action="store_true")
    args = parser.parse_args()
    try:
        policy = load_policy(args.controls)
        if args.check_policy:
            result = check_policy(policy, args.controls.parent)
        else:
            task = json.loads(args.task.read_text(encoding="utf-8-sig")) if args.task else json.load(sys.stdin)
            result = select(task, policy)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except (ValueError, OSError, KeyError) as error:
        print(json.dumps({"status": "invalid_input_or_policy", "error": str(error)}, ensure_ascii=False), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
