import unittest

from app.falco_router.rollout import WorkloadMonitor, workload_complete


class RolloutTests(unittest.TestCase):
    def test_deployment_waits_for_new_generation_and_available_replicas(self):
        workload = {
            "metadata": {"generation": 8},
            "spec": {"replicas": 2},
            "status": {"observedGeneration": 8, "updatedReplicas": 2, "availableReplicas": 1},
        }
        self.assertFalse(workload_complete("deployments", workload))
        workload["status"]["availableReplicas"] = 2
        self.assertTrue(workload_complete("deployments", workload))

    def test_deployment_does_not_complete_before_generation_is_observed(self):
        workload = {
            "metadata": {"generation": 5},
            "spec": {"replicas": 1},
            "status": {"observedGeneration": 4, "updatedReplicas": 1, "availableReplicas": 1},
        }
        self.assertFalse(workload_complete("deployments", workload))

    def test_statefulset_and_daemonset_completion(self):
        statefulset = {
            "metadata": {"generation": 1},
            "spec": {"replicas": 2},
            "status": {"observedGeneration": 1, "updatedReplicas": 2, "readyReplicas": 2},
        }
        daemonset = {
            "metadata": {"generation": 3},
            "status": {
                "observedGeneration": 3,
                "desiredNumberScheduled": 4,
                "updatedNumberScheduled": 4,
                "numberAvailable": 4,
            },
        }
        self.assertTrue(workload_complete("statefulsets", statefulset))
        self.assertTrue(workload_complete("daemonsets", daemonset))

    def test_pod_and_job_completion(self):
        pod = {"status": {"phase": "Running", "conditions": [{"type": "Ready", "status": "True"}]}}
        job = {"status": {"conditions": [{"type": "Complete", "status": "True"}]}}
        self.assertTrue(workload_complete("pods", pod))
        self.assertTrue(workload_complete("jobs", job))

    def test_deployment_progress_deadline_failure(self):
        workload = {
            "metadata": {"generation": 2},
            "status": {
                "observedGeneration": 2,
                "conditions": [
                    {"type": "Progressing", "status": "False", "reason": "ProgressDeadlineExceeded"}
                ]
            }
        }
        self.assertTrue(WorkloadMonitor._deployment_failed(workload))

    def test_old_deployment_failure_condition_does_not_fail_new_generation(self):
        workload = {
            "metadata": {"generation": 3},
            "status": {
                "observedGeneration": 2,
                "conditions": [
                    {"type": "Progressing", "status": "False", "reason": "ProgressDeadlineExceeded"}
                ],
            },
        }
        self.assertFalse(WorkloadMonitor._deployment_failed(workload))


if __name__ == "__main__":
    unittest.main()
