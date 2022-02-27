import urllib.request

url = 'http://www.google.com'
with urllib.request.urlopen(url) as response: # GET
    content = response.read()

print(content)