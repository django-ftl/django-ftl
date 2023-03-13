from django_ftl import activate
from django_ftl.bundles import Bundle

from .base import TestBase

ftl_bundle = Bundle(["tests/docs.ftl"])


class TestDocs(TestBase):
    def test_usage_docs(self):
        # These tests parallel the code in the usage.rst docs
        activate("en")
        title = ftl_bundle.format("events-title")
        self.assertEqual(title, "MyApp Events!")

        greeting = ftl_bundle.format(
            "events-greeting", {"username": "boaty mcboatface"}
        )
        self.assertEqual(greeting, "Hello, \u2068boaty mcboatface\u2069")

        zero_events_info = ftl_bundle.format(
            "events-new-events-info", {"count": 0}
        )
        self.assertEqual(zero_events_info, "There have been no new events since your last event.")
        one_event_info = ftl_bundle.format(
            "events-new-events-info", {"count": 1}
        )
        self.assertEqual(one_event_info, "There has been one new event since your last visit.")
        many_event_info = ftl_bundle.format(
            "events-new-events-info", {"count": 2}
        )
        self.assertEqual(
            many_event_info,
            "There have been \u20682\u2069 new events since your last visit."
        )
