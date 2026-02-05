from scraper import scrape_gig

GIG_URL = "https://www.fiverr.com/username/gig-name"


def main():
    gig_data = scrape_gig(GIG_URL)
    print(gig_data)


if __name__ == "__main__":
    main()
