import unittest

from app.falco_router.formatter import format_message


class FormatterTests(unittest.TestCase):
    def test_workload_change(self):
        event = {
            "rule": "VNPost K8s Human User Workload Change",
            "priority": "Warning",
            "time": "2026-10-20T03:46:06.837Z",
            "output_fields": {
                "ka.target.namespace": "tf-lab2-stag",
                "ka.target.resource": "deployments",
                "ka.target.name": "falco-message-format-test",
                "ka.verb": "patch",
                "ka.response.code": 200,
                "ka.user.name": "falco-rule-test-user",
            },
        }
        self.assertEqual(
            format_message(event),
            "🚨 [FIRING: WARNING] Thay đổi workload\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "Severity: WARNING\n"
            "Cluster: Kubernetes\n"
            "Namespace: tf-lab2-stag\n"
            "\n"
            "Details:\n"
            "• Đối tượng: Deployment/falco-message-format-test\n"
            "• Hành động: Cập nhật\n"
            "• Người dùng: falco-rule-test-user\n"
            "• Kết quả: ✅ Thành công\n"
            "\n"
            "Started: 2026-10-20T03:46:06.837Z",
        )

    def test_secret_list_omits_missing_name_and_prefers_impersonated_user(self):
        event = {
            "rule": "VNPost K8s Human User Read Secret",
            "output_fields": {
                "ka.target.namespace": "falco",
                "ka.target.name": "<NA>",
                "ka.verb": "list",
                "ka.response.code": 200,
                "ka.user.name": "system:serviceaccount:cattle-system:rancher",
                "ka.impuser.name": "user-bhm62",
                "jevt.value[/impersonatedUser/extra/username/0]": "admin-user",
            },
        }
        self.assertEqual(
            format_message(event),
            "🚨 [FIRING: WARNING] Truy cập Secret\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "Severity: WARNING\n"
            "Cluster: Kubernetes\n"
            "Namespace: falco\n"
            "\n"
            "Details:\n"
            "• Hành động: Liệt kê Secret\n"
            "• Người dùng: admin-user\n"
            "• Kết quả: ✅ Thành công",
        )

    def test_port_forward(self):
        event = {
            "rule": "VNPost K8s Human User PortForward Pod",
            "output_fields": {
                "ka.target.namespace": "falco",
                "ka.target.name": "falco-st6wt",
                "ka.response.code": 101,
            },
        }
        self.assertEqual(
            format_message(event),
            "🚨 [FIRING: WARNING] Port-forward Pod\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "Severity: WARNING\n"
            "Cluster: Kubernetes\n"
            "Namespace: falco\n"
            "\n"
            "Details:\n"
            "• Đối tượng: Pod/falco-st6wt\n"
            "• Kết quả: ✅ Thành công",
        )

    def test_rollout_restart_says_request_accepted_not_unknown(self):
        event = {
            "rule": "VNPost K8s Human User Rollout Restart",
            "priority": "Warning",
            "time": "2026-10-20T07:30:17.932172Z",
            "output_fields": {
                "ka.target.namespace": "tf-lab2-stag",
                "ka.target.resource": "deployments",
                "ka.target.name": "frontend",
                "ka.verb": "patch",
                "ka.user.name": "test-user",
            },
        }
        message = format_message(event)
        self.assertIn("Yêu cầu rollout restart", message)
        self.assertIn("Deployment/frontend", message)
        self.assertIn("Yêu cầu đã được API chấp nhận", message)
        self.assertNotIn("Kết quả: Không rõ", message)

    def test_scale_workload_includes_requested_replicas_and_actor(self):
        message = format_message(
            {
                "rule": "VNPost K8s Human User Scale Workload",
                "output_fields": {
                    "ka.target.namespace": "tf-lab2-stag",
                    "ka.target.resource": "deployments",
                    "ka.target.name": "frontend",
                    "ka.verb": "patch",
                    "ka.response.code": 200,
                    "ka.user.name": "test-user",
                    "jevt.value[/requestObject/spec/replicas]": 4,
                },
            }
        )
        self.assertIn("Deployment/frontend", message)
        self.assertIn("Số replica mong muốn: 4", message)
        self.assertIn("Người dùng: test-user", message)

    def test_missing_fields_are_safe(self):
        self.assertEqual(
            format_message({"rule": "Some Rule", "output_fields": {}}),
            "🚨 [FIRING: WARNING] Some Rule\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "Severity: WARNING\n"
            "Cluster: Kubernetes\n"
            "Namespace: không rõ\n"
            "\n"
            "Details:\n"
            "• Kết quả: Không rõ",
        )


if __name__ == "__main__":
    unittest.main()
