# Example test for module1
import unittest
from Sisyphus import parsers

class TestCVParser(unittest.TestCase):
    def test_parse_cv_simple(self):
        sample_cv = """
[0]Name: John Doe
[0]Contact Information:
    [1]Address: 123 Main St, City, Country
    [1]Phone: +1234567890
    [1]Email: jd@hotmail.com
    [1]LinkedIn: https://linkedin.com/in/johndoe
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
    [1]Courses: Algorithms, Data Structures, Operating Systems
    [1]Degree: Master of Science in Software Engineering
    [1]University: Example University
    [1]Location: City, Country
    [1]Duration: 2019 - 2021
    [1]Courses: Software Architecture, Cloud Computing, Agile Development
[0]Certifications:
    [1]Certification Name: AWS Certified Solutions Architect
    [1]Issuing Organization: Amazon
    [1]Issue Date: 2022-05
    [1]Certification Name: Google Cloud Professional
    [1]Issuing Organization: Google
    [1]Issue Date: 2023-03
[0]Awards and Scholarships:
    [1]Award Name: Dean's List
    [1]Issuing Organization: University of Example
    [1]Issue Date: 2018
    [1]Award Name: Best Graduate
    [1]Issuing Organization: Example University
    [1]Issue Date: 2021
[0]Volunteering and Leadership:
    [1]Role: Team Lead
    [1]Organization: Open Source Project
    [1]Location: Remote
    [1]Duration: 2020 - 2021
    [1]Description: Led a team of 10 contributors.
    [1]Skills: Technical Skills: Web Development, Cloud Computing; Soft Skills: Leadership, Communication
    [1]Role: Volunteer
    [1]Organization: Local Charity
    [1]Location: City, Country
    [1]Duration: 2019 - 2020
    [1]Description: Organized fundraising events.
    [1]Skills: Technical Skills: Event Planning, Fundraising; Soft Skills: Communication, Teamwork
[0]Work Experience:
    [1]Job Title: Software Developer
    [1]Company: TechCorp
    [1]Location: City, Country
    [1]Duration: 2021 - 2023
    [1]Description: Developed web applications.
    [1]Skills: Programming Languages: Python, JavaScript; Technical Skills: Web Development; Soft Skills: Problem Solving, Communication
    [1]Job Title: Intern
    [1]Company: WebStart
    [1]Location: City, Country
    [1]Duration: 2020 - 2021
    [1]Description: Assisted in software development.
    [1]Skills: Programming Languages: Python; Technical Skills: Testing; Soft Skills: Adaptability
[0]Projects:
    [1]Project Title: Portfolio Website
    [1]Type: Personal
    [1]Duration: 2022
    [1]Description: Built a personal portfolio site.
    [1]Skills: Programming Languages: JavaScript; Technical Skills: Web Design; Soft Skills: Creativity
    [1]Project Title: Inventory System
    [1]Type: Academic
    [1]Duration: 2021
    [1]Description: Developed an inventory management system.
    [1]Skills: Programming Languages: Python; Technical Skills: Database Design; Soft Skills: Analytical Thinking
"""
        expected = {
            'name': 'John Doe',
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
            'languages': ['English', 'Spanish'],
            'education': [
                {
                    'degree': 'Bachelor of Science in Computer Science',
                    'university': 'University of Example',
                    'location': 'City, Country',
                    'duration': '2015 - 2019',
                    'courses': ['Algorithms', 'Data Structures', 'Operating Systems']
                },
                {
                    'degree': 'Master of Science in Software Engineering',
                    'university': 'Example University',
                    'location': 'City, Country',
                    'duration': '2019 - 2021',
                    'courses': ['Software Architecture', 'Cloud Computing', 'Agile Development']
                }
            ],
            'certifications': [
                {
                    'certification_name': 'AWS Certified Solutions Architect',
                    'issuing_organization': 'Amazon',
                    'issue_date': '2022-05'
                },
                {
                    'certification_name': 'Google Cloud Professional',
                    'issuing_organization': 'Google',
                    'issue_date': '2023-03'
                }
            ],
            'awards_and_scholarships': [
                {
                    'award_name': "Dean's List",
                    'issuing_organization': 'University of Example',
                    'issue_date': '2018'
                },
                {
                    'award_name': 'Best Graduate',
                    'issuing_organization': 'Example University',
                    'issue_date': '2021'
                }
            ],
            'volunteering_and_leadership': [
                {
                    'role': 'Team Lead',
                    'organization': 'Open Source Project',
                    'location': 'Remote',
                    'duration': '2020 - 2021',
                    'description': 'Led a team of 10 contributors.',
                    'skills': {
                        'technical_skills': ['Web Development', 'Cloud Computing'],
                        'soft_skills': ['Leadership', 'Communication']
                    }
                },
                {
                    'role': 'Volunteer',
                    'organization': 'Local Charity',
                    'location': 'City, Country',
                    'duration': '2019 - 2020',
                    'description': 'Organized fundraising events.',
                    'skills': {
                        'technical_skills': ['Event Planning', 'Fundraising'],
                        'soft_skills': ['Communication', 'Teamwork']
                    }
                }
            ],
            'work_experience': [
                {
                    'job_title': 'Software Developer',
                    'company': 'TechCorp',
                    'location': 'City, Country',
                    'duration': '2021 - 2023',
                    'description': 'Developed web applications.',
                    'skills': {
                        'programming_languages': ['Python', 'JavaScript'],
                        'technical_skills': ['Web Development'],
                        'soft_skills': ['Problem Solving', 'Communication']
                    }
                },
                {
                    'job_title': 'Intern',
                    'company': 'WebStart',
                    'location': 'City, Country',
                    'duration': '2020 - 2021',
                    'description': 'Assisted in software development.',
                    'skills': {
                        'programming_languages': ['Python'],
                        'technical_skills': ['Testing'],
                        'soft_skills': ['Adaptability']
                    }
                }
            ],
            'projects': [
                {
                    'project_title': 'Portfolio Website',
                    'type': 'Personal',
                    'duration': '2022',
                    'description': 'Built a personal portfolio site.',
                    'skills': {
                        'programming_languages': ['JavaScript'],
                        'technical_skills': ['Web Design'],
                        'soft_skills': ['Creativity']
                    }
                },
                {
                    'project_title': 'Inventory System',
                    'type': 'Academic',
                    'duration': '2021',
                    'description': 'Developed an inventory management system.',
                    'skills': {
                        'programming_languages': ['Python'],
                        'technical_skills': ['Database Design'],
                        'soft_skills': ['Analytical Thinking']
                    }
                }
            ]
        }
        result = parsers.parse_cv(sample_cv)
        self.assertEqual(result['name'], expected['name'])
        self.assertEqual(result['contact_information'], expected['contact_information'])
        self.assertEqual(result['title'], expected['title'])
        self.assertEqual(result['summary'], expected['summary'])
        self.assertEqual(result['languages'], expected['languages'])
        self.assertEqual(result['education'], expected['education'])
        self.assertEqual(result['certifications'], expected['certifications'])
        self.assertEqual(result['awards_and_scholarships'], expected['awards_and_scholarships'])
        self.assertEqual(result['volunteering_and_leadership'], expected['volunteering_and_leadership'])
        self.assertEqual(result['work_experience'], expected['work_experience'])
        self.assertEqual(result['projects'], expected['projects'])

    def test_empty_cv(self):
        sample_cv = ""
        expected = {}
        result = parsers.parse_cv(sample_cv)
        self.assertEqual(result, expected)

    def test_missing_parent_fields(self):
        sample_cv = """
[0]Name: John Doe
[0]Languages: English, Spanish
[0]Education:
    [1]Degree: Bachelor of Science in Computer Science
    [1]University: University of Example
    [1]Location: City, Country
    [1]Duration: 2015 - 2019
    [1]Courses: Algorithms, Data Structures, Operating Systems
"""
        expected = {
            'name': 'John Doe',
            'languages': ['English', 'Spanish'],
            'education': [
                {
                    'degree': 'Bachelor of Science in Computer Science',
                    'university': 'University of Example',
                    'location': 'City, Country',
                    'duration': '2015 - 2019',
                    'courses': ['Algorithms', 'Data Structures', 'Operating Systems']
                }
            ]
        }
        result = parsers.parse_cv(sample_cv)
        self.assertEqual(result, expected)

    def test_missing_subfields(self):
        sample_cv = """
[0]Name: John Doe
[0]Languages: English, Spanish
[0]Contact Information:
    [1]Address: 123 Main St, City, Country
[0]Education:
    [1]Degree: Bachelor of Science in Computer Science
"""
        expected = {
            'name': 'John Doe',
            'languages': ['English', 'Spanish'],
            'contact_information': {
                'address': '123 Main St, City, Country'
            },
            'education': [
                {
                    'degree': 'Bachelor of Science in Computer Science'
                }
            ]
        }
        result = parsers.parse_cv(sample_cv)
        self.assertEqual(result, expected)

    def test_missing_values(self):
        sample_cv = """
[0]Name:
[0]Languages:
[0]Contact Information:
    [1]Address:
[0]Education:
    [1]Degree:
"""
        expected = {
            'name': '',
            'languages': [],
            'contact_information': {
                'address': ''
            },
            'education': [
                {
                    'degree': ''
                }
            ]
        }
        result = parsers.parse_cv(sample_cv)
        self.assertEqual(result, expected)

    def test_extra_parent_fields(self):
        sample_cv = """
[0]Name: John Doe
[0]Languages: English, Spanish
[0]Contact Information:
    [1]Address: 123 Main St, City, Country
[0]Education:
    [1]Degree: Bachelor of Science in Computer Science
    [1]University: University of Example
    [1]Location: City, Country
    [1]Duration: 2015 - 2019
    [1]Courses: Algorithms, Data Structures, Operating Systems
[0]Hobbies: Chess, Painting
"""
        expected = {
            'name': 'John Doe',
            'languages': ['English', 'Spanish'],
            'contact_information': {
                'address': '123 Main St, City, Country'
            },
            'education': [
                {
                    'degree': 'Bachelor of Science in Computer Science',
                    'university': 'University of Example',
                    'location': 'City, Country',
                    'duration': '2015 - 2019',
                    'courses': ['Algorithms', 'Data Structures', 'Operating Systems']
                }
            ]
        }
        result = parsers.parse_cv(sample_cv)
        self.assertEqual(result, expected)

    def run(self, result=None):
        test_name = self._testMethodName
        try:
            super().run(result)
            print(f"Test {test_name}: PASS")
        except Exception:
            print(f"Test {test_name}: FAIL")
            raise

if __name__ == "__main__":
    unittest.main()
