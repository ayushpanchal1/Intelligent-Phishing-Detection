import pandas as pd
import requests
import re
import whois
import urllib
import urllib.request
from datetime import datetime
from urllib.parse import urlparse,urlencode
import ipaddress
import time
import concurrent.futures
from urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

dataset = pd.read_csv("../Static/feedback.csv")

top1kWebsites = pd.read_csv('../Static/top1kwebsites.csv')
top1kWebsites.columns = ['Domain']
top1kWebsiteslist = top1kWebsites['Domain'].tolist()

feature_names = ['Domain', 'Have_IP', 'Have_At', 'URL_Length', 'URL_Depth','Redirection', 'https_Domain', 'TinyURL', 'Prefix/Suffix', 'DNS_Record', 'Web_Traffic', 'Domain_Age', 'Domain_End', 'iFrame', 'Mouse_Over','Right_Click', 'Web_Forwards']

def getDomain(url):
  domain = urlparse(url).netloc
  if re.match(r"^www.",domain):
    domain = domain.replace("www.","")
  return domain

def havingIP(url):
  try:
    ipaddress.ip_address(url)
    ip = 1
  except:
    ip = 0
  return ip

def haveAtSign(url):
  if "@" in url:
    at = 1
  else:
    at = 0
  return at

def getLength(url):
  if len(url) < 54:
    length = 0
  else:
    length = 1
  return length

def getDepth(url):
  s = urlparse(url).path.split('/')
  depth = 0
  for j in range(len(s)):
    if len(s[j]) != 0:
      depth = depth+1
  return depth

def redirection(url):
  pos = url.rfind('//')
  if pos > 6:
    if pos > 7:
      return 1
    else:
      return 0
  else:
    return 0
  
def httpDomain(url):
  if 'https' in url:
    return 1
  else:
    return 0
  
shortening_services = r"bit\.ly|goo\.gl|shorte\.st|go2l\.ink|x\.co|ow\.ly|t\.co|tinyurl|tr\.im|is\.gd|cli\.gs|" \
                      r"yfrog\.com|migre\.me|ff\.im|tiny\.cc|url4\.eu|twit\.ac|su\.pr|twurl\.nl|snipurl\.com|" \
                      r"short\.to|BudURL\.com|ping\.fm|post\.ly|Just\.as|bkite\.com|snipr\.com|fic\.kr|loopt\.us|" \
                      r"doiop\.com|short\.ie|kl\.am|wp\.me|rubyurl\.com|om\.ly|to\.ly|bit\.do|t\.co|lnkd\.in|db\.tt|" \
                      r"qr\.ae|adf\.ly|goo\.gl|bitly\.com|cur\.lv|tinyurl\.com|ow\.ly|bit\.ly|ity\.im|q\.gs|is\.gd|" \
                      r"po\.st|bc\.vc|twitthis\.com|u\.to|j\.mp|buzurl\.com|cutt\.us|u\.bb|yourls\.org|x\.co|" \
                      r"prettylinkpro\.com|scrnch\.me|filoops\.info|vzturl\.com|qr\.net|1url\.com|tweez\.me|v\.gd|" \
                      r"tr\.im|link\.zip\.net"

def tinyURL(url):
    match=re.search(shortening_services,url)
    if match:
        return 1
    else:
        return 0

def prefixSuffix(url):
    if '-' in urlparse(url).netloc:
        return 1
    else:
        return 0

def web_traffic(url):
    try:
        parsed_url = urlparse(url)
        domain_with_protocol = parsed_url.scheme + "://" + parsed_url.netloc
        domain_without_www = domain_with_protocol.replace('www.', '')
        if domain_without_www.startswith('http://'):
            domain_without_www = domain_without_www.replace('http://', 'https://')
        return 0 if domain_without_www in top1kWebsiteslist else 1
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
def domainAge(domain_name):
  creation_date = domain_name.creation_date
  print("creation date is", creation_date) #
  expiration_date = domain_name.expiration_date
  print("expiration date is", expiration_date) #
  print("type of creation date is", type(creation_date))
  print("type of expiration date is", type(expiration_date))

  if (isinstance(creation_date,str) or isinstance(expiration_date,str)):
    try:
      creation_date = datetime.strptime(creation_date,'%Y-%m-%d')
      expiration_date = datetime.strptime(expiration_date,"%Y-%m-%d")
      print("stripped creation date is", creation_date)
      print("stripped expiration date is", expiration_date)
    except:
      return 1

  if type(creation_date) is list:
    creation_date = creation_date[0]
  if type(expiration_date) is list:
    expiration_date = expiration_date[0]
  if ((expiration_date is None) or (creation_date is None)):
      return 1
  elif ((type(expiration_date) is list) or (type(creation_date) is list)):
      return 1
  else:
    ageofdomain = abs((expiration_date - creation_date).days)
    if ((ageofdomain/30) < 6):
      age = 1
    else:
      age = 0
  return age

