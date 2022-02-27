import requests
url = 'http://www.google.com'
response = requests.get(url)

data = {'user':'tim' 'passwd: 31337'}
response = requests.post(url, data=data) # POST
print(response.text)

