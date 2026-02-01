"""Test fetching from a real Drive folder."""
from drive_fetcher import GoogleDriveFetcher
from excel_parser import parse_criterion_sheet

# Get first event with Drive folder URL
events = parse_criterion_sheet('data/Criteria 5.1.3 CMPN Data 2024-25.xlsx', '5.1.3')

# Find first event with a Drive URL
for event in events[:5]:
    url = event.get('doc_link', '')
    if url and 'drive.google.com' in url:
        print(f"Event: {event['name']}")
        print(f"URL: {url}")
        
        fetcher = GoogleDriveFetcher()
        result = fetcher.fetch_folder_content(url, output_dir="temp_downloads")
        
        if result['success']:
            print(f"\n✅ SUCCESS!")
            print(f"Files found: {len(result['files'])}")
            print(f"Text content length: {len(result['text_content'])} chars")
            print(f"Images: {len(result['images'])}")
            
            # Show preview
            if result['text_content']:
                print(f"\nContent preview:")
                print(result['text_content'][:500])
        else:
            print(f"\n❌ Error: {result['error']}")
        
        break
