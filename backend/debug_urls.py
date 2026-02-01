from excel_parser import parse_criterion_sheet

events = parse_criterion_sheet('data/Criteria 5.1.3 CMPN Data 2024-25.xlsx', '5.1.3')

print("Checking failing URLs (events 18-26):")
for i, e in enumerate(events[18:26]):
    idx = i + 18
    url = e.get('doc_link', '')
    print(f"\n{idx}. {e['name'][:40]}")
    print(f"   URL: {url}")
