from scraper import scrape_gig, print_gig_pretty, save_gig_to_json

GIG_URL = "https://www.fiverr.com/username/gig-name"


def main():
    gig_data = scrape_gig(GIG_URL)
    print_gig_pretty(gig_data)
    save_gig_to_json(gig_data)


if __name__ == "__main__":
    main()
