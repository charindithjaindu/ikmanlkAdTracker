import requests
import re
import json

def fetch_ads(keyword):
    """Fetches ads from ikman.lk for a given keyword."""
    try:
        params = {
            'query': keyword,
        }
        response = requests.get('https://ikman.lk/en/ads', params=params)
        response.raise_for_status()

        pattern = r'window.initialData = (.*?)</script>'
        match = re.findall(pattern, response.text, re.DOTALL)
        match = [script for script in match if "serp" in script and "browserInfo" in script]
        if not match:
            return []

        json_data = json.loads(match[0])
        ads_data = json_data.get('serp', {}).get('ads', {}).get('data', {})
        
        ads = ads_data.get('ads', [])
        top_ads = ads_data.get('topAds', [])
        
        all_ads = ads

        formatted_ads = []
        for ad in all_ads:
            formatted_ads.append({
                'id': ad.get('id'),
                'title': ad.get('title'),
                'url': 'https://ikman.lk/en/ad/' + ad.get('slug'),
                'image_url': ad.get('imgUrl').replace("142/107/cropped.jpg", "2048/2048/fitted.jpg"),
                'price': ad.get('price'),
                'location': ad.get('location'),
                'timeStamp': ad.get('timeStamp')
            })

        return formatted_ads

    except requests.exceptions.RequestException as e:
        print(f"Error fetching ads for '{keyword}': {e}")
        return []
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON for '{keyword}': {e}")
        return []


if __name__ == '__main__':
    ads = fetch_ads('pixel 9')
    print(ads)
    