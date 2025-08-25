"""
Syntetisk infinite scroll-sajt för E2E-tester

För nybörjare: Denna Flask-app simulerar en JavaScript-driven sajt med:
- Infinite scroll (AJAX-laddning av nytt innehåll)
- JSON API endpoints
- Dynamic content loading
- Browser automation test scenarios

Används för att testa headless browser capabilities och JavaScript rendering.
"""

from flask import Flask, Response, request, jsonify
import json
import time

app = Flask(__name__)

# Extended vehicle dataset för infinite scroll testing
INFINITE_VEHICLES = []

# Generate larger dataset
makes = ["Volvo", "BMW", "Audi", "Mercedes", "Toyota", "Volkswagen", "Ford", "Nissan", "Hyundai", "Kia"]
models = {
    "Volvo": ["XC60", "XC90", "V60", "V90", "S60", "S90"],
    "BMW": ["X3", "X5", "X1", "3 Series", "5 Series", "7 Series"],
    "Audi": ["Q5", "Q7", "A4", "A6", "A8", "Q3"],
    "Mercedes": ["GLC", "GLE", "C-Class", "E-Class", "S-Class", "GLA"],
    "Toyota": ["RAV4", "Highlander", "Camry", "Corolla", "Prius", "Yaris"],
    "Volkswagen": ["Tiguan", "Touareg", "Golf", "Passat", "Polo", "Arteon"],
    "Ford": ["Kuga", "Explorer", "Focus", "Mondeo", "Fiesta", "Mustang"],
    "Nissan": ["Qashqai", "X-Trail", "Juke", "Micra", "Note", "Leaf"],
    "Hyundai": ["Tucson", "Santa Fe", "i30", "i20", "IONIQ", "Kona"],
    "Kia": ["Sportage", "Sorento", "Ceed", "Rio", "Niro", "Stonic"]
}

# Generate 200 synthetic vehicles för extensive testing
import random
for i in range(1, 201):
    make = random.choice(makes)
    model = random.choice(models[make])
    year = random.randint(2018, 2024)
    co2 = round(random.uniform(80.0, 250.0), 1)
    reg = f"{''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=3))}{random.randint(100, 999)}"
    
    INFINITE_VEHICLES.append({
        "id": i,
        "reg": reg,
        "make": make,
        "model": model,
        "year": year,
        "co2": co2,
        "mileage": random.randint(5000, 150000),
        "fuel_type": random.choice(["Bensin", "Diesel", "Hybrid", "El"]),
        "price": random.randint(150000, 800000)
    })

@app.route("/")
def root():
    """Root-sida för hälsokontroll"""
    return Response("Synthetic Infinite Scroll Service OK", mimetype="text/plain")

