import re
import json

def extract_strings():
    with open('frontend/index.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find all Arabic strings (can include spaces, punctuation, numbers)
    # We will look for strings between > and <, or between quotes.
    
    matches_jsx = re.findall(r'>([^<]*[\u0600-\u06FF]+[^<]*)<', content)
    matches_quotes1 = re.findall(r'"([^"]*[\u0600-\u06FF]+[^"]*)"', content)
    matches_quotes2 = re.findall(r"'([^']*[\u0600-\u06FF]+[^']*)'", content)
    matches_backticks = re.findall(r'`([^`]*[\u0600-\u06FF]+[^`]*)`', content)
    
    all_matches = set(matches_jsx + matches_quotes1 + matches_quotes2 + matches_backticks)
    
    cleaned = []
    for m in all_matches:
        s = m.strip()
        if len(s) > 1:
            cleaned.append(s)
            
    with open('frontend/extracted.json', 'w', encoding='utf-8') as f:
        json.dump(sorted(cleaned), f, ensure_ascii=False, indent=2)

if __name__ == '__main__':
    extract_strings()
    print("Extracted strings to frontend/extracted.json")
