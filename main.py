import re
import time
import random

import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver


def get_kinopoisk(names, users_score, country, years, genres, url):  # функция для создания датасета с сайта кинопоиск
    reg = re.compile(r"\d{4}")  # регулярное выражение для нахождения года
    # создаю пустые списки чтобы заполнять их информацией из сайта
    names1 = []
    users_score1 = []
    year1 = []
    genre1 = []
    countries1 = []
    # цикл в котором заходим на сайт и берем данные
    for i in range(1, 11):
        time.sleep(random.randint(5, 36))  # делаем рандомный промежуток между страницами
        url = url if i == 1 else "https://www.kinopoisk.ru/lists/top500/?page={}&tab=all".format(i)
        driver = webdriver.Firefox(executable_path='./geckodriver.exe')
        driver.get(url)  # открываем сайт
        result = driver.page_source  # изучаем его
        value = BeautifulSoup(result)  # извлекаем данные
        # находим на сайте  где находятся названия, года, страны, жанры, оценки зрителей
        name = value.find_all(names[0], names[1])
        user_score = value.find_all(users_score[0], users_score[1])
        countries = value.find_all(country[0], country[1])
        year = value.find_all(years[0], years[1])
        genre = value.find_all(genres[0], genres[1])

        # вытаскиваем данные и заполняем их в список
        names1 += [x.contents[0] for x in name]
        users_score1 += [x.contents[0] for x in user_score]
        countries1 += [x.contents[0] for i, x in enumerate(countries) if i % 2 == 0]
        year1 += [re.findall(reg, x.contents[0]) for x in year]
        genre1 += [x.contents[0] for i, x in enumerate(genre) if i % 2]
        driver.close()  # закрываем браузер

    rows = get_rows(names1, users_score1, countries1, year1, genre1)  # создаем словарь
    df = pd.DataFrame(rows)  # создаем датасет
    df.to_csv("kinopoisk_500.csv", mode='a', columns=["name", "user_score", "country", "year", "genre"],
              index=False)  # создаем файл и записываем все туда


def get_imdb(names, users_score, countries, years, genres, url):  # функция для создания датасета с сайта IMDb
    # создаю пустые списки чтобы заполнять их информацией из сайта
    names1 = []
    users_score1 = []
    year1 = []
    genre1 = []
    countries1 = []

    pattern = r'\/title\/tt\d+\/\?ref_=ttls_li_tt'  # регулярное выражение для нахождения названий
    reg = re.compile(r"\d{4}")  # регулярное выражение для нахождения года
    # цикл в котором заходим на сайт и берем данные
    for i in range(1, 6):
        time.sleep(5)
        url = url if i == 1 else "https://www.imdb.com/list/ls062911411/?st_dt=&mode=detail&page={}&ref_=ttls_vm_dtl&sort=list_order,asc".format(
            i)
        driver = webdriver.Firefox(executable_path='./geckodriver.exe')
        driver.get(url)  # открываем сайт
        result = driver.page_source  # изучаем его
        value = BeautifulSoup(result)  # извлекаем данные

        # находим на сайте  где находятся названия
        name = value.find_all(names[0], names[1])
        n = re.findall(pattern, str(name))
        name = []
        for i in range(len(n)):
            name += value.find_all('a', {'href': n[i]})
        # находим на сайте  где находятся  года, страны, жанры, оценки зрителей
        user_score = value.find_all(users_score[0], users_score[1])
        year = value.find_all(years[0], years[1])
        genre = value.find_all(genres[0], genres[1])

        # вытаскиваем данные и заполняем их в список
        names1 += [x.contents[0] for x in name]
        users_score1 += [x.contents[0] for i, x in enumerate(user_score) if i % 23 == 0]
        year1 += [re.findall(reg, x.contents[0]) for x in year]
        genre1 += [x.contents[0].replace('\n', '').replace(' ', '') for x in genre]
        countries1 += [''] * 100  # тк на этом сайте нет стран просто заполняем его пустыми строками
        driver.close()  # закрываем браузер

    rows = get_rows(names1, users_score1, countries1, year1, genre1)  # создаем словарь
    df = pd.DataFrame(rows)  # создаем датасет
    df.to_csv("imdb.csv", mode='a', columns=["name", "user_score", "country", "year", "genre"],
              index=False)  # создаем файл и записываем все туда


