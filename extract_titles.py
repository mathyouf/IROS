import json

def extract_unique_titles():
    try:
        with open('/Users/matto/Desktop/IROS/schedule.json', 'r') as f:
            schedule_data = json.load(f)
    except FileNotFoundError:
        print("Error: schedule.json not found.")
        return
    except json.JSONDecodeError:
        print("Error: Could not decode schedule.json.")
        return

    unique_titles = set()
    for session in schedule_data:
        for paper in session.get('papers', []):
            if 'title' in paper:
                unique_titles.add(paper['title'])

    with open('/Users/matto/Desktop/IROS/unique_titles.txt', 'w') as f:
        for title in sorted(list(unique_titles)):
            f.write(f"{title}\n")

    print(f"Successfully extracted {len(unique_titles)} unique titles to unique_titles.txt")

if __name__ == '__main__':
    extract_unique_titles()
