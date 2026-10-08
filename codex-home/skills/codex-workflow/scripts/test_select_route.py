"""Regression scenarios for capability, effort, governance and stop boundaries."""
import unittest
from select_route import load_policy, select, check_policy, DEFAULT_CONTROLS


class RouteScenarios(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.policy = load_policy()

    def test_policy_registration_consistency(self):
        self.assertEqual(check_policy(self.policy, DEFAULT_CONTROLS.parent)["status"], "ok")

    def test_route_scenarios(self):
        cases = [
            ("simple", {}, "sol_low", "T1", "advice_only"),
            ("bounded_config", {"shared_config": True}, "sol_low", "T2", "advice_only"),
            ("integrated", {"tier": "T2", "complexity": "integrated"}, "sol_medium", "T2", "advice_only"),
            ("dense_missing_evidence", {"tier": "T2", "reasoning": "dense"}, "sol_medium", "T2", "advice_only"),
            ("dense_named", {"tier": "T2", "reasoning": "dense", "evidence": "Coupled constraints and exact boundary derivation"}, "sol_high", "T2", "advice_only"),
            ("critical", {"critical_risk": True}, "astra_low", "T3", "advice_only"),
            ("critical_dense", {"critical_risk": True, "reasoning": "dense", "evidence": "Interdependent rollback ordering"}, "astra_medium", "T3", "advice_only"),
            ("planner", {"role": "planner"}, "astra_high", "T1", "advice_only"),
            ("critical_planner", {"role": "planner", "critical_risk": True}, "astra_high", "T3", "advice_only"),
            ("final", {"role": "final"}, "astra_high", "T1", "advice_only"),
            ("confidence", {"high_confidence": True}, "sol_low", "T1", "advice_only"),
            ("effort", {"tier": "T2", "failure": "effort_limit", "previous_profile": "sol_medium", "evidence": "Task understood, required boundary missed", "writer_attempts_used": 1}, "sol_high", "T2", "advice_only"),
            ("capability", {"tier": "T2", "failure": "capability_limit", "previous_profile": "sol_medium", "evidence": "Persistent incorrect cross-module abstraction"}, "astra_medium", "T2", "advice_only"),
            ("environment", {"tier": "T2", "failure": "environment", "previous_profile": "sol_medium", "evidence": "Interpreter failed to launch"}, "sol_medium", "T2", "repair_first"),
            ("capacity", {"tier": "T2", "failure": "capacity", "previous_profile": "sol_medium", "evidence": "Model at capacity"}, "sol_medium", "T2", "repair_first"),
            ("ordinary_defect", {"tier": "T2", "failure": "validation_defect", "previous_profile": "sol_medium", "evidence": "Known off-by-one in index"}, "sol_medium", "T2", "repair_first"),
            ("missing_failure_evidence", {"tier": "T2", "failure": "effort_limit", "previous_profile": "sol_medium"}, "sol_low", "T2", "needs_evidence"),
            ("missing_actual_profile", {"tier": "T2", "failure": "effort_limit", "evidence": "Missed constraint"}, "sol_low", "T2", "needs_evidence"),
            ("transition_budget", {"tier": "T2", "failure": "effort_limit", "previous_profile": "sol_high", "evidence": "Named insufficiency", "transitions_used": 2}, "sol_high", "T2", "budget_exhausted"),
            ("writer_budget", {"tier": "T2", "writer_attempts_used": 3}, "sol_low", "T2", "budget_exhausted"),
            ("astra_stop", {"tier": "T3", "failure": "capability_limit", "previous_profile": "astra_medium", "evidence": "Assigned model cannot resolve coupled proof"}, "astra_medium", "T3", "stop"),
            ("astra_effort", {"tier": "T3", "failure": "effort_limit", "previous_profile": "astra_medium", "evidence": "Medium missed a demonstrated constraint"}, "astra_high", "T3", "advice_only"),
            ("batch_scope", {"role": "batch", "trivial_execution": True, "execution_evidence": "Exact substitutions supplied", "failure": "capability_limit", "previous_profile": "luna_medium", "evidence": "Work is no longer mechanical"}, "luna_medium", "T1", "stop"),
        ]
        for name, task, profile, tier, status in cases:
            with self.subTest(name=name):
                result = select(task, self.policy)
                self.assertEqual((result["profile"], result["tier"], result["status"]), (profile, tier, status))
                self.assertFalse(result["route_executed"])
                self.assertEqual(result["availability"], "unverified")
                self.assertEqual(result["specialist_gate"], "not_evaluated_not_authorized")

    def test_mandatory_boundaries_after_every_override_and_failure(self):
        for tier in ("T0", "T1", "T2", "T3", "T4"):
            for role in ("planner", "final"):
                for modifiers in ({}, {"reasoning": "dense", "evidence": "Coupled constraints"},
                                  {"complexity": "novel", "evidence": "Novel coupled abstraction"},
                                  {"trivial_execution": True, "execution_evidence": "Exact command supplied"}):
                    result = select({"tier": tier, "role": role, **modifiers}, self.policy)
                    self.assertEqual((result["profile"], result["tier"]), ("astra_high", tier))
                    self.assertTrue(result["independent_contexts_required"])
                for failure in self.policy["adaptation_policy"]["failure_classes"]:
                    if failure == "none":
                        continue
                    for previous in self.policy["execution_profiles"]:
                        for budget in ({}, {"transitions_used": 2, "writer_attempts_used": 3}):
                            result = select({"tier": tier, "role": role, "failure": failure,
                                             "previous_profile": previous, "evidence": "Named diagnosis", **budget}, self.policy)
                            self.assertEqual(result["profile"], "astra_high")
                stopped = select({"tier": tier, "role": role, "failure": "effort_limit",
                                  "previous_profile": "astra_high", "evidence": "High missed proof"}, self.policy)
                self.assertEqual(stopped["status"], "stop")

    def test_luna_requires_explicit_deterministic_execution_evidence(self):
        eligible = {"tier": "T0", "trivial_execution": True,
                    "execution_evidence": "Replace the exact supplied literal in the one named file"}
        self.assertEqual(select(eligible, self.policy)["profile"], "luna_medium")
        for modifiers in ({"trivial_execution": False}, {"execution_evidence": " "},
                          {"reasoning": "multistep"}, {"complexity": "integrated"},
                          {"shared_config": True}, {"engineering": True}, {"critical_risk": True},
                          {"architecture": True}, {"tier": "T2"}, {"role": "explorer"}):
            result = select({**eligible, **modifiers}, self.policy)
            self.assertFalse(result["profile"].startswith("luna_"))
        result = select({"failure": "environment", "previous_profile": "luna_medium",
                         "evidence": "Interpreter failed"}, self.policy)
        self.assertEqual(result["profile"], "sol_low")
        self.assertTrue(select(eligible, self.policy)["review_required"])

    def test_sol_low_and_luna_adaptation(self):
        for previous, expected in (("sol_low", "sol_medium"), ("luna_medium", "sol_medium")):
            result = select({"failure": "effort_limit", "previous_profile": previous,
                             "evidence": "Task now needs a demonstrated reasoning derivation"}, self.policy)
            self.assertEqual(result["profile"], expected)

    def test_effort_override_cannot_use_fixed_registration(self):
        result = select({"tier": "T2", "reasoning": "dense", "evidence": "Named dense constraints"}, self.policy)
        self.assertEqual(result["semantic_role"], "worker_sol")
        self.assertTrue(result["invocation"].startswith("default_child"))

    def test_invalid_and_unsafe_inputs(self):
        for task in ([], None, {"critical_risk": "false"}, {"transitions_used": -1},
                     {"writer_attempts_used": True}, {"tier": "T9"},
                     {"previous_profile": "sol_medium"}, {"file_count": 10},
                     {"effort": "max"}, {"role": "batch", "critical_risk": True}, {"trivial_execution": "true"}, {"execution_evidence": []}, {"role": "batch"}):
            with self.subTest(task=task), self.assertRaises(ValueError):
                select(task, self.policy)

    def test_confidence_and_budget_accounting(self):
        result = select({"tier": "T2", "high_confidence": True, "transitions_used": 1, "writer_attempts_used": 2}, self.policy)
        self.assertTrue(result["review_required"])
        self.assertEqual(result["remaining_automatic_transitions"], 1)
        self.assertEqual(result["remaining_writer_attempts"], 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
