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
               "writer_attempts_used", "trivial_execution", "execution_evidence"}
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
    execution_evidence = task.get("execution_evidence", "")
    if not isinstance(execution_evidence, str):
        raise ValueError("execution_evidence must be text")
    if not isinstance(evidence, str):
        raise ValueError("evidence must be text")
    for field in ("critical_risk", "shared_config", "engineering", "architecture", "high_confidence", "trivial_execution"):
        if field in task and type(task[field]) is not bool:
            raise ValueError(f"{field} must be boolean")
    for field in ("transitions_used", "writer_attempts_used"):
        if type(task.get(field, 0)) is not int or task.get(field, 0) < 0:
            raise ValueError(f"{field} must be a nonnegative integer")
    profiles = policy["execution_profiles"]
    selection = policy["selection_policy"]
    adaptation = policy["adaptation_policy"]
    reasons = []
    if task.get("architecture", False):
        tier = "T4"
        reasons.append("Architecture requires T4 governance; boundary roles do not determine tier")
    elif task.get("critical_risk", False) and TIERS.index(tier) < 3:
        tier = "T3"
        reasons.append("Critical risk requires at least T3 governance")
    elif (task.get("shared_config", False) or task.get("engineering", False)) and TIERS.index(tier) < 2:
        tier = "T2"
        reasons.append("Shared config or engineering overlay requires at least T2")

    luna_eligible = (task.get("trivial_execution", False) and bool(execution_evidence.strip())
                     and tier in ("T0", "T1") and complexity == "bounded"
                     and reasoning == "routine" and not any(task.get(key, False) for key in
                     ("critical_risk", "shared_config", "engineering", "architecture")))
    if role == "explorer":
        semantic, profile = "explorer", "sol_low"
    elif role == "batch":
        if not luna_eligible:
            raise ValueError("Batch requires evidenced trivial deterministic execution without substantive reasoning or risk overlays")
        semantic, profile = "batch_worker", "luna_medium"
    elif role == "final":
        semantic, profile = "reviewer_final", selection["final_review_profile"]
    elif role == "planner":
        semantic, profile = "planner_frontier", selection["planner_profile"]
    elif role == "reviewer":
        semantic = "reviewer_frontier" if tier in ("T3", "T4") else "reviewer_risk"
        profile = selection["frontier_default_profile"] if tier in ("T3", "T4") else "sol_medium"
    elif tier in ("T3", "T4"):
        semantic, profile = "worker_frontier", selection["frontier_default_profile"]
    elif luna_eligible:
        semantic, profile = "batch_worker", "luna_medium"
    elif tier in ("T0", "T1") and complexity == "bounded" and reasoning == "routine":
        semantic, profile = "root_direct", "sol_low"
    else:
        tier = "T2"
        profile = selection["bounded_t2_profile"] if complexity == "bounded" and reasoning == "routine" else selection["integrated_t2_profile"]
        semantic = "worker_standard" if profile == "sol_low" else "worker_sol"
    if role not in ("batch", "explorer", "planner", "final") and reasoning == "dense" and evidence.strip():
        if profile.startswith("astra_"):
            profile = selection["frontier_coupled_profile"]
        else:
            profile = selection["dense_reasoning_profile"]
        reasons.append("Named dense reasoning evidence justifies greater initial effort")
    if complexity == "novel" and role not in ("batch", "explorer", "planner", "final"):
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

    # Apply floors AFTER all initial selection, failure repair and stop paths.
    if role in ("planner", "final"):
        if profile != "astra_high":
            reasons.append("Restored mandatory Astra high boundary floor after adaptation")
        profile = "astra_high"
    else:
        frontier_required = semantic in ("worker_frontier", "reviewer_frontier") or (task.get("critical_risk", False) and role not in ("explorer", "batch"))
        if frontier_required and not profile.startswith("astra_"):
            profile = selection["frontier_coupled_profile"] if reasoning == "dense" else selection["frontier_default_profile"]
            reasons.append("Preserved critical-risk/frontier capability floor")
        if profile.startswith("luna_") and (not luna_eligible or role not in ("worker", "batch")):
            profile = "sol_low"
            reasons.append("Restored Sol floor: Luna eligibility absent")
    if role == "worker":
        if profile.startswith("astra_"):
            semantic = "worker_frontier"
        elif profile == "sol_low":
            semantic = "root_direct" if tier in ("T0", "T1") else "worker_standard"
        elif profile.startswith("sol_"):
            semantic = "worker_sol"
        elif profile == "luna_medium":
            semantic = "batch_worker"
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
            "reasons": reasons, "independent_contexts_required": True,
            "initial_planning_required": True, "final_review_profile": "astra_high",
            "boundary_roles": ["planner_frontier", "reviewer_final"],
            "luna_eligible": bool(luna_eligible),
            "review_required": role in ("worker", "batch"),
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
        allowed = {"gpt-6-luna": ("medium",), "gpt-6.1-sol": ("low", "medium", "high"), "gpt-6-astra": ("low", "medium", "high")}
        if profile["model_reasoning_effort"] not in allowed.get(profile["model"], ()):
            raise ValueError(f"Invalid automatic profile: {name}")
    for role, fallback in policy.get("fallback_profiles", {}).items():
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
    if any(policy["selection_policy"][key] != "astra_high" for key in ("planner_profile", "final_review_profile")):
        raise ValueError("Boundary selection profiles must be Astra high")
    for role in ("planner_frontier", "reviewer_final"):
        if (policy["model_roles"][role]["model"], policy["model_roles"][role]["model_reasoning_effort"]) != ("gpt-6-astra", "high"):
            raise ValueError("Mandatory Astra high boundary registration floor")
    if (policy["root_default"]["model"], policy["root_default"]["model_reasoning_effort"]) != ("gpt-6.1-sol", "low"):
        raise ValueError("Default root must be Sol low")
    if any(name != "luna_medium" and profile["model"] == "gpt-6-luna" for name, profile in policy["execution_profiles"].items()):
        raise ValueError("Luna automatic profile must be medium only")
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
