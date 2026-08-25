import sys
import os

# Add the dashboard path to python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from catalog_app import generate_pdf_report
except ImportError as e:
    print(f"Error importing catalog_app: {e}")
    sys.exit(1)

# Mock some dummy product data
mock_products = [
    {
        "product_name": "10T Hydraulic Bottle Jack",
        "ref_code": "EDQ71010",
        "company": "Deli",
        "category": "Handtools",
        "series": "Pro Series",
        "specification": "8\"(200mm)\nEdge cutting life exceeds 10,000 times\nHead material: #55 Carbon Steel",
        "mrp": 5400.0,
        "packing_pcs": 1,
        "image_url": ""
    },
    {
        "product_name": "12V Cordless Drill Driver",
        "ref_code": "EDQ71212",
        "company": "Tejas",
        "category": "Power Tools",
        "series": "Basic",
        "specification": "No-load speed: 0-400/0-1350rpm\nMax torque: 25N.m\nBattery: 1.5Ah Li-ion",
        "mrp": 7500.5,
        "packing_pcs": 2,
        "packing_bx": 10,
        "image_url": ""
    },
    {
        "product_name": "Heavy Duty Wrench Set",
        "ref_code": "EDQ78891",
        "company": "Deli Tools",
        "category": "Handtools",
        "series": "Pro Series",
        "specification": "12 pcs set\nChrome Vanadium Steel\nAnti-rust coating",
        "mrp": 2100.0,
        "packing_pcs": 1,
        "packing_bx": 5,
        "image_url": ""
    }
]

print("Generating test PDF...")
try:
    pdf_bytes = generate_pdf_report(mock_products)
    output_file = "test_catalog_report.pdf"
    
    with open(output_file, "wb") as f:
        f.write(pdf_bytes)
        
    print(f"✅ Successfully generated '{output_file}'!")
    print(f"You can open '{os.path.abspath(output_file)}' to verify the new 'PRODUCT DETAILS' header, grid layout, and removed footer.")
except Exception as e:
    print(f"❌ Error during generation: {e}")
    import traceback
    traceback.print_exc()
