import sys
try:
    import pypdf
except ImportError:
    print("pypdf not installed")
    sys.exit(1)

reader = pypdf.PdfReader('legacy/2023ShahidZaman_Polycyclic.pdf')
print(f"Total pages: {len(reader.pages)}")
for i in range(5, min(12, len(reader.pages))):
    print(f"--- PAGE {i+1} ---")
    print(reader.pages[i].extract_text()[:1200])
