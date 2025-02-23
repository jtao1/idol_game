import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import re
import choose_idol as ci
import unicodedata

def get_soup(url: str) -> BeautifulSoup:
    page = requests.get(url)
    return BeautifulSoup(page.content, 'html.parser')


def get_votes(soup: BeautifulSoup, url: str) -> dict:
    votes = {}
    group = soup.find('h1', class_='entry-title h1').text
    group = group[:group.index('Members') - 1]
    print(group)

    result = soup.find('ul', class_='dem-answers')

    vote_results = result.find_all('li')

    for vote in vote_results:
        name = vote.find('div', class_='dem-label').contents[0].strip()
        vote = vote.find('span', class_='dem-votes-txt-votes').text.split()[0].strip()
        votes[name] = int(vote)

    voters = int(soup.find('div', class_='dem-users-voted').text.split()[1].strip())

    return group, votes, voters

def get_ages(soup: BeautifulSoup) -> dict:
    ages = {}
    nationality_dict = {}
    today = datetime.today()
    group = soup.find('h1', class_='entry-title h1').text
    group = group[:group.index('Members') - 1]
    if group == "BLACKPINK":
        nationalities = ["Korean", "Korean", "Australian", "Thai"]
    elif group == "ITZY" or group == "Red Velvet":
        nationalities = ["Korean"] * 5
    elif group == "WOOAH":
        nationalities = ["Korean", "Korean", "Japanese", "Korean", "Korean", "Korean"]
    elif group == "IZONE":
        nationalities = ["Korean", "Japanese", "Korean", "Korean", "Korean", "Korean", "Korean", "Japanese", "Japanese", "Korean", "Korean", "Korean"]
    elif group == "GFRIEND":
        nationalities = ["Korean"] * 6 
    elif group == "OH MY GIRL":
        nationalities = ["Korean"] * 8
    
    else:
        nationalities = soup.find_all('span', string=lambda text: text and text.strip() in ["Nationality:"])
    print(nationalities)

    if group == "IZ*ONE":
        group = "IZONE"
    print(group)

    if group == "tripleS":
        names = soup.find_all('span', string=lambda text: text and text.strip() in ["Birth Name:", "Birth Name (Taiwanese):"])
    else:
        names = soup.find_all('span', string=lambda text: text and text.strip() in ["Stage Name:", "Stage / Birth Name:", "Stage/Korean Name:"])
        outlier = soup.find('span', string=lambda text: text and text == " Name:")
        if outlier:
            names.append(outlier)
        if group == "TWICE":
            names = [span for span in names if not span.find_parent('span')]
    birthdays = soup.find_all('span', string=lambda text: text and text.strip() in ["Birthdate:", "Birthday:"])
    
    print(names)
    for i in range(len(names)):
        real_name = names[i].find_next(string=True).find_next(string=True).strip()
        real_name = real_name.split('(')[0].replace("-", "").strip()
        if len(real_name) > 7:
            real_name = real_name[real_name.find(" ")+1:]
        real_name = real_name.replace(" ", "")
        real_name = ''.join(c for c in unicodedata.normalize('NFKD', real_name) if not unicodedata.combining(c))
        bday = birthdays[i].find_next(string=True).find_next(string=True).strip()
        
        if group in ['BLACKPINK', 'ITZY', 'Red Velvet', 'WOOAH', 'IZONE', 'GFRIEND', 'OH MY GIRL']:
            nationality = nationalities[i]
        else:
            nationality = nationalities[i].find_next(string=True).find_next(string=True).strip()

        print(nationality)
        if i == 3 and group == "NMIXX":
            bday = "December 28th, 2004"
            real_name = "Bae"

        bday = re.sub(r'(\d+)(st|nd|rd|th)', r'\1', bday)
        birthday = datetime.strptime(bday, "%B %d, %Y")
        age = today.year - birthday.year - ((today.month, today.day) < (birthday.month, birthday.day))
        ages[real_name] = age
        nationality_dict[real_name] = nationality

    return group, ages

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
    with open(f'./girl groups/{group}.json', 'w') as f:
        json.dump(votes, f, indent=4)

def get_group_data(age: bool):
    link_types = ['gg']
    for link_type in link_types:
        with open(f'./{link_type}-links.txt', 'r') as links_file:
            url = links_file.readline()
            while url:
                soup = get_soup(url)
                if age:
                    group, ages = get_ages(soup)

                    json_text = {}
                    json_text['group name'] = group
                    json_text['group-type'] = link_type
                    json_text['ages'] = ages
                else:
                    group, votes, voters = get_votes(soup, url)

                    json_text = {}
                    json_text['group name'] = group
                    json_text['group-type'] = link_type
                    json_text['votes'] = votes
                    json_text['voters'] = voters
                write_json(group, json_text)
                url = links_file.readline()


# soup = get_soup('https://kprofiles.com/izone-members-profile/')
# idol_scraper(soup)
get_group_data(True) # True for age, False for votes
# ci.write_all_idols(True, 1, "all female idols.txt")

# stage_name, birth_name, birthdate

 