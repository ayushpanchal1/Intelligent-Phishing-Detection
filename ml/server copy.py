from flask import Flask, request, jsonify
import pandas as pd
import pickle
from urllib.parse import urlparse
import re
import ipaddress
from datetime import datetime
from urllib.parse import urlparse
import requests
import whois

app = Flask(__name__)

# Load the trained model
loaded_model = pickle.load(open("./models/XGBoostClassifierMAXWithWebTrafficOLD.pickle.dat", "rb"))

# Load the list of top 1000 websites
top1kWebsites = pd.read_csv('./datasets/top1kwebsites.csv')
top1kWebsites.columns = ['Domain']
top1kWebsiteslist = top1kWebsites['Domain'].tolist()

feature_names = ['Domain', 'Have_IP', 'Have_At', 'URL_Length', 'URL_Depth','Redirection',
                      'https_Domain', 'TinyURL', 'Prefix/Suffix', 'DNS_Record', 'Web_Traffic',
                      'Domain_Age', 'Domain_End', 'iFrame', 'Mouse_Over','Right_Click', 'Web_Forwards']

# Shortening services regex pattern
shortening_services = r"bit\.ly|goo\.gl|shorte\.st|go2l\.ink|x\.co|ow\.ly|t\.co|tinyurl|tr\.im|is\.gd|cli\.gs|" \
                      r"yfrog\.com|migre\.me|ff\.im|tiny\.cc|url4\.eu|twit\.ac|su\.pr|twurl\.nl|snipurl\.com|" \
                      r"short\.to|BudURL\.com|ping\.fm|post\.ly|Just\.as|bkite\.com|snipr\.com|fic\.kr|loopt\.us|" \
                      r"doiop\.com|short\.ie|kl\.am|wp\.me|rubyurl\.com|om\.ly|to\.ly|bit\.do|lnkd\.in|db\.tt|" \
                      r"qr\.ae|adf\.ly|goo\.gl|bitly\.com|cur\.lv|tinyurl\.com|ow\.ly|bit\.ly|ity\.im|q\.gs|is\.gd|" \
                      r"po\.st|bc\.vc|twitthis\.com|u\.to|j\.mp|buzurl\.com|cutt\.us|u\.bb|yourls\.org|x\.co|" \
                      r"prettylinkpro\.com|scrnch\.me|filoops\.info|vzturl\.com|qr\.net|1url\.com|tweez\.me|v\.gd|" \
                      r"tr\.im|link\.zip\.net"

def getDomain(url):
    domain = urlparse(url).netloc
    if re.match(r"^www.", domain):
        domain = domain.replace("www.", "")
    return domain

def havingIP(url):
    try:
        ipaddress.ip_address(url)
        ip = 1
    except:
        ip = 0
    return ip

def haveAtSign(url):
    return 1 if "@" in url else 0

def getLength(url):
    return 1 if len(url) >= 54 else 0

def getDepth(url):
    return len(urlparse(url).path.split('/'))

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
    domain = urlparse(url).netloc
    return 1 if 'https' in domain else 0

def tinyURL(url):
    match = re.search(shortening_services, url)
    return 1 if match else 0

def prefixSuffix(url):
    return 1 if '-' in urlparse(url).netloc else 0

def web_traffic(url):
    try:
        parsed_url = urlparse(url)
        domain_with_protocol = parsed_url.scheme + "://" + parsed_url.netloc
        domain_without_www = domain_with_protocol.replace('www.', '')
        if domain_without_www.startswith('http://'):
            domain_without_www = domain_without_www.replace('http://', 'https://')
            # print('yes') if domain_without_www in top1kWebsiteslist else print('not in list')
        return 0 if domain_without_www in top1kWebsiteslist else 1
    except Exception as e:
        print(f"Error: {e}")
        return 1

def domainAge(domain_name):
    creation_date = domain_name.creation_date
    expiration_date = domain_name.expiration_date
    if (isinstance(creation_date, str) or isinstance(expiration_date, str)):
        try:
            creation_date = datetime.strptime(creation_date, '%Y-%m-%d')
            expiration_date = datetime.strptime(expiration_date, "%Y-%m-%d")
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
        return 1 if (ageofdomain / 30) < 6 else 0

def domainEnd(domain_name):
    expiration_date = domain_name.expiration_date
    if isinstance(expiration_date, str):
        try:
            expiration_date = datetime.strptime(expiration_date, "%Y-%m-%d")
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
        return 1 if ((end / 30) < 6) else 0

def iframe(response):
    if response == "":
        return 1
    else:
        if re.search(r"<iframe\s+(?:(?!frameBorder).)*>", response.text, re.IGNORECASE):
            return 1
        else:
            return 0

def mouseOver(response):
    if response == "":
        return 1
    else:
        if re.findall("<script>.+onmouseover.+</script>", response.text):
            return 1
        else:
            return 0

def rightClick(response):
    if response == "":
        return 1
    else:
        if re.search(r"event\.button\s*===\s*2", response.text):
            return 1
        else:
            return 0

def forwarding(response):
    if response == "":
        return 1
    else:
        if len(response.history) <= 2:
            return 0
        else:
            return 1

def featureExtraction(url):
    features = []
    features.append(getDomain(url))
    features.append(havingIP(url))
    features.append(haveAtSign(url))
    features.append(getLength(url))
    features.append(getDepth(url))
    features.append(redirection(url))
    features.append(httpDomain(url))
    features.append(tinyURL(url))
    features.append(prefixSuffix(url))
    dns = 0
    try:
        domain_name = whois.whois(urlparse(url).netloc)
    except:
        dns = 1
    features.append(dns)
    features.append(web_traffic(url))
    features.append(1 if dns == 1 else domainAge(domain_name))
    features.append(1 if dns == 1 else domainEnd(domain_name))
    try:
        response = requests.get(url, timeout=10)
    except Exception as e:
        print(f"Error fetching URL {url}: {str(e)}")
        response = ""
    features.append(iframe(response))
    features.append(mouseOver(response))
    features.append(rightClick(response))
    features.append(forwarding(response))
    return features

def predict_phishing(url):
    print(url)
    with open('pdomat.txt', 'r') as file:
        urls_in_file = file.read().splitlines()
        # Remove trailing slash if present
        url_without_trailing_slash = url.rstrip('/')
        if url_without_trailing_slash in urls_in_file or url.replace('https://', 'http://') in urls_in_file or url.replace('http://', 'https://') in urls_in_file:
            print("Phishing")
            return "Phishing"
        else:
            return "Legitimate"

@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    url = data['url']
    result = predict_phishing(url)
    features = featureExtraction(url) # this gets called twice, once here and again in the predict_phishing func 
                                      # uhhh well it works and is fast enough for now
    input_data = pd.DataFrame([features], columns=feature_names)
    input_data = input_data.drop(['Domain'], axis=1).copy()
    input_data_dict = input_data.to_dict(orient='records')
    return jsonify({"result": result, "data": input_data_dict})


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
