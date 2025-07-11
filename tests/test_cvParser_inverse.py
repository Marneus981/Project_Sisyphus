import unittest
from Sisyphus.parsers import parse_cv, inv_parse_cv

class TestCVParserInverse(unittest.TestCase):
    def setUp(self):
        self.cv_text = '''[0]Name: John Doe
[0]Contact Information:
[1]Address: 123 Main St, City, Country
[1]Phone: +1234567890
[1]Email: jd@hotmail.com
[1]Linkedin: https://linkedin.com/in/johndoe
[1]Github: https://github.com/johndoe
[1]Portfolio: https://johndoe.com
[0]Title: Software Engineer
[0]Summary: Experienced software engineer with a passion for developing innovative solutions.
[0]Languages: English, Spanish
[0]Education:
[1]Degree: Bachelor of Science in Computer Science
[1]University: University of Example
[1]Location: City, Country
[1]Duration: 2015 - 2019
[1]Courses: Algorithms, Data Structures, AI
[1]Degree: Master of Science in Software Engineering
[1]University: Example University
[1]Location: City, Country
[1]Duration: 2019 - 2021
[1]Courses: Software Design, ML, NLP
[0]Skills:
[1]Programming Languages: Python, Java
[1]Technical Skills: Docker, Git
[1]Soft Skills: Communication, Teamwork'''

    def test_inverse_operations(self):
        # Parse the CV text to dict
        cv_dict = parse_cv(self.cv_text)
        # Convert dict back to text
        regenerated_text = inv_parse_cv(cv_dict)
        # Parse again
        cv_dict2 = parse_cv(regenerated_text)
        # Show full diff if test fails
        self.maxDiff = None
        try:
            self.assertEqual(cv_dict, cv_dict2)
        except AssertionError:
            import pprint
            print("\n--- Original Dict ---")
            pprint.pprint(cv_dict)
            print("\n--- Regenerated Dict ---")
            pprint.pprint(cv_dict2)
            raise

if __name__ == "__main__":
    unittest.main()
