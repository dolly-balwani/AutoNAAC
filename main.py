import argparse
from agents import app
from fpdf import FPDF

def generate_pdf(criterion: str, content: str, filename: str):
    """Generates a PDF report from the text content."""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # Title
    pdf.set_font("Helvetica", "B", 16)
    # Encode title to handle special chars
    safe_title = criterion.encode('latin-1', errors='replace').decode('latin-1')
    pdf.cell(0, 10, f"NAAC Criterion: {safe_title}", ln=True, align="C")
    pdf.ln(10)
    
    # Body - encode to handle special characters
    pdf.set_font("Helvetica", "", 11)
    safe_content = content.encode('latin-1', errors='replace').decode('latin-1')
    pdf.multi_cell(0, 7, safe_content)
    
    pdf_filename = filename.replace(".txt", ".pdf")
    pdf.output(pdf_filename)
    return pdf_filename

def generate_report(criterion: str):
    """
    Runs the Multi-Agent System for a specific Criterion.
    """
    print(f"\n🚀 STARTING NAAC REPORT GENERATION FOR: {criterion}\n")
    print("="*60)
    
    initial_state = {
        "criterion": criterion,
        "evidence": "",
        "draft": "",
        "critique": "",
        "revision_count": 0,
        "final_report": ""
    }
    
    # Run the Graph
    final_state = app.invoke(initial_state)
    
    print("\n" + "="*60)
    print("✅ FINAL REPORT GENERATED")
    print("="*60)
    print(final_state["draft"])
    print("="*60)
    
    # Save to TXT file
    txt_filename = f"report_{criterion.replace(' ', '_')}.txt"
    with open(txt_filename, "w", encoding="utf-8") as f:
        f.write(f"NAAC CRITERION: {criterion}\n\n")
        f.write(final_state["draft"])
    
    print(f"\n📂 Saved TXT report to: {txt_filename}")
    
    # Save to PDF file
    pdf_filename = generate_pdf(criterion, final_state["draft"], txt_filename)
    print(f"📄 Saved PDF report to: {pdf_filename}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="NAAC Report Generator Agent")
    parser.add_argument("--criterion", type=str, required=True, help="The NAAC Criterion to generate a report for")
    
    args = parser.parse_args()
    generate_report(args.criterion)
