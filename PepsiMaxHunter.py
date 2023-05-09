import requests, http.client, urllib, re

#Product links in JSON format
links = {
'ColesPepsi10Link': 'https://www.coles.com.au/product/pepsi-max-multipack-cans-375ml-10-pack-2684166',
'ColesPepsi24Link': 'https://www.coles.com.au/product/pepsi-soft-drink-cola-max-24-pack-7366022',
'ColesPepsi30Link': 'https://www.coles.com.au/product/pepsi-max-soft-drink-375ml-can-30-pack-7837413',
'WooliesPepsi10Link': 'https://www.woolworths.com.au/shop/productdetails/442190/pepsi-max-cans',
'WooliesPepsi24Link': 'https://www.woolworths.com.au/shop/productdetails/54291/pepsi-max-cans',
'WooliesPepsi30Link': 'https://www.woolworths.com.au/shop/productdetails/773129/pepsi-max-cans',
}

# User Agent was pulled from my Dell Laptop on 04/05/2023
getHeaders = {'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36'}

# Creates a "dictionary" in Python this is a way of storing data, so below the for loop will add data to the dictionary
ProcessedInformation = {}

#Get cookie from Woolworths to bypass WAF.
response = requests.get('https://www.woolworths.com.au', headers=getHeaders, timeout=10)
cookies = response.cookies
WooliesAPICookie = {'bm_sz': cookies.get('bm_sz')}

# for loop that goes over each item in links array
# link is the link name (e.g ColesPepsi24) | links.keys is items within the array
for link in links.keys():
    # links[link] is just the url
    link = links[link]

    # If link has coles in the URL, its going to go through the coles filter
    if 'coles' in str(link):

        # Stores the supermarket as a variable
        Store = "Coles"

        #Try/except is incase the the website timesout
        try:

            # split the URL into parts using the "/" separator
            url_parts = link.split("/")

            # get the last part of the URL, which contains the product code
            product_code = url_parts[-1]

            # Add the Product code to the API URL
            apilink = "https://www.coles.com.au/_next/data/20230502.01_v3.34.0/en/product/" + product_code + ".json"           

            # Gets the data from the Coles links
            jsondata = requests.get(apilink, headers=getHeaders, timeout=10).json()

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

    # If link has woolworth in the URL, its going to go through the coles filter
    if 'woolworths' in str (link):
        
        # Stores the supermarket as a variable
        Store = "Woolies"

        #Try/except is incase the the website timesout
        try:
            # split the URL into parts using the "/" separator
            url_parts = link.split("/")

            # get the second-to-last part of the URL, which contains the product code
            product_code = url_parts[-2]

            # Add the Product code to the API URL
            apilink = "https://www.woolworths.com.au/api/v3/ui/schemaorg/product/" + product_code

            # Gets the data from the Woolies links
            jsondata = requests.get(apilink, headers=getHeaders, cookies=WooliesAPICookie, timeout=10).json()

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
