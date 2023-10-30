#!/bin/python
import sys
from bs4 import BeautifulSoup
import requests

response = requests.get(sys.argv[1])
soup = BeautifulSoup(response.text, "html")
print(soup.prettify())
