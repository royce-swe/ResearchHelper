# Install PyAlex:
# pip install pyalex

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
    "interests": ["machine learning", "computer engineering"],
    "location": "remote",
    "preferred_universities": ["MIT", "Stanford University", "Harvard University"]
}

# Pre-fetched OpenAlex concept IDs for more precise filtering
concept_ids = [
    "C41008148",  # Machine Learning
    "C127313418"  # Computer Engineering
]

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
                "works_count": ">10",
                "concepts.id": "|".join(concept_ids)
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
                topics = ", ".join([concept["display_name"] for concept in author.get("x_concepts", [])])

                professors.append({
                    "name": name,
                    "email": "N/A",
                    "university": inst_id.split('/')[-1],
                    "research_area": topics if topics else "N/A"
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
    with open("professors_pyalex2.csv", "w", newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["Name", "Email", "University_ID", "Research Area"])
        for prof in all_professors:
            writer.writerow([prof['name'], prof['email'], prof['university'], prof['research_area']])

    print("\n✅ Finished! Results saved to professors_pyalex.csv")
