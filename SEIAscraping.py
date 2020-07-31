from bs4 import BeautifulSoup
import requests
import csv

lst2 = [
    'Arizona',
    'Florida',
    'Illinois',
    'Iowa',
    'Kentucky',
    'Nebraska',
    'Ohio',
    'Oklahoma',
    'Missouri',
    'Massachusetts',
    'New-Jersey',
    'California',
    'Nevada',
    'Washington',
    'Colorado',
    'Hawaii',
    'North-Carolina',
    'Pennsylvania',
    'Texas',
    'New-Mexico',
    'Delaware',
    'Oregon',
    'Vermont',
    'New-York',
    'Maryland',
    'Utah',
    'Georgia',
    'Minnesota',
    'Indiana',
    'Rhode-Island',
    'Tennessee',
    'Connecticut',
    'South-Carolina',
    'Kansas',
    'Virginia',
    'Idaho',
    'Wisconsin',
    'Michigan',
    'Arkansas',
    'Alabama',
    'Mississippi',
    'Maine',
    'South-Dakota',
    'Montana',
    'Wyoming',
    'Louisiana',
    'Washington-DC',
    'New-Hampshire',
    'North-Dakota',
    'West-Virginia',
    'Alaska',
]


article = [0.0] * len(lst2)
count = 0
for name in lst2:
    source = requests.get(
        'https://www.seia.org/state-solar-policy/' + name + '-solar'
    ).text
    soup = BeautifulSoup(source, 'lxml')
    article[count] = soup.find(class_='field_mw_installed').find(
        class_="field-item"
    )
    count = count + 1


# name of csv file
filename = "SEIAdata.csv"


# writing to csv file
with open(filename, 'w') as csvfile:
    # creating a csv writer object
    csvwriter = csv.writer(csvfile)

    for i in range(len(article)):
        entry1 = lst2[i].replace("-", " ")
        entry2 = article[i].get_text().replace(",", "")
        row = [entry1, entry2]
        csvwriter.writerow(row)
