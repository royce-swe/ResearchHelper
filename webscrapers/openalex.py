# Install PyAlex:
# pip install pyalex

import csv
import time
from rapidfuzz import fuzz
from pyalex import Institutions, Authors, Works, config

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
    "preferred_universities": ["Massachusetts Institute of Technology", "Stanford University", "Harvard University"]
}

# Pre-fetched OpenAlex concept IDs for more precise filtering
concept_ids = [
    "C41008148",  # Machine Learning
    "C127313418"  # Computer Engineering
]

MAX_RESULTS_PER_UNI = 10

# Helper to aggregate top research areas with frequency scores
def get_top_concepts(author_id, top_n=3):
    print(f"   ↳ Fetching top concepts for author: {author_id}")
    concept_count = {}
    try:
        works_iter = Works().filter(**{"authorships.author.id": author_id}).select(["concepts"]).paginate(per_page=50)
        for page_num, page in enumerate(works_iter, start=1):
            print(f"     - Processing page {page_num} of works for {author_id}")
            for work in page:
                for concept in work.get("concepts", []):
                    name = concept.get("display_name")
                    if name:
                        concept_count[name] = concept_count.get(name, 0) + 1
            time.sleep(0.3)
    except Exception as e:
        print(f"⚠️ Error fetching works for {author_id}: {e}")

    sorted_concepts = sorted(concept_count.items(), key=lambda x: x[1], reverse=True)
    print(f"   ↳ Found top concepts: {sorted_concepts[:top_n]}")
    return [c[0] for c in sorted_concepts[:top_n]]

# ========== FETCH PROFESSORS USING PyAlex ==========
def fetch_professors(university):
    print(f"🔍 Fetching professors for: {university}")
    professors = []
    try:
        insts = list(Institutions().search(university).get())
        print(f"   🔎 Institutions found: {[i['display_name'] for i in insts]}")
        if not insts:
            print(f"   ⚠️ No institution found for {university}")
            return professors

        inst_id = insts[0]['id']
        print(f"   ✅ Using institution ID: {inst_id}")

        authors_iter = Authors().filter(
            **{
                "last_known_institutions.id": inst_id,
                "works_count": ">10"
            }
        ).select(["id", "display_name", "x_concepts", "last_known_institutions", "works_count", "updated_date"]).paginate(per_page=100)

        for page_num, page in enumerate(authors_iter, start=1):
            print(f"   📄 Processing page {page_num}")
            for author in page:
                if len(professors) >= MAX_RESULTS_PER_UNI:
                    print(f"   ⏹️ Reached max of {MAX_RESULTS_PER_UNI} professors for {university}")
                    return professors

                author_name = author.get("display_name", "Unknown")
                print(f"     👤 Evaluating author: {author_name}")
                
                institutions = [inst.get('id', '') for inst in author.get('last_known_institutions', [])]
                if inst_id not in institutions:
                    print(f"       ❌ Skipping (different institution)")
                    continue
                updated_date = author.get("updated_date", "")
                if updated_date and updated_date < "2010-01-01":
                    print(f"       ⏭ Skipping outdated author")
                    continue

                author_id = author.get("id", "")
                top_concepts = get_top_concepts(author_id)

                if any(any(interest.lower() in c.lower() for interest in student['interests']) for c in top_concepts):
                    professors.append({
                        "name": author_name,
                        "email": "N/A",
                        "university": inst_id.split('/')[-1],
                        "research_area": ", ".join(top_concepts) if top_concepts else "N/A"
                    })
                    print(f"       ✅ Added {author_name}")
                else:
                    print(f"       🚫 No relevant research area found")
            time.sleep(0.5)
    except Exception as e:
        print(f"⚠️ Error fetching professors for {university}: {e}")
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
    with open("professors_pyalex.csv", "w", newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["Name", "Email", "University_ID", "Research Area"])
        for prof in all_professors:
            writer.writerow([prof['name'], prof['email'], prof['university'], prof['research_area']])

    print("\n✅ Finished! Results saved to professors_pyalex.csv")