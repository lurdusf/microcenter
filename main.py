import requests
import time
from bs4 import BeautifulSoup
from discord_hooks import Webhook

webhookUrl = None # redacted this for privacy reasons
link = "https://www.microcenter.com/search/search_results.aspx?N=4294966937&NTK=all&sortby=pricehigh&rpp=96"

headers = {
    'User-Agent': '...',
    'referer': 'htttps://...'
}

cookies = {
    'storeSelected': '075'
}

class GPU:
    
    def __init__(self, details, image, stock):
        self.Name = details["data-name"]
        self.Price = details['data-price']
        self.Link = "https://microcenter.com" + details['href']
        self.Image = image
        self.Stock = stock


def getAvailableCards():
    try:
        req = requests.get(link, headers=headers, cookies=cookies)
        soup = BeautifulSoup(req.text, features="lxml")

        cards = soup.find_all(attrs={'class': 'product_wrapper'})
        _cards = []
        for card in cards:
            info = card.find('div', attrs={'class': 'pDescription compressedNormal2'})

            details = info.findChildren()[0].findChildren()[0].findChildren()[0]
            stock = ''.join(filter(str.isdigit, card.find('div', attrs={'class': 'stock'}).findChildren()[0].text))
            image = card.find('img', attrs={'class': 'SearchResultProductImage'})['src']
            if stock == "25":
                stock = "25+"
            _cards.append(GPU(details, image, stock))
        return _cards
    except:
        return []
 
def getCardType(name):
    _types = ["RTX 3090", "RTX 3080", "RTX 3070", "RTX 3060 TI", "RTX 3060"]
    _type = "Other"
    for v in _types:
        if name.find(v) != -1:
            _type = v
            break
    return _type

def postCard(card):
    msg = Webhook(webhookUrl, msg="<@>")
    msg.post()

    embed = Webhook(webhookUrl, color=7846144)
    embed.set_author(name=getCardType(card.Name), icon='https://cdn4.iconfinder.com/data/icons/logos-and-brands/512/235_Nvidia_logo-512.png')
    embed.set_desc(card.Name)
    embed.add_field(name="Price", value="$"+card.Price)
    embed.add_field(name="Stock", value=card.Stock)
    embed.add_field(name="Link", value=card.Link)
    embed.set_image(card.Image)
    embed.set_timestamp(now=True)

    embed.post()

def arrayFind(array, string):
    found = True
    try:
        activeCards.index(string)
    except ValueError:
        found = False
    if found == True:
        return activeCards.index(string)
    else:
        return -1

activeCards = []

print("Began watching the MicroCenter GPU page.")

while True:
    cards = getAvailableCards()
    names = []
    for card in cards:
        names.append(card.Name)
        if (getCardType(card.Name) != "Other") and arrayFind(activeCards, card.Name) == -1:
            activeCards.append(card.Name)
            postCard(card)
        
    for card in activeCards:
        if arrayFind(names, card) == -1:
            activeCards.remove(card)
    
    time.sleep(5)