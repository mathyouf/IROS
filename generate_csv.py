import csv
import json

def create_highlighted_papers_csv():
    """_summary_
    Reads paper titles from 'topapers.csv' and schedule data from 'schedule.json',
    then generates 'highlighted_papers.csv' containing titles and abstracts of highlighted papers.
    """
    # Read the list of paper titles to highlight
    with open('topapers.csv', 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader)  # Skip header
        highlight_titles = {row[0].strip() for row in reader}

    # Read the schedule data
    with open('schedule.json', 'r', encoding='utf-8') as f:
        schedule_data = json.load(f)

    # Prepare data for the new CSV
    highlighted_papers = []
    for session in schedule_data:
        for paper in session.get('papers', []):
            if paper.get('title') in highlight_titles:
                highlighted_papers.append({
                    'title': paper.get('title'),
                    'abstract': paper.get('abstract', 'No abstract available')
                })

    # Write the highlighted papers to a new CSV file
    with open('highlighted_papers.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Paper Title', 'Abstract'])
        for paper in highlighted_papers:
            writer.writerow([paper['title'], paper['abstract']])

    print(f"Successfully created highlighted_papers.csv with {len(highlighted_papers)} papers.")

if __name__ == '__main__':
    create_highlighted_papers_csv()
