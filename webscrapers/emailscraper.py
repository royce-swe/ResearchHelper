# import requests
# from bs4 import BeautifulSoup
# import openai
# import re
# import time
# import csv
# from rapidfuzz import fuzz

# # ========== CONFIGURATION ==========
# openai.api_key = "your-openai-api-key"
# semantic_scholar_url = "https://api.semanticscholar.org/graph/v1/author/search"
# semantic_scholar_papers = "https://api.semanticscholar.org/graph/v1/author/{author_id}/papers?limit=1"

# student = {
#     "name": "Royce Mathis",
#     "grade": "Junior",
#     "program": "IB",
#     "interests": ["machine learning", "computer engineering"],
#     "skills": ["Python", "Java", "data analysis"],
#     "github": "https://github.com/royce-swe",
#     "location": "remote",
#     "preferred_universities": ["MIT", "Stanford", "Harvard"]
# }

# department_pages = {
#     "MIT": "https://www.eecs.mit.edu/people/faculty-advisors/",
#     "Stanford": "https://cs.stanford.edu/directory/faculty",
#     "Harvard": "https://www.seas.harvard.edu/computer-science/people/faculty"
# }

# headers = {
#     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0 Safari/537.36"
# }


# # ========== SCRAPING PROFESSORS ==========
# def scrape_professors(university_url):
#     try:
#         response = requests.get(university_url, headers=headers, timeout=10)
#         soup = BeautifulSoup(response.text, 'html.parser')
#         professors = []

#         for tag in soup.find_all(['a', 'p', 'li', 'div'], string=True):
#             email_match = re.search(r"[\w\.-]+@[\w\.-]+", tag.get_text())
#             name_match = re.search(r"(Professor|Dr\.?)\s+[A-Z][a-zA-Z]+\s+[A-Z][a-zA-Z]+", tag.get_text())
#             if email_match and name_match:
#                 professors.append({
#                     "name": name_match.group(),
#                     "email": email_match.group(),
#                     "university": university_url,
#                     "profile_url": tag['href'] if tag.name == 'a' and tag['href'].startswith('http') else "",
#                     "research_area": "",
#                     "recent_paper": "",
#                     "paper_summary": ""
#                 })
#         return professors
#     except Exception as e:
#         print(f"Error scraping {university_url}: {e}")
#         return []


# # ========== SEMANTIC SCHOLAR FETCH ==========
# def fetch_professor_research(name):
#     try:
#         params = {"query": name, "fields": "name,papers"}
#         res = requests.get(semantic_scholar_url, params=params, timeout=5).json()
#         if "data" not in res or not res["data"]:
#             return "", "", ""

#         author_id = res["data"][0]["authorId"]
#         paper_res = requests.get(semantic_scholar_papers.format(author_id=author_id), timeout=5).json()
#         if "data" not in paper_res or not paper_res["data"]:
#             return "", "", ""

#         paper = paper_res["data"][0]
#         title = paper.get("title", "")
#         abstract = paper.get("abstract", "")
#         topics = ", ".join([t["topic"] for t in paper.get("topics", [])]) if paper.get("topics") else ""

#         return topics or "Computer Science", title, abstract[:300]  # trim abstract
#     except:
#         return "", "", ""


# # ========== AI EMAIL GENERATOR ==========
# def generate_email(student, professor):
#     prompt = f"""
#     You are an AI assistant that writes personalized research outreach emails for high school students.

#     Student Info:
#     Name: {student['name']}
#     Grade: {student['grade']}
#     Program: {student['program']}
#     Interests: {', '.join(student['interests'])}
#     Skills: {', '.join(student['skills'])}
#     GitHub: {student['github']}

#     Professor Info:
#     Name: {professor['name']}
#     Email: {professor['email']}
#     University: {professor['university']}
#     Research Area: {professor['research_area']}
#     Recent Paper: {professor['recent_paper']}
#     Paper Summary: {professor['paper_summary']}

#     Write a concise, professional outreach email (≤3 short paragraphs), tailored to this professor's research.
#     """

#     response = openai.ChatCompletion.create(
#         model="gpt-4o",
#         messages=[
#             {"role": "system", "content": "You write polite, tailored, professional outreach emails."},
#             {"role": "user", "content": prompt}
#         ]
#     )
#     return response["choices"][0]["message"]["content"].strip()


# # ========== MAIN SCRIPT ==========
# if __name__ == "__main__":
#     all_professors = []
#     seen_emails = set()