def domainEnd(domain_name):
  expiration_date = domain_name.expiration_date
  if isinstance(expiration_date,str):
    try:
      expiration_date = datetime.strptime(expiration_date,"%Y-%m-%d")
    except:
      return 1
  if type(expiration_date) is list:
    expiration_date = expiration_date[0]
  if (expiration_date is None):
      return 1
  elif (type(expiration_date) is list):
      return 1
  else:
    today = datetime.now()
    end = abs((expiration_date - today).days)
    if ((end/30) < 6):
      end = 1
    else:
      end = 0
  return end

def iframe(response):
    if response == "":
        return 1  # Phishing: Empty response
    else:
        if re.search(r"<iframe\s+(?:(?!frameBorder).)*>", response.text, re.IGNORECASE):
            return 1  # Phishing: iframe tag found without frameBorder attribute
        else:
            return 0
        
def mouseOver(response):
  if response == "" :
    return 1
  else:
    if re.findall("<script>.+onmouseover.+</script>", response.text):
      return 1
    else:
      return 0
    
def rightClick(response):
    if response == "":
        return 1  # Phishing: Empty response
    else:
        if re.search(r"event\.button\s*===\s*2", response.text):
            return 1  # Phishing: Right click disabled
        else:
            return 0
        
def forwarding(response):
  if response == "":
    return 1
  else:
    if len(response.history) <= 2: # should be 1 or max 2 for legitimates
      return 0
    else:
      return 1
    
def featureExtraction(url, label):
    features = []
    # Address bar based features (10)
    features.append(getDomain(url))
    features.append(havingIP(url))
    features.append(haveAtSign(url))
    features.append(getLength(url))
    features.append(getDepth(url))
    features.append(redirection(url))
    features.append(httpDomain(url))
    features.append(tinyURL(url))
    features.append(prefixSuffix(url))

    print("Address bar features extracted.")

    # Domain based features (4)
    dns = 0
    try:
        domain_name = whois.whois(urlparse(url).netloc)
    except:
        dns = 1

    features.append(dns)
    features.append(web_traffic(url))

    features.append(1 if dns == 1 else domainAge(domain_name))
    features.append(1 if dns == 1 else domainEnd(domain_name))

    print("Domain based features extracted.")

    # HTML & Javascript based features (4)
    try:
        response = requests.get(url, timeout=10, verify=False)  # Timeout set to 10 seconds
    except Exception as e:
        print(f"Error fetching URL {url}: {str(e)}")
        response = ""

    features.append(iframe(response))
    features.append(mouseOver(response))
    features.append(rightClick(response))
    features.append(forwarding(response))
    features.append(label)

    print("HTML & Javascript based features extracted.")

    return features


legi_features = []
label = 0

def process_url(url):
    return featureExtraction(url, label)

# Define the maximum number of threads (adjust as needed)
MAX_THREADS = 1

# Get the size of legiurl
num_urls = len(dataset['URL'])

# Create a ThreadPoolExecutor
with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
    # Map the process_url function to each URL in legiurl
    results = list(executor.map(process_url, dataset['URL']))

# Process the results if needed
for i, result in enumerate(results):
    legi_features.append(result)
    print(f"Processed {i+1} URLs.")

feature_names = ['Domain', 'Have_IP', 'Have_At', 'URL_Length', 'URL_Depth','Redirection',
                      'https_Domain', 'TinyURL', 'Prefix/Suffix', 'DNS_Record', 'Web_Traffic',
                      'Domain_Age', 'Domain_End', 'iFrame', 'Mouse_Over','Right_Click', 'Web_Forwards', 'Label']

legitimate = pd.DataFrame(legi_features, columns= feature_names)

legitimate.to_csv('../Static/feedback-features.csv', index= False)