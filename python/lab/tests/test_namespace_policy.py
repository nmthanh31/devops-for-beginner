import unittest

from app.falco_router.namespace_api import should_filter_namespace


class NamespacePolicyTests(unittest.TestCase):
    def test_namespace_without_labels_is_allowed(self):
        self.assertFalse(should_filter_namespace("tf-lab2-stag", None))

    def test_namespace_is_filtered_only_when_explicitly_disabled(self):
        self.assertTrue(
            should_filter_namespace(
                "tf-lab2-stag", {"security.falco.io/alerts": "disabled"}
            )
        )
        self.assertFalse(
            should_filter_namespace(
                "tf-lab2-stag", {"security.falco.io/alerts": "enabled"}
            )
        )

    def test_explicit_denylist_filters_namespace(self):
        self.assertTrue(
            should_filter_namespace("noise-ns", {}, {"noise-ns"})
        )


if __name__ == "__main__":
    unittest.main()