def get_rotten(names, users_score, country, years, genres, url):  # функция для создания датасета с сайта rottentomatoes
    # создаю пустые списки чтобы заполнять их информацией из сайта
    names1 = []
    users_score1 = []
    year1 = []
    genre1 = []
    countries1 = []
    reg = re.compile(r"\d{4}")  # регулярное выражение для нахождения года
    # цикл в котором заходим на сайт и берем данные
    for i in range(1, 101):
        time.sleep(5)
        driver = webdriver.Firefox(executable_path='./geckodriver.exe')
        driver.get(url)
        elems = driver.find_elements_by_xpath("//td//a[@class='unstyled articleLink']")  # берем все сслыки с фильмами
        elems[i - 1].click()  # открываем нужный фильм чтобы взять данные
        result = driver.page_source  # изучаем его
        value = BeautifulSoup(result)  # извлекаем данные

        # находим на сайте  где находятся  названия, года, страны, жанры, оценки зрителей
        name = value.find_all(names[0], names[1])
        user_score = driver.execute_script(
            'return document.querySelector("score-board").shadowRoot.querySelector("score-icon-audience").shadowRoot.querySelector("div.wrap span.percentage")')
        countries = value.find_all(country[0], country[1])
        year = value.find_all(years[0], years[1])
        genre = value.find_all(genres[0], genres[1])

        # вытаскиваем данные и заполняем их в список
        names1 += [x.contents[0] for x in name]
        users_score1 += [user_score.text]
        year1 += [re.findall(reg, x.contents[0]) for x in year]
        genre1 += [x.contents[0].replace('\n', '').replace(' ', '') for x in genre]
        countries1 += ['']  # тк на этом сайте нет стран просто заполняем его пустыми строками
        driver.close()  # закрываем браузер

    rows = get_rows(names1, users_score1, countries1, year1, genre1)  # создаем словарь
    df = pd.DataFrame(rows)  # создаем датасет
    df.to_csv("rotten.csv", mode='a', columns=["name", "user_score", "country", "year", "genre"],
              index=False)  # создаем файл и записываем все туда


def get_rows(names, users_score, countries, year, genres):  # функция для созадния словаря
    return {"name": names, "user_score": users_score, "country": countries, "year": year, "genre": genres}


dom_elements = {"kinopoisk": {"names": ('p', {"class": "selection-film-item-meta__name"}),
                              "users_score": ('span', {"class": "rating__value rating__value_positive"}),
                              "country": ('span', {"class": "selection-film-item-meta__meta-additional-item"}),
                              "year": ('p', {"class": "selection-film-item-meta__original-name"}),
                              "genre": ('span', {"class": "selection-film-item-meta__meta-additional-item"})},
                "imdb": {"names": ('h3', {"class": "lister-item-header"}),
                         "users_score": ('span', {"class": "ipl-rating-star__rating"}),
                         "country": ('', {"": ""}),
                         "year": ('span', {"class": "lister-item-year text-muted unbold"}),
                         "genre": ('span', {"class": "genre"})},
                "rottentomatoes": {"names": ('h1', {"class": "scoreboard__title"}),
                                   "users_score": ('div', {"class": "metascore_w user large movie positive"}),
                                   "country": ('', {"": ""}),
                                   "year": ('p', {"class": "scoreboard__info"}),
                                   "genre": ('div', {"class": "meta-value genre"})},
                "metacritic": {"names": ('h1', {"class": "scoreboard__title"}),
                               "users_score": ('span', {"class": "percentage"}),
                               "country": ('span', {"class": "data"}),
                               "year": ('p', {"class": "scoreboard__info"}),
                               "genre": ('div', {"class": "meta-value genre"})}
                }  # словарь с названиями сайтов и тем где находятся данные на сайте
urls = [
    "https://www.imdb.com/list/ls062911411/",
    "https://www.kinopoisk.ru/lists/top500/?tab=all",
    "https://www.rottentomatoes.com/top/bestofrt/",
    "https://www.metacritic.com/browse/movies/score/metascore/all/filtered"
]  # ссылки сайтов

# проходим по циклу для всех ссылок и для каждого сайта создаем датасет
for i in range(len(urls)):
    url = urls[i]
    name_site = urls[i].split('.')
    key = list(dom_elements.keys())
    if key[0] == name_site[1]:
        get_kinopoisk(dom_elements["kinopoisk"]["names"], dom_elements["kinopoisk"]["users_score"],
                      dom_elements["kinopoisk"]["country"], dom_elements["kinopoisk"]["year"],
                      dom_elements["kinopoisk"]["genre"], url)
    elif key[1] == name_site[1]:
        get_imdb(dom_elements["imdb"]["names"], dom_elements["imdb"]["users_score"], dom_elements["imdb"]["country"],
                 dom_elements["imdb"]["year"], dom_elements["imdb"]["genre"], url)
    elif key[2] == name_site:
        get_rotten(dom_elements["rottentomatoes"]["names"], dom_elements["rottentomatoes"]["users_score"],
                   dom_elements["rottentomatoes"]["country"], dom_elements["rottentomatoes"]["year"],
                   dom_elements["rottentomatoes"]["genre"], url)
