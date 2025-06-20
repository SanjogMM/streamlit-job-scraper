import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd

st.set_page_config(page_title="Job Scraper", layout="wide")

st.title("🔍 Telecom Job Scraper (Ribbon SBC | SIP | Teams DR/OC)")

# Inputs
keywords = st.text_input("Search Keywords", value="Ribbon SBC, SIP, MS Teams Direct Routing, Operator Connect")
location = st.text_input("Location (e.g., Remote or Pune)", value="Remote")
min_exp = st.slider("Minimum Experience (Years)", 0, 20, 10)

headers = {"User-Agent": "Mozilla/5.0"}

def safe_request(url):
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            return response
        else:
            return None
    except Exception as e:
        return None

def scrape_indeed(keywords, location):
    search = "+".join(keywords.split(","))
    url = f"https://www.indeed.com/jobs?q={search}&l={location}&fromage=7"
    r = safe_request(url)
    if not r: return []
    soup = BeautifulSoup(r.content, "html.parser")
    job_cards = soup.find_all("a", class_="tapItem")
    jobs = []
    for card in job_cards[:10]:
        try:
            title = card.find("h2").text.strip()
            company = card.find("span", class_="companyName").text.strip()
            summary = card.find("div", class_="job-snippet").text.strip()
            link = "https://www.indeed.com" + card.get("href")
            jobs.append({"Title": title, "Company": company, "Summary": summary, "Link": link, "Source": "Indeed"})
        except:
            continue
    return jobs

def scrape_naukri(keywords, location):
    search = "-".join(keywords.lower().replace(",", "").split())
    url = f"https://www.naukri.com/{search}-jobs-in-{location.lower()}"
    r = safe_request(url)
    if not r: return []
    soup = BeautifulSoup(r.content, "html.parser")
    cards = soup.find_all("article", class_="jobTuple")
    jobs = []
    for card in cards[:10]:
        try:
            title = card.find("a", class_="title").text.strip()
            company = card.find("a", class_="subTitle").text.strip()
            link = card.find("a", class_="title").get("href")
            summary = card.find("li", class_="job-snippet").text.strip() if card.find("li", class_="job-snippet") else "No details"
            jobs.append({"Title": title, "Company": company, "Summary": summary, "Link": link, "Source": "Naukri"})
        except:
            continue
    return jobs

def scrape_foundit(keywords, location):
    query = "-".join(keywords.lower().replace(",", "").split())
    url = f"https://www.foundit.in/srp/results?query={query}&locations={location}&experience=10"
    r = safe_request(url)
    if not r: return []
    soup = BeautifulSoup(r.content, "html.parser")
    jobs = []
    cards = soup.find_all("div", class_="srp-jobtuple-wrapper")
    for card in cards[:10]:
        try:
            title_tag = card.find("h3")
            company_tag = card.find("span", class_="company-name")
            link_tag = card.find("a", href=True)
            if title_tag and link_tag:
                title = title_tag.text.strip()
                link = "https://www.foundit.in" + link_tag["href"]
                company = company_tag.text.strip() if company_tag else "N/A"
                summary = "No summary available"
                jobs.append({"Title": title, "Company": company, "Summary": summary, "Link": link, "Source": "FoundIt"})
        except:
            continue
    return jobs

def scrape_shine(keywords, location):
    query = "+".join(keywords.lower().replace(",", "").split())
    url = f"https://www.shine.com/job-search/{query}-jobs-in-{location.lower()}"
    r = safe_request(url)
    if not r: return []
    soup = BeautifulSoup(r.content, "html.parser")
    jobs = []
    cards = soup.find_all("li", class_="w-100")
    for card in cards[:10]:
        try:
            title_tag = card.find("a")
            if title_tag:
                title = title_tag.text.strip()
                link = "https://www.shine.com" + title_tag["href"]
                company = "Shine listing"
                summary = "No summary available"
                jobs.append({"Title": title, "Company": company, "Summary": summary, "Link": link, "Source": "Shine"})
        except:
            continue
    return jobs

def scrape_linkedin(keywords, location):
    search_url = f"https://www.linkedin.com/jobs/search/?keywords={keywords}&location={location}&f_E=4&f_TPR=r2592000"
    return [{
        "Title": "Senior Voice Engineer - Ribbon SBC & MS Teams",
        "Company": "Confidential (LinkedIn)",
        "Summary": "Focus on Ribbon SBC, SIP, Teams Direct Routing and Operator Connect. 10+ years experience.",
        "Link": search_url,
        "Source": "LinkedIn (Manual Entry)"
    }]

def scrape_reed(keywords, location):
    query = "-".join(keywords.lower().replace(",", "").split())
    loc = location.lower().replace(" ", "-")
    url = f"https://www.reed.co.uk/jobs/{query}-jobs-in-{loc}"
    r = safe_request(url)
    if not r: return []
    soup = BeautifulSoup(r.content, "html.parser")
    jobs = []
    cards = soup.find_all("article", class_="job-result")
    for card in cards[:10]:
        try:
            title_tag = card.find("h3")
            company_tag = card.find("a", class_="gtmJobListingPostedBy")
            link_tag = title_tag.find("a") if title_tag else None
            if title_tag and link_tag:
                title = title_tag.text.strip()
                link = "https://www.reed.co.uk" + link_tag["href"]
                company = company_tag.text.strip() if company_tag else "N/A"
                summary = "No summary available"
                jobs.append({"Title": title, "Company": company, "Summary": summary, "Link": link, "Source": "Reed"})
        except:
            continue
    return jobs

if st.button("🔎 Search Jobs"):
    with st.spinner("Scraping job boards..."):
        indeed_jobs = scrape_indeed(keywords, location)
        naukri_jobs = scrape_naukri(keywords, location)
        foundit_jobs = scrape_foundit(keywords, location)
        shine_jobs = scrape_shine(keywords, location)
        linkedin_jobs = scrape_linkedin(keywords, location)
        reed_jobs = scrape_reed(keywords, location)

        all_jobs = indeed_jobs + naukri_jobs + foundit_jobs + shine_jobs + linkedin_jobs + reed_jobs
        df = pd.DataFrame(all_jobs)
        st.success(f"Found {len(df)} jobs.")
        st.dataframe(df, use_container_width=True)

        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📅 Download CSV", data=csv, file_name="jobs.csv", mime="text/csv")
