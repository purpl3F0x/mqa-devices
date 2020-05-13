import requests
from bs4 import BeautifulSoup
import helper
import csv

URL = "https://www.mqa.co.uk"
FIRST_URL = URL + "/how-to-get-mqa"


visited_manufacturers = []

s = {}

def parse_product_page(url):
  url = URL + url
  page_ = requests.get(url)
  soup_ = BeautifulSoup(page_.content, "html.parser")

  manufacturer = soup_.find("div", {"class": "banner panel"}).text.strip()

  if manufacturer in visited_manufacturers:
    return 
  else:
    visited_manufacturers.append(manufacturer)
    s[manufacturer] = []

  print("\t+", manufacturer)

  products = soup_.findAll("div", {"class": "c-playback-partner__left"})
  products_title = [p.find("h2",{"class": "c-playback-partner__title"}) for p in products]
  refs = [p.find("a", href=True) for p in products]

  for p, r in zip(products_title, refs):
    name = p.text.strip()
    if name.split(":")[0] in helper.categories or name.split(":")[0][:-1] in helper.categories:
      cat, name = name.split(":")
      print("\t\t+", cat, name, r['href'])
      s[manufacturer].append(
        {
          "name": name,
          "category": cat,
          "url": r['href'],
        }
      )





page = requests.get(FIRST_URL)

soup = BeautifulSoup(page.content, "html.parser")
results = soup.findAll("div", {"class": "c-partners-panel__devices"})


SKIP = ["Download", "Streaming & Applications", "Smartphones"]
for r in results:
  category = r.find("div", {"class": "c-partners-panel__content"})
  category_txt = r.find("h4", {"class": "c-partners-panel__device-title"}).text.strip()

  print("+", category_txt)
  if category_txt in SKIP: 
    print("\t- Ignoring\n")
    continue
  
  cat_parteners = category.findAll("a", {"class": "c-partners-panel__tile"}, href=True)
  for partner in cat_parteners:
    parse_product_page(partner['href'])


tr = '''
<tr>
  <td>{0}</td>
  <td>{1}</td>
  <td>{2}</td>
  <td><a href="{3}">{3}</a></td>
</tr>
'''

with open('in.html', 'r') as fin:
  h = fin.read()
  with open('index.html', 'w') as fout:
    tbody = ""
    for man, products in s.items():
      print(products)
      for p in products:
        tbody += tr.format(man , p['name'], p['category'], p['url'])

    h = h.replace("{%tbody%}", tbody)
    fout.write(h)


with open('output.csv', 'w') as csvfile:
  spamreader = csv.writer(csvfile, delimiter=',')
  spamreader.writerow(['Manufacturer', 'Name' ,'Category', 'URL'])

  for man, products in s.items():
    print(products)
    for p in products:
      spamreader.writerow([man , p['name'], p['category'], p['url']])
