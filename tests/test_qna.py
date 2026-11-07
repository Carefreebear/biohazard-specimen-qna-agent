import tempfile
import unittest
from pathlib import Path

from src.qna import SpecimenQACoordinator


class QNATests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.knowledge = Path(self.tmp.name) / "sop.md"
        self.knowledge.write_text(
            "# SOP\n## Temperature control\nKeep the validated container closed and report a temperature alarm.\n"
            "## Spill response\nDo not touch a leaking package. Isolate the area and contact the safety lead.\n",
            encoding="utf-8",
        )

    def tearDown(self):
        self.tmp.cleanup()

    def test_grounded_answer_has_source(self):
        result = SpecimenQACoordinator(self.knowledge).ask("What should I do about a temperature alarm?")
        self.assertIn("Source: Temperature control", result["answer"])

    def test_leak_question_escalates(self):
        result = SpecimenQACoordinator(self.knowledge).ask("The package is leaking. What now?")
        self.assertTrue(result["escalated"])
        self.assertIn("contact your supervisor", result["answer"])


if __name__ == "__main__":
    unittest.main()
