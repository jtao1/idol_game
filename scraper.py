import requests
from bs4 import BeautifulSoup
import json


def get_soup(url: str) -> BeautifulSoup:
    page = requests.get(url)
    return BeautifulSoup(page.content, 'html.parser')


def get_votes(soup: BeautifulSoup, url: str) -> dict:
    res = {}
    group = soup.find('h1', class_='entry-title h1').text
    group = group[:group.index('Members') - 1]

    result = soup.find('ul', class_='dem-answers')

    votes = result.find_all('li')

    for vote in votes:
        name = vote.find('div', class_='dem-label').contents[0].strip()
        vote = vote.find('span', class_='dem-votes-txt-votes').text.split()[0].strip()
        res[name] = int(vote)

    voters = int(soup.find('div', class_='dem-users-voted').text.split()[1].strip())

    return group, res, voters

def idol_scraper(soup: BeautifulSoup):
    div = soup.find('div', class_='entry-content herald-entry-content')
    paras = div.find_all('p')
    paras = [p for p in paras if p.find('strong')]
    paras_text = [p.text for p in paras if p in paras] #grabs the text
    for p in paras_text:
        if 'birthdate' in p.lower():
            split_p = p.split('\n')
            for text in split_p:
                lowered_text = text.lower()
                if 'stage name' in lowered_text:
                    stage_name_split = text.split('(')
                    stage_name = stage_name_split[0].split(':')[1].strip()
                    stage_name_kr = stage_name_split[1][: len(stage_name_split[1]) - 2].strip()
                    print(stage_name)
                    print(stage_name_kr)
                if 'birth name' in lowered_text:
                    birth_name_split = text.split('(')
                    birth_name = birth_name_split[0].split(':')[1].strip()
                    birth_name_kr = birth_name_split[1][: len(birth_name_split[1]) - 2].strip()
                    print(birth_name)
                    print(birth_name_kr)
                if 'birthdate' in lowered_text:
                    print(text)

def write_json(group, votes: dict) -> None:
    if (group == "IZ*ONE"):
        group = "IZONE"
    with open(f'./groups/{group}.json', 'w') as f:
        json.dump(votes, f, indent=4)


def get_group_data():
    link_types = ['gg']
    for link_type in link_types:
        with open(f'./{link_type}-links.txt', 'r') as links_file:
            url = links_file.readline()
            while url:
                soup = get_soup(url)
                group, votes, voters = get_votes(soup, url)
                print(group)

                json_text = {}
                json_text['name'] = group
                json_text['group-type'] = link_type
                json_text['votes'] = votes
                json_text['voters'] = voters
                write_json(group, json_text)
                url = links_file.readline()


# soup = get_soup('https://kprofiles.com/izone-members-profile/')
# idol_scraper(soup)
get_group_data()

# stage_name, birth_name, birthdate

