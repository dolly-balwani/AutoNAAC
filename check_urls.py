from excel_parser import parse_criterion_sheet

events = parse_criterion_sheet('data/Criteria 5.1.3 CMPN Data 2024-25.xlsx', '5.1.3')

print("Google Doc URLs found:")
for i, e in enumerate(events[:10]):
    name = e['name'][:40]
    link = e['doc_link']
    print(f"{i+1}. {name}")
    print(f"   URL: {link}")
    print()
