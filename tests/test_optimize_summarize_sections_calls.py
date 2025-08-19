import unittest
from Sisyphus.helpers import optimize_summarize_sections_calls

class TestOptimizeSummarizeSectionsCalls(unittest.TestCase):
    def test_basic_cases(self):
        print("[TEST]test_basic_cases")
        # Test for no_sections = 7
        result = optimize_summarize_sections_calls(no_sections=7)
        print(result)
        self.assertEqual(sum(result), 7)
        self.assertTrue(all(isinstance(x, int) and x > 0 for x in result))
        # Test for no_sections = 0 (should raise ValueError)
        with self.assertRaises(ValueError):
            optimize_summarize_sections_calls(no_sections=0)
        # Test for no_sections = 1
        result = optimize_summarize_sections_calls(no_sections=1)
        print(result)
        self.assertEqual(sum(result), 1)
        # Test for no_sections = 10
        result = optimize_summarize_sections_calls(no_sections=10)
        print(result)
        self.assertEqual(sum(result), 10)
        # Test for no_sections = 4
        result = optimize_summarize_sections_calls(no_sections=4)
        print(result)
        self.assertEqual(sum(result), 4)

    def test_various_chunk_sizes(self):
        print("[TEST]test_various_chunk_sizes")
        for chunk_size in [1, 2, 3, 4]:
            result = optimize_summarize_sections_calls(no_sections=10, chunk_sz=chunk_size)
            print(result)
            self.assertEqual(sum(result), 10)

    def test_various_inputs(self):
        print("[TEST]test_various_inputs")
        for n in [1, 4, 7, 11, 20]:
            result = optimize_summarize_sections_calls(no_sections=n)
            print(result)
            self.assertEqual(sum(result), n)

if __name__ == "__main__":
    unittest.main()