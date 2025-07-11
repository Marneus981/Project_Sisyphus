import unittest
from Sisyphus.parsers import dict_spliter, dict_grafter

class TestDictSpliterGrafter(unittest.TestCase):
    def setUp(self):
        self.cv_dict = {
            'name': 'John Doe',
            'languages': ['English', 'Spanish'],
            'contact_information': {
                'address': '123 Main St, City, Country',
                'phone': '+1234567890',
                'email': 'jd@hotmail.com',
                'linkedin': 'https://linkedin.com/in/johndoe',
                'github': 'https://github.com/johndoe',
                'portfolio': 'https://johndoe.com'
            },
            'title': 'Software Engineer',
            'summary': 'Experienced software engineer with a passion for developing innovative solutions.',
            'education': [
                {
                    'degree': 'Bachelor of Science in Computer Science',
                    'university': 'University of Example',
                    'location': 'City, Country',
                    'duration': '2015 - 2019',
                    'courses': ['Algorithms', 'Data Structures', 'AI']
                },
                {
                    'degree': 'Master of Science in Software Engineering',
                    'university': 'Example University',
                    'location': 'City, Country',
                    'duration': '2019 - 2021',
                    'courses': ['Software Design', 'ML', 'NLP']
                }
            ]
        }

    def test_spliter_grafter_inverse(self):
        split_dicts = dict_spliter(self.cv_dict)
        grafted_dict = dict_grafter(split_dicts)
        self.assertEqual(self.cv_dict, grafted_dict)

if __name__ == "__main__":
    unittest.main()
