import pandas as pd
import re

# Load the CSV file containing the list of top websites
def load_top_websites(csv_file):
    try:
        df = pd.read_csv(csv_file)
        df.columns = ['Website']
        df.head()
        return df['Website'].tolist()
    except FileNotFoundError:
        print(f"Error: CSV file '{csv_file}' not found.")
        return []

# Prepend "https://" to all websites
def prepend_https(websites):
    return ["https://" + website for website in websites]

# Check if the website is a URL shortener
def is_url_shortener(website, shortening_services):
    return any(re.match(shortening_service, website) for shortening_service in shortening_services)

# Remove URL shorteners from the list of websites
def remove_url_shorteners(websites, shortening_services):
    return [website for website in websites if not is_url_shortener(website, shortening_services)]

# Load list of top websites
csv_file = "top1kwebsites.csv"  # Specify the path to your CSV file containing top websites
top_websites = load_top_websites(csv_file)

# Prepend "https://" to all websites
top_websites_https = prepend_https(top_websites)

cleaned_websites = pd.DataFrame(top_websites_https, columns= ['Domain'])
cleaned_websites.head()

print("Cleaned websites:")
for website in cleaned_websites:
    print(website)

cleaned_websites.to_csv('cleanedtop1kc.csv', index= False)