#     for uni in student['preferred_universities']:
#         url = department_pages.get(uni)
#         if url:
#             scraped = scrape_professors(url)
#             for prof in scraped:
#                 if prof["email"] in seen_emails:
#                     continue
#                 seen_emails.add(prof["email"])

#                 # Fetch research data
#                 topics, title, summary = fetch_professor_research(prof['name'])
#                 prof['research_area'] = topics
#                 prof['recent_paper'] = title
#                 prof['paper_summary'] = summary

#                 # Filter based on interests
#                 if any(fuzz.partial_ratio(i.lower(), (topics or "").lower()) > 50 for i in student["interests"]):
#                     all_professors.append(prof)
#                 time.sleep(1)

#     # Write results to CSV
#     with open("professors_output.csv", "w", newline='', encoding='utf-8') as f:
#         writer = csv.writer(f)
#         writer.writerow(["Name", "Email", "University", "Research Area", "Recent Paper", "Generated Email"])
#         for prof in all_professors:
#             email_text = generate_email(student, prof)
#             writer.writerow([prof['name'], prof['email'], prof['university'], prof['research_area'], prof['recent_paper'], email_text])
#             print(f"✅ Generated email for {prof['name']}")

#     print("🎉 Finished! Results saved to professors_output.csv")


# Install PyAlex:
# pip install pyalex rapidfuzz

import csv
import time
from rapidfuzz import fuzz
from pyalex import Institutions, Authors, config

# Set your contact email for polite API usage
config.email = "jalenmathis7@gmail.com"
config.max_retries = 3
config.retry_backoff_factor = 0.1
config.retry_http_codes = [429, 500, 503]

# ========== CONFIGURATION ==========
student = {
    "name": "Royce Mathis",
    "grade": "Junior",
    "program": "IB",
    "interests": ["machine learning", "computer engineering"],  # plain text interests
    "location": "remote",
    "preferred_universities": ["MIT", "Stanford University", "Harvard University"]
}

FUZZY_MATCH_THRESHOLD = 70  # Adjust if needed (higher = stricter match)

# ========== FETCH PROFESSORS USING PyAlex ==========
def fetch_professors(university, max_results=300):
    professors = []
    try:
        insts = list(Institutions().search(university).get())
        if not insts:
            print(f"No institution found for {university}")
            return professors
        inst_id = insts[0]['id']
        print(f"Found institution ID for {university}: {inst_id}")

        authors_iter = Authors().filter(
            **{
                "last_known_institutions.id": inst_id,
                "works_count": ">10"
            }
        ).select(["id", "display_name", "x_concepts", "last_known_institutions", "works_count", "updated_date"]).paginate(per_page=200)

        for page in authors_iter:
            for author in page:
                if len(professors) >= max_results:
                    print(f"Reached max of {max_results} professors for {university}")
                    return professors

                institutions = [inst.get('id', '') for inst in author.get('last_known_institutions', [])]
                if inst_id not in institutions:
                    continue

                updated_date = author.get("updated_date", "")
                if updated_date and updated_date < "2010-01-01":
                    continue

                name = author.get("display_name", "")
                topics = [concept["display_name"] for concept in author.get("x_concepts", [])]
                topic_string = ", ".join(topics)

                # ✅ Fuzzy keyword matching
                if any(fuzz.partial_ratio(interest.lower(), topic.lower()) >= FUZZY_MATCH_THRESHOLD
                       for interest in student['interests'] for topic in topics):
                    professors.append({
                        "name": name,
                        "email": "N/A",
                        "university": inst_id.split('/')[-1],
                        "research_area": topic_string if topic_string else "N/A"
                    })
            time.sleep(0.5)
    except Exception as e:
        print(f"Error fetching professors for {university}: {e}")
    return professors

# ========== MAIN SCRIPT ==========
if __name__ == "__main__":
    all_professors = []
    seen_names = set()

    for uni in student['preferred_universities']:
        print(f"\n🔎 Searching professors for {uni}...")
        results = fetch_professors(uni)
        for prof in results:
            if prof['name'] not in seen_names:
                seen_names.add(prof['name'])
                all_professors.append(prof)

    # Write results to CSV (name, email, university, research topics)
    with open("professors_pyalex_fuzzy.csv", "w", newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["Name", "Email", "University_ID", "Research Area"])
        for prof in all_professors:
            writer.writerow([prof['name'], prof['email'], prof['university'], prof['research_area']])

    print("\n✅ Finished! Results saved to professors_pyalex_fuzzy.csv")