@app.route("/scroll")
def scroll_page():
    """Huvudsida med infinite scroll funktionalitet"""
    html = """<!doctype html>
<html>
<head>
    <meta charset="utf-8">
    <title>Infinite Scroll Fordonssök</title>
    <style>
        body { 
            font-family: Arial, sans-serif; 
            margin: 0; 
            padding: 20px; 
            background-color: #f5f5f5; 
        }
        .header {
            background: #fff;
            padding: 20px;
            margin-bottom: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .vehicle-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }
        .vehicle-card {
            background: white;
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            transition: transform 0.2s;
        }
        .vehicle-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }
        .vehicle-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }
        .vehicle-reg {
            font-size: 18px;
            font-weight: bold;
            color: #0066cc;
        }
        .vehicle-year {
            background: #e7f3ff;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 12px;
            color: #0066cc;
        }
        .vehicle-make-model {
            font-size: 16px;
            margin-bottom: 10px;
            color: #333;
        }
        .vehicle-specs {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 8px;
            font-size: 14px;
            color: #666;
        }
        .spec-item {
            display: flex;
            justify-content: space-between;
        }
        .loading {
            text-align: center;
            padding: 40px;
            color: #666;
            font-size: 16px;
        }
        .end-message {
            text-align: center;
            padding: 40px;
            color: #999;
            font-style: italic;
        }
        .stats {
            position: fixed;
            top: 20px;
            right: 20px;
            background: rgba(0,0,0,0.8);
            color: white;
            padding: 10px 15px;
            border-radius: 5px;
            font-size: 12px;
        }
    </style>
</head>
<body>
    <div class="stats" id="stats">
        Laddade: <span id="loaded-count">0</span> / 200
    </div>
    
    <div class="header">
        <h1>🚗 Infinite Scroll Fordonssök</h1>
        <p>Scrolla ner för att ladda fler fordon automatiskt</p>
    </div>
    
    <div class="vehicle-grid" id="vehicle-container">
        <!-- Vehicles will be loaded here via JavaScript -->
    </div>
    
    <div class="loading" id="loading" style="display: none;">
        <div>⏳ Laddar fler fordon...</div>
    </div>
    
    <div class="end-message" id="end-message" style="display: none;">
        <div>✅ Alla fordon har laddats!</div>
    </div>

    <script>
        class InfiniteScrollLoader {
            constructor() {
                this.container = document.getElementById('vehicle-container');
                this.loading = document.getElementById('loading');
                this.endMessage = document.getElementById('end-message');
                this.statsCount = document.getElementById('loaded-count');
                
                this.page = 0;
                this.pageSize = 20;
                this.isLoading = false;
                this.hasMore = true;
                this.loadedCount = 0;
                
                this.init();
            }
            
            init() {
                // Initial load
                this.loadPage();
                
                // Setup scroll listener
                window.addEventListener('scroll', () => this.handleScroll());
                
                // Setup intersection observer för better performance
                this.setupIntersectionObserver();
            }
            
            setupIntersectionObserver() {
                const sentinel = document.createElement('div');
                sentinel.id = 'scroll-sentinel';
                sentinel.style.height = '10px';
                document.body.appendChild(sentinel);
                
                const observer = new IntersectionObserver((entries) => {
                    entries.forEach(entry => {
                        if (entry.isIntersecting && this.hasMore && !this.isLoading) {
                            this.loadPage();
                        }
                    });
                }, { rootMargin: '100px' });
                
                observer.observe(sentinel);
            }
            
            handleScroll() {
                const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
                const windowHeight = window.innerHeight;
                const documentHeight = document.documentElement.scrollHeight;
                
                // Load when user is near bottom
                if (scrollTop + windowHeight >= documentHeight - 200) {
                    if (this.hasMore && !this.isLoading) {
                        this.loadPage();
                    }
                }
            }
            
            async loadPage() {
                if (this.isLoading || !this.hasMore) return;
                
                this.isLoading = true;
                this.loading.style.display = 'block';
                
                try {
                    const response = await fetch(`/api/vehicles?page=${this.page}&size=${this.pageSize}`);
                    const data = await response.json();
                    
                    if (data.vehicles && data.vehicles.length > 0) {
                        this.renderVehicles(data.vehicles);
                        this.loadedCount += data.vehicles.length;
                        this.page++;
                        
                        if (data.vehicles.length < this.pageSize || !data.has_more) {
                            this.hasMore = false;
                            this.endMessage.style.display = 'block';
                        }
                    } else {
                        this.hasMore = false;
                        this.endMessage.style.display = 'block';
                    }
                    
                    this.updateStats();
                    
                } catch (error) {
                    console.error('Error loading vehicles:', error);
                } finally {
                    this.isLoading = false;
                    this.loading.style.display = 'none';
                }
            }
            
            renderVehicles(vehicles) {
                vehicles.forEach(vehicle => {
                    const card = this.createVehicleCard(vehicle);
                    this.container.appendChild(card);
                });
            }
            
            createVehicleCard(vehicle) {
                const card = document.createElement('div');
                card.className = 'vehicle-card';
                card.setAttribute('data-vehicle-id', vehicle.id);
                card.setAttribute('data-registration', vehicle.reg);
                
                card.innerHTML = `
                    <div class="vehicle-header">
                        <span class="vehicle-reg">${vehicle.reg}</span>
                        <span class="vehicle-year">${vehicle.year}</span>
                    </div>
                    <div class="vehicle-make-model">${vehicle.make} ${vehicle.model}</div>
                    <div class="vehicle-specs">
                        <div class="spec-item">
                            <span>CO₂:</span>
                            <span>${vehicle.co2} g/km</span>
                        </div>
                        <div class="spec-item">
                            <span>Bränslе:</span>
                            <span>${vehicle.fuel_type}</span>
                        </div>
                        <div class="spec-item">
                            <span>Miltal:</span>
                            <span>${vehicle.mileage.toLocaleString()} km</span>
                        </div>
                        <div class="spec-item">
                            <span>Pris:</span>
                            <span>${vehicle.price.toLocaleString()} kr</span>
                        </div>
                    </div>
                `;
                
                return card;
            }
            
            updateStats() {
                this.statsCount.textContent = this.loadedCount;
            }
        }
        
        // Initialize when DOM is ready
        document.addEventListener('DOMContentLoaded', () => {
            new InfiniteScrollLoader();
        });
    </script>
</body>
</html>"""
    
    return Response(html, mimetype="text/html")

