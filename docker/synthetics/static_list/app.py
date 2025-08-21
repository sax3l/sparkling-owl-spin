"""
Syntetisk statisk list-sajt för E2E-tester

För nybörjare: Denna Flask-app simulerar en webbplats med:
- Statisk lista med länkar
- Detaljsidor för fordon
- Paginering
- Standardiserad HTML-struktur för scraping-tester

Används ENDAST för testning - ingen riktig data eller externa anrop.
"""

from flask import Flask, Response, request

app = Flask(__name__)

# Sample vehicle data för tester
VEHICLES = [
    {"id": 1, "reg": "ABC123", "make": "Volvo", "model": "XC60", "year": 2021, "co2": 132.5},
    {"id": 2, "reg": "DEF456", "make": "BMW", "model": "X3", "year": 2020, "co2": 145.2},
    {"id": 3, "reg": "GHI789", "make": "Audi", "model": "Q5", "year": 2022, "co2": 128.0},
    {"id": 4, "reg": "JKL012", "make": "Mercedes", "model": "GLC", "year": 2021, "co2": 155.8},
    {"id": 5, "reg": "MNO345", "make": "Toyota", "model": "RAV4", "year": 2023, "co2": 102.3},
    {"id": 6, "reg": "PQR678", "make": "Volkswagen", "model": "Tiguan", "year": 2020, "co2": 142.7},
    {"id": 7, "reg": "STU901", "make": "Volvo", "model": "XC90", "year": 2022, "co2": 168.9},
    {"id": 8, "reg": "VWX234", "make": "BMW", "model": "X5", "year": 2021, "co2": 198.4},
    {"id": 9, "reg": "YZA567", "make": "Audi", "model": "Q7", "year": 2023, "co2": 185.2},
    {"id": 10, "reg": "BCD890", "make": "Mercedes", "model": "GLE", "year": 2022, "co2": 203.1},
]

@app.route("/")
def root():
    """Root-sida för hälsokontroll"""
    return Response("Synthetic Static List Service OK", mimetype="text/plain")

@app.route("/list")
def list_page():
    """Huvudlista med fordon - simulerar biluppgifter.se liknande sajt"""
    page = int(request.args.get("page", 1))
    per_page = 5
    start = (page - 1) * per_page
    end = start + per_page
    
    page_vehicles = VEHICLES[start:end]
    has_next = end < len(VEHICLES)
    has_prev = page > 1
    
    html = f"""<!doctype html>
<html>
<head>
    <meta charset="utf-8">
    <title>Fordonslista - Sida {page}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .vehicle-list {{ list-style: none; padding: 0; }}
        .vehicle-item {{ 
            border: 1px solid #ddd; 
            margin: 10px 0; 
            padding: 15px; 
            border-radius: 5px; 
        }}
        .vehicle-item a {{ 
            text-decoration: none; 
            color: #0066cc; 
            font-weight: bold; 
        }}
        .pagination {{ margin: 20px 0; }}
        .pagination a {{ 
            display: inline-block; 
            padding: 8px 16px; 
            margin: 0 4px; 
            text-decoration: none; 
            border: 1px solid #ddd; 
        }}
    </style>
</head>
<body>
    <h1>Fordonslista</h1>
    <ul class="vehicle-list" id="vehicle-items">"""
    
    for vehicle in page_vehicles:
        html += f"""
        <li class="vehicle-item">
            <a href="/item/{vehicle['id']}">{vehicle['reg']} - {vehicle['make']} {vehicle['model']}</a>
            <div class="vehicle-summary">
                År: {vehicle['year']}, CO₂: {vehicle['co2']} g/km
            </div>
        </li>"""
    
    html += """
    </ul>
    <div class="pagination">"""
    
    if has_prev:
        html += f'<a href="/list?page={page-1}">← Föregående</a>'
    
    html += f'<span>Sida {page}</span>'
    
    if has_next:
        html += f'<a href="/list?page={page+1}">Nästa →</a>'
    
    html += """
    </div>
</body>
</html>"""
    
    return Response(html, mimetype="text/html")

@app.route("/item/<int:vehicle_id>")
def item_detail(vehicle_id):
    """Detaljsida för enskilt fordon"""
    vehicle = next((v for v in VEHICLES if v["id"] == vehicle_id), None)
    
    if not vehicle:
        return Response("Fordon ej hittat", status=404)
    
    html = f"""<!doctype html>
<html>
<head>
    <meta charset="utf-8">
    <title>Fordonsinformation - {vehicle['reg']}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .vehicle-details {{ max-width: 600px; }}
        .detail-row {{ 
            display: flex; 
            margin: 10px 0; 
            border-bottom: 1px solid #eee; 
            padding-bottom: 8px; 
        }}
        .detail-label {{ 
            font-weight: bold; 
            width: 200px; 
            flex-shrink: 0; 
        }}
        .detail-value {{ flex-grow: 1; }}
        .back-link {{ 
            display: inline-block; 
            margin-top: 20px; 
            text-decoration: none; 
            color: #0066cc; 
        }}
    </style>
</head>
<body>
    <h1>Fordonsinformation</h1>
    <div class="vehicle-details">
        <div class="detail-row">
            <div class="detail-label">Registreringsnummer:</div>
            <div class="detail-value" id="registration-number">{vehicle['reg']}</div>
        </div>
        <div class="detail-row">
            <div class="detail-label">Märke:</div>
            <div class="detail-value" id="make">{vehicle['make']}</div>
        </div>
        <div class="detail-row">
            <div class="detail-label">Modell:</div>
            <div class="detail-value" id="model">{vehicle['model']}</div>
        </div>
        <div class="detail-row">
            <div class="detail-label">Modellår:</div>
            <div class="detail-value" id="model-year" data-spec="modelYear">{vehicle['year']}</div>
        </div>
        <div class="detail-row">
            <div class="detail-label">CO₂ (WLTP):</div>
            <div class="detail-value" id="wltp-co2">{vehicle['co2']} g/km</div>
        </div>
    </div>
    <a href="/list" class="back-link">← Tillbaka till listan</a>
</body>
</html>"""
    
    return Response(html, mimetype="text/html")

@app.route("/robots.txt")
def robots():
    """Robots.txt för att testa robots-respekt"""
    return Response("""User-agent: *
Allow: /
Crawl-delay: 1

# Test-kommentar: Denna robots.txt är för syntetiska tester
""", mimetype="text/plain")

@app.route("/sitemap.xml")
def sitemap():
    """Enkel sitemap för crawl-tester"""
    xml = '''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    <url>
        <loc>http://localhost:8081/list</loc>
        <changefreq>daily</changefreq>
        <priority>1.0</priority>
    </url>'''
    
    for vehicle in VEHICLES:
        xml += f'''
    <url>
        <loc>http://localhost:8081/item/{vehicle['id']}</loc>
        <changefreq>weekly</changefreq>
        <priority>0.8</priority>
    </url>'''
    
    xml += '\n</urlset>'
    return Response(xml, mimetype="application/xml")

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8081))
    print(f"🚀 Starting Synthetic Static List Service on port {port}")
    print(f"📋 Available endpoints:")
    print(f"   GET /list         - Vehicle list with pagination")
    print(f"   GET /item/{{id}}    - Vehicle detail pages")
    print(f"   GET /robots.txt   - Robots.txt for crawler tests")
    print(f"   GET /sitemap.xml  - XML sitemap")
    
    app.run(host="0.0.0.0", port=port, debug=False)
