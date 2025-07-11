# Example test for module1
import unittest
from Sisyphus import cvParser

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
[0]Education:
    [1]Degree: Bachelor of Science in Computer Science
    [1]University: University of Example
    [1]Location: City, Country
    [1]Duration: 2015 - 2019
    [1]Degree: Master of Science in Software Engineering
    [1]University: Example University
    [1]Location: City, Country
    [1]Duration: 2019 - 2021
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
    [1]Role: Volunteer
    [1]Organization: Local Charity
    [1]Location: City, Country
    [1]Duration: 2019 - 2020
    [1]Description: Organized fundraising events.
[0]Work Experience:
    [1]Job Title: Software Developer
    [1]Company: TechCorp
    [1]Location: City, Country
    [1]Duration: 2021 - 2023
    [1]Description: Developed web applications.
    [1]Job Title: Intern
    [1]Company: WebStart
    [1]Location: City, Country
    [1]Duration: 2020 - 2021
    [1]Description: Assisted in software development.
[0]Projects:
    [1]Project Title: Portfolio Website
    [1]Type: Personal
    [1]Duration: 2022
    [1]Description: Built a personal portfolio site.
    [1]Project Title: Inventory System
    [1]Type: Academic
    [1]Duration: 2021
    [1]Description: Developed an inventory management system.
[0]Skills:
    [1]Languages: English, Spanish
    [1]Programming Languages: Python, JavaScript
    [1]Technical Skills: Web Development, Cloud Computing
    [1]Soft Skills: Leadership, Communication
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
            'education': [
                {
                    'degree': 'Bachelor of Science in Computer Science',
                    'university': 'University of Example',
                    'location': 'City, Country',
                    'duration': '2015 - 2019'
                },
                {
                    'degree': 'Master of Science in Software Engineering',
                    'university': 'Example University',
                    'location': 'City, Country',
                    'duration': '2019 - 2021'
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
                    'description': 'Led a team of 10 contributors.'
                },
                {
                    'role': 'Volunteer',
                    'organization': 'Local Charity',
                    'location': 'City, Country',
                    'duration': '2019 - 2020',
                    'description': 'Organized fundraising events.'
                }
            ],
            'work_experience': [
                {
                    'job_title': 'Software Developer',
                    'company': 'TechCorp',
                    'location': 'City, Country',
                    'duration': '2021 - 2023',
                    'description': 'Developed web applications.'
                },
                {
                    'job_title': 'Intern',
                    'company': 'WebStart',
                    'location': 'City, Country',
                    'duration': '2020 - 2021',
                    'description': 'Assisted in software development.'
                }
            ],
            'projects': [
                {
                    'project_title': 'Portfolio Website',
                    'type': 'Personal',
                    'duration': '2022',
                    'description': 'Built a personal portfolio site.'
                },
                {
                    'project_title': 'Inventory System',
                    'type': 'Academic',
                    'duration': '2021',
                    'description': 'Developed an inventory management system.'
                }
            ],
            'skills': {
                'languages': 'English, Spanish',
                'programming_languages': 'Python, JavaScript',
                'technical_skills': 'Web Development, Cloud Computing',
                'soft_skills': 'Leadership, Communication'
            }
        }
        result = cvParser.parse_cv(sample_cv)
        self.assertEqual(result['name'], expected['name'])
        self.assertEqual(result['contact_information'], expected['contact_information'])
        self.assertEqual(result['title'], expected['title'])
        self.assertEqual(result['summary'], expected['summary'])
        self.assertEqual(result['education'], expected['education'])
        self.assertEqual(result['certifications'], expected['certifications'])
        self.assertEqual(result['awards_and_scholarships'], expected['awards_and_scholarships'])
        self.assertEqual(result['volunteering_and_leadership'], expected['volunteering_and_leadership'])
        self.assertEqual(result['work_experience'], expected['work_experience'])
        self.assertEqual(result['projects'], expected['projects'])
        self.assertEqual(result['skills'], expected['skills'])

if __name__ == "__main__":
    unittest.main()
