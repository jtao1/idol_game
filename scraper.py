import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import re
import unicodedata
import os

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
    nations = {}
    today = datetime.today()
    group = soup.find('h1', class_='entry-title h1').text
    group = group[:group.index('Members') - 1]
    group = group.replace('*', '')

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
    elif group == "OH MY GIRL" or group == "cignature":
        nationalities = ["Korean"] * 8
    elif group == "Weeekly":
        nationalities = ["Korean"] * 7
    else:
        nationalities = soup.find_all('span', string=lambda text: text and text.strip() in ["Nationality:"])

    print(group + "-------")

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
    print(f'names: {len(names)}')
    print(f'nationalities: {len(nationalities)}')
    for i in range(len(names)):
        real_name = names[i].find_next(string=True).find_next(string=True).strip()
        real_name = real_name.split('(')[0].replace("-", "").strip()
        if len(real_name) > 7:
            real_name = real_name[real_name.find(" ")+1:]
        real_name = real_name.replace(" ", "")
        real_name = ''.join(c for c in unicodedata.normalize('NFKD', real_name) if not unicodedata.combining(c))
        bday = birthdays[i].find_next(string=True).find_next(string=True).strip()
        if group in ['BLACKPINK', 'ITZY', 'Red Velvet', 'WOOAH', 'IZONE', 'GFRIEND', 'OH MY GIRL', 'cignature', 'Weeekly']:
            nationality = nationalities[i]
        else:
            nationality = nationalities[i].find_next(string=True).find_next(string=True).strip()

        if "Japanese" in nationality:
            nationality = "Japanese"
        elif "American" in nationality or "Australian" in nationality:
            nationality = "English"
        # elif "Chinese" in nationality or "Taiwanese" in nationality or "Hongkongese" in nationality:
        #     nationality = "CHN"
        # elif "Thai" in nationality or "Filipina" in nationality:
        #     nationality = "THA"
        # else:
        #     nationality = "KOR"
        if i == 5 and group == "cignature":
            real_name = "Hyeonju"

        if i == 3 and group == "NMIXX":
            bday = "December 28th, 2004"
            real_name = "Bae"
        if group == "tripleS":
            if i == 23:
                real_name = "SeoAh"
            if i == 3:
                real_name = "NakYoung"

        bday = re.sub(r'(\d+)(st|nd|rd|th)', r'\1', bday)
        birthday = datetime.strptime(bday, "%B %d, %Y")
        age = today.year - birthday.year - ((today.month, today.day) < (birthday.month, birthday.day))
        real_name = real_name.replace("\u2019", "")
        ages[real_name] = age
        nations[real_name] = nationality

    return group, ages, nations

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

def write_json(group: str, votes: dict) -> None:
    with open(f'./girl groups/{group.upper()}.json', 'w') as f:
        json.dump(votes, f, indent=4)

def get_group_data(votes: bool):
    link_types = ['gg']
    for link_type in link_types:
        with open(f'./{link_type}-links.txt', 'r') as links_file:
            url = links_file.readline()
            while url:
                soup = get_soup(url)
                if not votes:
                    group, ages, nations = get_ages(soup)

                    file_name = f'./girl groups/{group.upper()}.json' # get ratings if already existing
                    exist = {"members": []}
                    if os.path.exists(file_name):
                        with open(file_name, "r") as f:
                            exist = json.load(f)
                    ratings = {member["name"]: member["rating"] for member in exist["members"]}
                    stats = {member["name"]: member["stats"] for member in exist["members"]}

                    json_text = {
                        "group": {
                            "name": group,
                            "type": link_type
                        },
                        "members": []
                    }
                    for name in ages.keys():
                        member = {
                            "name": name,
                            "age": ages.get(name, None),
                            "country": nations.get(name, None),
                            "rating": ratings.get(name, 3),
                            "stats": {
                                "games": stats.get(name, {}).get("games", 0), # total games idol appeared in
                                "wins": stats.get(name, {}).get("wins", 0), # total wins idol has achieved
                                "reroll": stats.get(name, {}).get("reroll", 0), # total times idol was rerolled, upgraded, replaced, or deluxe rerolled
                                "opp reroll": stats.get(name, {}).get("opp reroll", 0), # total times idol was opponent rerolled
                                "opp chances": stats.get(name, {}).get("opp chances", 0), # total chances for opponent to reroll
                                "gr": stats.get(name, {}).get("gr", 0), # total times group rerolled
                                "times bought": stats.get(name, {}).get("times bought", 0), # total times idol was bought
                                "money spent": stats.get(name, {}).get("money spent", 0) # total amount of money spent on idol
                            }
                        }
                        json_text["members"].append(member)
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
get_group_data(False) # True for votes, false for regular
# ci.write_all_idols(True, 1, "all female idols.txt")

# stage_name, birth_name, birthdate

 