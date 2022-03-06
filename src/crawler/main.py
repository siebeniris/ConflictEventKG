
from wiki_events_scraper import scrape_by_day
import csv

wikipedia_dir = "/Users/yiyichen/Documents/experiments/eventKB/data/wikipedia"
# scrape_by_day(year=2022, month="February", start_day=24, end_day=28, output_dir=wikipedia_dir)
# scrape_by_day(year=2022, month="March", start_day=1, end_day=3, output_dir=wikipedia_dir)

scrape_by_day(year=2022, month="March", start_day=4, end_day=4, output_dir=wikipedia_dir)

