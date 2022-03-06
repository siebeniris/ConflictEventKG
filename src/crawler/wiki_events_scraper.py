import requests
import time
import random
import os

months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November',
          'December']

headers = {
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'}


def scrape_by_day(year=2022, month="February", start_day=24, end_day=28, output_dir="../data/wikipedia/"):
    for day in range(start_day, end_day+1):
        time.sleep(5 + random.random())
        url = f'https://en.wikipedia.org/wiki/Portal:Current_events/{year}_{month}_{day}'
        response = requests.get(url)
        save_file = os.path.join(output_dir, f"{year}_{month}_{day}.html")
        if response.status_code == 200:
            with open(save_file, "w") as file:
                file.write(response.text)

