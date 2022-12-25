import numpy as np
import pandas as pd
import requests
import datetime

from tqdm.notebook import tqdm
from bs4 import BeautifulSoup


class Parser:

    def __init__(self, data=pd.DataFrame({'time': [], 'title': [], 'link': [], 'source': [], 'processed': []})):
        self.df = data
        self.interfax_url = 'https://www.interfax.ru/news/'
        self.lenta_url = 'https://lenta.ru/'

    def parse_interfax(self, date):

        res = pd.DataFrame({'time': [], 'title': [], 'link': [], 'source': [], 'processed': []})

        def get_right_link(x):
            if 'http' in x:
                return x
            else:
                return 'https://interfax.ru' + x

        for i in range(1, 20):
            response = requests.get(
                self.interfax_url + date + '/all/page_' + str(i))
            soup = BeautifulSoup(response.text, 'lxml')

            items = soup.find(class_='an')

            time_stamps = [date + item.text for item in items.find_all('span')]
            links = [get_right_link(item.get('href'))
                     for item in items.find_all('a')]
            titles = [item.find('h3').get_text().strip()
                      for item in items.find_all('a')]
            if links[0] in self.df['link'].values:
                break

            res = pd.concat([res, pd.DataFrame({'time': time_stamps,
                                                'title': titles, 'link': links, 'source': 'interfax'})])

        res['time'] = pd.to_datetime(res['time'], format='%Y/%m/%d%H:%M')

        return res

    def parse_lenta(self, date):

        res = pd.DataFrame({'time': [], 'title': [], 'link': [], 'source': [], 'processed': []})
        for i in range(1, 30):
            response = requests.get(self.lenta_url + date + '/page/' + str(i))
            soup = BeautifulSoup(response.text, 'lxml')

            items = soup.find_all(class_='archive-page__item _news')

            if len(items) == 0:
                break

            links = [self.lenta_url[:-1] +
                     item.find('a').get('href') for item in items]
            time_stamps = [date + item.find('time').text[:5] for item in items]
            titles = [item.find('h3').text for item in items]

            res = pd.concat([res, pd.DataFrame({'time': time_stamps,
                                                'title': titles, 'link': links, 'source': 'lenta'})])

        res['time'] = pd.to_datetime(res['time'], format='%Y/%m/%d%H:%M')

        return res

    def parse(self, n_days=30, mode='default'):

        if mode == 'update':
            start_date = self.df['time'].max()
            if start_date is np.nan:
                raise ValueError(
                    "Existing database is empty. Use mode='default' to fill it from scratch"
                )
            start_date, end_date = start_date.date(), datetime.date.today()
        else:
            start_date, end_date = datetime.date.today(
            ) - datetime.timedelta(days=n_days), datetime.date.today()

        delta = end_date - start_date
        dates = [str(start_date + datetime.timedelta(days=i))[:4] + '/'
                 + str(start_date + datetime.timedelta(days=i))[5:7] + '/'
                 + str(start_date + datetime.timedelta(days=i))[8:10] for i in range(delta.days + 1)]

        for date in tqdm(dates):
            self.df = pd.concat([self.df, self.parse_interfax(date)])
            self.df = pd.concat([self.df, self.parse_lenta(date)])

        self.df.drop_duplicates(subset='link', inplace=True)
        self.df.sort_values(by='time', inplace=True)
        self.df.reset_index(drop=True, inplace=True)
