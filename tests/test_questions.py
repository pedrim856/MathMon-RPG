import unittest
from data.questions_db import QuestionGenerator
from settings import CHALLENGE_MATH, CHALLENGE_EQUATION, CHALLENGE_MEMORY, CHALLENGE_LOGIC


class TestQuestionGenerator(unittest.TestCase):
    """Unit tests for procedural challenge question generation."""

    def test_math_questions_structure(self):
        """Test math challenge questions across multiple difficulty levels."""
        for diff in range(1, 11):
            q = QuestionGenerator.generate(CHALLENGE_MATH, diff)
            self.assertIn("question", q)
            self.assertIn("answer", q)
            self.assertIn("options", q)
            self.assertEqual(len(q["options"]), 4)
            self.assertIn(str(q["answer"]), q["options"])
            self.assertIn("timer", q)
            self.assertIn("type", q)
            self.assertGreater(q["timer"], 0)

    def test_equation_questions_structure(self):
        """Test equation challenge generation."""
        for diff in range(1, 11):
            q = QuestionGenerator.generate(CHALLENGE_EQUATION, diff)
            self.assertIn("question", q)
            self.assertIn("answer", q)
            self.assertIn("options", q)
            self.assertEqual(len(q["options"]), 4)
            self.assertIn(str(q["answer"]), q["options"])
            self.assertIn("timer", q)
            self.assertTrue(len(str(q["answer"])) > 0)

    def test_memory_questions_structure(self):
        """Test memory sequence challenge generation."""
        for diff in range(1, 11):
            q = QuestionGenerator.generate(CHALLENGE_MEMORY, diff)
            self.assertIn("sequence", q)
            self.assertIn("answer", q)
            self.assertGreaterEqual(len(q["sequence"]), 2)
            self.assertEqual(len(q["sequence"]), len(q["answer"]))

    def test_logic_questions_structure(self):
        """Test logic sequence challenge generation."""
        for diff in range(1, 11):
            q = QuestionGenerator.generate(CHALLENGE_LOGIC, diff)
            self.assertIn("question", q)
            self.assertIn("answer", q)
            self.assertIn("options", q)
            self.assertEqual(len(q["options"]), 4)
            self.assertIn(str(q["answer"]), q["options"])
            self.assertIn("timer", q)
            self.assertTrue(len(str(q["answer"])) > 0)


if __name__ == "__main__":
    unittest.main()
