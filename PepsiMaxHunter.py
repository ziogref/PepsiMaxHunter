import requests, http.client, urllib, json, re

# Variables
ColesPepsi10Link = "https://www.coles.com.au/_next/data/20230502.01_v3.34.0/en/product/pepsi-max-multipack-cans-375ml-10-pack-2684166.json?slug=pepsi-max-multipack-cans-375ml-10-pack-2684166"
ColesPepsi24Link = "https://www.coles.com.au/_next/data/20230502.01_v3.34.0/en/product/pepsi-soft-drink-cola-max-24-pack-7366022.json?slug=pepsi-soft-drink-cola-max-24-pack-7366022"
ColesPepsi30Link = "https://www.coles.com.au/_next/data/20230502.01_v3.34.0/en/product/pepsi-max-soft-drink-375ml-can-30-pack-7837413.json?slug=pepsi-max-soft-drink-375ml-can-30-pack-7837413"
WooliesPepsi10Link = "https://www.woolworths.com.au/api/v3/ui/schemaorg/product/442190"
WooliesPepsi24Link = "https://www.woolworths.com.au/api/v3/ui/schemaorg/product/54291"
WooliesPepsi30Link = "https://www.woolworths.com.au/api/v3/ui/schemaorg/product/773129"
# User Agent was pulled from my Dell Laptop on 04/05/2023
getHeaders = {'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36'}

# Creates a "dictionary" in Python this is a way of storing data, so below the for loop will add data to the dictionary
ProcessedInformation = {}

# links contains all the "links" listed above to run a for loop over. But due to Woolworths and Coles information being different I have to filter differently
# thats why there is an "if" loop in the "for" loop
links =[ColesPepsi10Link, ColesPepsi24Link, ColesPepsi30Link, WooliesPepsi10Link, WooliesPepsi24Link, WooliesPepsi30Link]
for link in links:
    if 'coles' in str(link):

        # Stores the supermarket as a variable
        Store = "Coles"

        #Try/except is incase the the website timesout
        try:
            # Gets the data from the Coles links
            jsondata = requests.get(link, headers=getHeaders, timeout=10).json()

            # Price stored as a String for Displaying in a message later on
            priceString = str((jsondata['pageProps']['product']['pricing']['now']))

            # Price is grabbed a number to run math on
            priceNumber = (jsondata['pageProps']['product']['pricing']['now'])

            # Gets the amount of can in the box (e.g 24 pack)
            PackSizeName = (jsondata['pageProps']['product']['size'])

            # Capitilise the P in pack to make it look pretty
            PackSizeName = PackSizeName.replace('pack', 'Pack')

            # The "Size" information has the work "pack" in it. This strips this information
            PackSizeNumber = int(PackSizeName.split()[0])

            # format is $ + string (converted to display leading 0's if any(floating number(Price) divide by pack size), round to 2 decimal)finalise leading 0's)
            PricePerCan = '$' + str(f'{round(float((priceNumber) / PackSizeNumber), 2):.2f}')
            PricePerPack = '$' + priceString

            # Adds information to Dictionary
                # information is the following order. Name is Store + Pack size (e.g Coles 24 Pack), followed by 
                # Price (String)
                # Price Per can
            ProcessedInformation[Store + " " + PackSizeName] = [PricePerPack, PricePerCan]
            print("Coles")

        except requests.exceptions.Timeout:
            print('Coles timed out')

    if 'woolworths' in str (link):
        
        # Stores the supermarket as a variable
        Store = "Woolies"

        #Try/except is incase the the website timesout
        try:
            #Get cookie from the root website to use when calling the API
            response = requests.get('https://www.woolworths.com.au', headers=getHeaders, timeout=10)
            cookies = response.cookies

            WooliesAPICookie = {'bm_sz': cookies.get('bm_sz')}

            # Gets the data from the Woolies links
            jsondata = requests.get(link, headers=getHeaders, cookies=WooliesAPICookie, timeout=10).json()

            #Price stored as a String for Displaying in a message later on
            priceString = str((jsondata['offers']['price']))

            # Price is grabbed a number to run math on
            priceNumber = (jsondata['offers']['price'])

            # Name contains how many cans in the pack
            WooliesName = (jsondata['name'])

            #E xtracts pack size from text
            PackSizeNumber = int(re.search(r'\d+', WooliesName).group())

            # Add the word Pack to size
            PackSizeName = str(PackSizeNumber) + " Pack"

            # Format is $ + string (converted to display leading 0's if any(floating number(Price) divide by pack size), round to 2 decimal)finalise leading 0's)
            PricePerCan = '$' + str(f'{round(float((priceNumber) / PackSizeNumber), 2):.2f}')
            PricePerPack = '$' + str(f'{round(float((priceNumber)), 2):.2f}')
            #Adds information to Dictionary
                #information is the following order. Name is Store + Pack size (e.g Coles 24 Pack), followed by 
                #Price (String)
                #Price Per can
            ProcessedInformation[Store + " " + PackSizeName] = [PricePerPack, PricePerCan]

            print("Woolies")
            
        except requests.exceptions.Timeout:
            print('Woolies timed out')

# Sort the dictionary by the last value of each item
SortedInformation = sorted(ProcessedInformation.items(), key=lambda x: float(x[1][-1].replace('$', '')))

# Initialize an empty string to store the formatted output
PushoverMessage = ""

# Format each value as a new line with a custom header for each line
for item in SortedInformation:
    PushoverMessage += item[0] + "\n"
    PushoverMessage += "Price: " + item[1][0] + "\n"
    PushoverMessage += "Price per can: " + item[1][1] + "\n\n"

# Send Pushover
conn = http.client.HTTPSConnection("api.pushover.net:443")
conn.request("POST", "/1/messages.json",
  urllib.parse.urlencode({
    "token": "[App token here]",
    "user": "[User token here]",
    "message": PushoverMessage,
  }), { "Content-type": "application/x-www-form-urlencoded" })
conn.getresponse()