@app.route("/api/vehicles")
def api_vehicles():
    """API endpoint för infinite scroll data loading"""
    page = int(request.args.get("page", 0))
    page_size = int(request.args.get("size", 20))
    
    # Simulate network delay för realistic testing
    time.sleep(0.2)
    
    start = page * page_size
    end = start + page_size
    
    page_vehicles = INFINITE_VEHICLES[start:end]
    has_more = end < len(INFINITE_VEHICLES)
    
    response_data = {
        "vehicles": page_vehicles,
        "page": page,
        "page_size": page_size,
        "total": len(INFINITE_VEHICLES),
        "has_more": has_more,
        "loaded": end if end < len(INFINITE_VEHICLES) else len(INFINITE_VEHICLES)
    }
    
    return jsonify(response_data)

@app.route("/api/vehicle/<int:vehicle_id>")
def api_vehicle_detail(vehicle_id):
    """API endpoint för individual vehicle data"""
    vehicle = next((v for v in INFINITE_VEHICLES if v["id"] == vehicle_id), None)
    
    if not vehicle:
        return jsonify({"error": "Vehicle not found"}), 404
    
    # Simulate network delay
    time.sleep(0.1)
    
    return jsonify(vehicle)

@app.route("/api/search")
def api_search():
    """API endpoint för search functionality"""
    query = request.args.get("q", "").lower()
    make_filter = request.args.get("make", "").lower()
    year_min = request.args.get("year_min", type=int)
    year_max = request.args.get("year_max", type=int)
    page = int(request.args.get("page", 0))
    page_size = int(request.args.get("size", 20))
    
    # Filter vehicles
    filtered_vehicles = INFINITE_VEHICLES
    
    if query:
        filtered_vehicles = [v for v in filtered_vehicles 
                           if query in v["reg"].lower() or 
                              query in v["make"].lower() or 
                              query in v["model"].lower()]
    
    if make_filter:
        filtered_vehicles = [v for v in filtered_vehicles 
                           if make_filter in v["make"].lower()]
    
    if year_min:
        filtered_vehicles = [v for v in filtered_vehicles if v["year"] >= year_min]
        
    if year_max:
        filtered_vehicles = [v for v in filtered_vehicles if v["year"] <= year_max]
    
    # Paginate results
    start = page * page_size
    end = start + page_size
    page_vehicles = filtered_vehicles[start:end]
    
    # Simulate network delay
    time.sleep(0.3)
    
    return jsonify({
        "vehicles": page_vehicles,
        "page": page,
        "page_size": page_size,
        "total": len(filtered_vehicles),
        "has_more": end < len(filtered_vehicles),
        "query": query,
        "filters": {
            "make": make_filter,
            "year_min": year_min,
            "year_max": year_max
        }
    })

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8082))
    print(f"🚀 Starting Synthetic Infinite Scroll Service on port {port}")
    print(f"📱 Available endpoints:")
    print(f"   GET /scroll               - Main infinite scroll page")
    print(f"   GET /api/vehicles         - Paginated vehicle API")
    print(f"   GET /api/vehicle/{{id}}     - Individual vehicle API")
    print(f"   GET /api/search           - Search API with filters")
    print(f"📊 Generated {len(INFINITE_VEHICLES)} synthetic vehicles")
    
    app.run(host="0.0.0.0", port=port, debug=False)
