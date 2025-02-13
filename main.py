import requests
from bs4 import BeautifulSoup
import random
import pandas as pd
import time


class LinkedInJobScraper:
    def __init__(self, title, location):
        """
        Initialize the scraper with job title and location.
        """
        self.title = title
        self.location = location
        self.start = 0
        self.job_list = []

    def fetch_job_listings(self):
        """
        Scrapes job listings from LinkedIn.
        """
        while True:
            url = (f"https://www.linkedin.com/jobs-guest/jobs/api/"
                   f"seeMoreJobPostings/search?keywords={self.title}&"
                   f"location={self.location}&start={self.start}")
            response = requests.get(url)
            soup = BeautifulSoup(response.text, "html.parser")
            jobs = soup.find_all("li")

            jobs_found = len(jobs)
            self.start += jobs_found
            print(f"Scraped {self.start} jobs so far...")

            if jobs_found == 0:
                print(f"Total jobs scraped: {len(self.job_list)}")
                break

            job_ids = self.extract_job_ids(jobs)
            self.scrape_job_details(job_ids)

    def extract_job_ids(self, jobs):
        """
        Extracts job IDs from job postings.
        """
        job_ids = []
        for job in jobs:
            base_card_div = (job.find("div",
                                     {"class": "base-card"}) or
                             job.find("a", {
                                 "class": "base-card"}))
            if base_card_div:
                job_id = base_card_div.get("data-entity-urn").split(":")[3]
                job_ids.append(job_id)
        return job_ids

    def scrape_job_details(self, job_ids):
        """
        Scrapes job details for each job ID.
        """
        for job_id in job_ids:
            job_url = (f"https://www.linkedin.com/jobs-guest/"
                       f"jobs/api/jobPosting/{job_id}")
            response = requests.get(job_url)
            soup = BeautifulSoup(response.text, "html.parser")

            job_post = {
                "job_title": self.get_text(soup,
                                           "h2",
                                           "top-card-layout__title"),
                "company_name": self.get_text(soup, "a",
                                              "topcard__org-name-link"),
                "time_posted": self.get_text(soup, "span",
                                             "posted-time-ago__text"),
                "num_applicants": self.get_text(soup, "span",
                                                "num-applicants__caption"),
                "JD": self.get_text(soup, "div",
                                    "show-more-less-html__markup")
            }

            self.job_list.append(job_post)
            # Pause to avoid detection
            time.sleep(random.randint(2, 6))

    def get_text(self, soup, tag, class_name):
        """
        Extracts text from HTML elements safely.
        """
        element = soup.find(tag, {"class": class_name})
        return element.text.strip() if element else None

    def get_dataframe(self):
        """
        Returns a pandas DataFrame of scraped jobs.
        """
        return pd.DataFrame(self.job_list)


# Usage
scraper = LinkedInJobScraper("Python Developer", "Kenya")
scraper.fetch_job_listings()
jobs_df = scraper.get_dataframe()
print(jobs_df)
