"""
Syntetisk formulärbaserad sajt för E2E-tester

För nybörjare: Denna Flask-app simulerar en komplex webbapplikation med:
- Multi-step formulär
- Session management
- Form validation
- CSRF protection simulation
- JavaScript-enhanced forms
- File upload simulation

Används för att testa form submission, session handling och complex workflows.
"""

from flask import Flask, Response, request, session, redirect, url_for, jsonify
import json
import uuid
import time
from datetime import datetime
import re

app = Flask(__name__)
app.secret_key = "synthetic-test-key-not-for-production"

# Storage för submitted data (in-memory för testing)
SUBMISSIONS = {}
SESSION_DATA = {}

def generate_csrf_token():
    """Generate a fake CSRF token för testing"""
    if 'csrf_token' not in session:
        session['csrf_token'] = str(uuid.uuid4())
    return session['csrf_token']

def validate_registration_number(reg_num):
    """Validate Swedish registration number format"""
    if not reg_num:
        return False, "Registreringsnummer krävs"
    
    # Remove spaces and convert to uppercase
    reg_num = reg_num.replace(" ", "").upper()
    
    # Check format: 3 letters + 3 digits or 3 letters + 2 digits + 1 letter
    if re.match(r'^[A-Z]{3}\d{3}$', reg_num) or re.match(r'^[A-Z]{3}\d{2}[A-Z]$', reg_num):
        return True, reg_num
    
    return False, "Ogiltigt format. Använd format ABC123 eller ABC12D"

@app.route("/")
def root():
    """Root-sida för hälsokontroll"""
    return Response("Synthetic Form Flow Service OK", mimetype="text/plain")

@app.route("/form")
def form_start():
    """Startsida för formulärflödet"""
    # Initialize session
    session['form_step'] = 1
    session['form_data'] = {}
    session['submission_id'] = str(uuid.uuid4())
    csrf_token = generate_csrf_token()
    
    html = f"""<!doctype html>
<html>
<head>
    <meta charset="utf-8">
    <title>Fordonsregistrering - Steg 1/4</title>
    <style>
        body {{ 
            font-family: Arial, sans-serif; 
            margin: 0; 
            padding: 20px; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }}
        .container {{
            max-width: 600px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        .header {{
            background: #4f46e5;
            color: white;
            padding: 30px;
            text-align: center;
        }}
        .step-indicator {{
            display: flex;
            justify-content: center;
            margin: 20px 0;
        }}
        .step {{
            width: 40px;
            height: 40px;
            border-radius: 50%;
            background: #e5e7eb;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 10px;
            font-weight: bold;
        }}
        .step.active {{
            background: #4f46e5;
            color: white;
        }}
        .step.completed {{
            background: #10b981;
            color: white;
        }}
        .form-content {{
            padding: 40px;
        }}
        .form-group {{
            margin-bottom: 25px;
        }}
        .form-label {{
            display: block;
            margin-bottom: 8px;
            font-weight: bold;
            color: #374151;
        }}
        .form-input {{
            width: 100%;
            padding: 12px 16px;
            border: 2px solid #e5e7eb;
            border-radius: 8px;
            font-size: 16px;
            transition: border-color 0.3s;
        }}
        .form-input:focus {{
            outline: none;
            border-color: #4f46e5;
        }}
        .form-button {{
            background: #4f46e5;
            color: white;
            padding: 12px 30px;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            cursor: pointer;
            transition: background-color 0.3s;
        }}
        .form-button:hover {{
            background: #4338ca;
        }}
        .form-button:disabled {{
            background: #9ca3af;
            cursor: not-allowed;
        }}
        .help-text {{
            font-size: 14px;
            color: #6b7280;
            margin-top: 5px;
        }}
        .error {{
            color: #dc2626;
            font-size: 14px;
            margin-top: 5px;
        }}
        .progress-bar {{
            width: 100%;
            height: 6px;
            background: #e5e7eb;
            margin-bottom: 30px;
        }}
        .progress-fill {{
            height: 100%;
            background: #4f46e5;
            width: 25%;
            transition: width 0.3s;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚗 Fordonsregistrering</h1>
            <p>Registrera ditt fordon i vårt system</p>
        </div>
        
        <div class="progress-bar">
            <div class="progress-fill" style="width: 25%;"></div>
        </div>
        
        <div class="step-indicator">
            <div class="step active">1</div>
            <div class="step">2</div>
            <div class="step">3</div>
            <div class="step">4</div>
        </div>
        
        <div class="form-content">
            <h2>Steg 1: Grundinformation</h2>
            <form id="step1-form" method="post" action="/form/step1">
                <input type="hidden" name="csrf_token" value="{csrf_token}">
                
                <div class="form-group">
                    <label class="form-label" for="registration_number">Registreringsnummer *</label>
                    <input type="text" 
                           id="registration_number" 
                           name="registration_number" 
                           class="form-input" 
                           placeholder="ABC123"
                           maxlength="6"
                           pattern="[A-Za-z]{{3}}[0-9]{{2,3}}[A-Za-z]?"
                           required>
                    <div class="help-text">Ange fordonets registreringsnummer (t.ex. ABC123)</div>
                </div>
                
                <div class="form-group">
                    <label class="form-label" for="owner_name">Ägarens namn *</label>
                    <input type="text" 
                           id="owner_name" 
                           name="owner_name" 
                           class="form-input" 
                           placeholder="För- och efternamn"
                           required>
                </div>
                
                <div class="form-group">
                    <label class="form-label" for="owner_ssn">Personnummer *</label>
                    <input type="text" 
                           id="owner_ssn" 
                           name="owner_ssn" 
                           class="form-input" 
                           placeholder="YYYYMMDD-XXXX"
                           pattern="[0-9]{{8}}-?[0-9]{{4}}"
                           required>
                    <div class="help-text">Format: YYYYMMDD-XXXX</div>
                </div>
                
                <button type="submit" class="form-button">Nästa steg →</button>
            </form>
        </div>
    </div>
    
    <script>
        // Form enhancement
        document.getElementById('step1-form').addEventListener('submit', function(e) {{
            const regNum = document.getElementById('registration_number').value;
            const ownerName = document.getElementById('owner_name').value;
            const ownerSsn = document.getElementById('owner_ssn').value;
            
            // Basic client-side validation
            if (!regNum || !ownerName || !ownerSsn) {{
                e.preventDefault();
                alert('Alla obligatoriska fält måste fyllas i');
                return;
            }}
            
            // Disable submit button to prevent double submission
            const submitBtn = this.querySelector('button[type="submit"]');
            submitBtn.disabled = true;
            submitBtn.textContent = 'Behandlar...';
        }});
        
        // Auto-format registration number
        document.getElementById('registration_number').addEventListener('input', function(e) {{
            let value = e.target.value.toUpperCase().replace(/[^A-Z0-9]/g, '');
            if (value.length > 6) value = value.substring(0, 6);
            e.target.value = value;
        }});
        
        // Auto-format SSN
        document.getElementById('owner_ssn').addEventListener('input', function(e) {{
            let value = e.target.value.replace(/[^0-9-]/g, '');
            if (value.length === 8 && !value.includes('-')) {{
                value = value + '-';
            }}
            if (value.length > 13) value = value.substring(0, 13);
            e.target.value = value;
        }});
    </script>
</body>
</html>"""
    
    return Response(html, mimetype="text/html")

@app.route("/form/step1", methods=["POST"])
def form_step1():
    """Process step 1 and show step 2"""
    # Validate CSRF token
    if request.form.get('csrf_token') != session.get('csrf_token'):
        return Response("CSRF token mismatch", status=403)
    
    # Validate registration number
    reg_num = request.form.get('registration_number', '').strip()
    is_valid, reg_result = validate_registration_number(reg_num)
    
    if not is_valid:
        return Response(f"Error: {reg_result}", status=400)
    
    # Store step 1 data
    session['form_data'] = {
        'registration_number': reg_result,
        'owner_name': request.form.get('owner_name', '').strip(),
        'owner_ssn': request.form.get('owner_ssn', '').strip()
    }
    session['form_step'] = 2
    
    csrf_token = generate_csrf_token()
    
    html = f"""<!doctype html>
<html>
<head>
    <meta charset="utf-8">
    <title>Fordonsregistrering - Steg 2/4</title>
    <style>
        body {{ 
            font-family: Arial, sans-serif; 
            margin: 0; 
            padding: 20px; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }}
        .container {{
            max-width: 600px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        .header {{
            background: #4f46e5;
            color: white;
            padding: 30px;
            text-align: center;
        }}
        .step-indicator {{
            display: flex;
            justify-content: center;
            margin: 20px 0;
        }}
        .step {{
            width: 40px;
            height: 40px;
            border-radius: 50%;
            background: #e5e7eb;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 10px;
            font-weight: bold;
        }}
        .step.active {{
            background: #4f46e5;
            color: white;
        }}
        .step.completed {{
            background: #10b981;
            color: white;
        }}
        .form-content {{
            padding: 40px;
        }}
        .form-group {{
            margin-bottom: 25px;
        }}
        .form-label {{
            display: block;
            margin-bottom: 8px;
            font-weight: bold;
            color: #374151;
        }}
        .form-input, .form-select {{
            width: 100%;
            padding: 12px 16px;
            border: 2px solid #e5e7eb;
            border-radius: 8px;
            font-size: 16px;
            transition: border-color 0.3s;
        }}
        .form-input:focus, .form-select:focus {{
            outline: none;
            border-color: #4f46e5;
        }}
        .form-button {{
            background: #4f46e5;
            color: white;
            padding: 12px 30px;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            cursor: pointer;
            transition: background-color 0.3s;
            margin-right: 10px;
        }}
        .form-button:hover {{
            background: #4338ca;
        }}
        .form-button.secondary {{
            background: #6b7280;
        }}
        .form-button.secondary:hover {{
            background: #4b5563;
        }}
        .progress-bar {{
            width: 100%;
            height: 6px;
            background: #e5e7eb;
            margin-bottom: 30px;
        }}
        .progress-fill {{
            height: 100%;
            background: #4f46e5;
            width: 50%;
            transition: width 0.3s;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚗 Fordonsregistrering</h1>
            <p>Registrerat fordon: <strong>{session['form_data']['registration_number']}</strong></p>
        </div>
        
        <div class="progress-bar">
            <div class="progress-fill" style="width: 50%;"></div>
        </div>
        
        <div class="step-indicator">
            <div class="step completed">✓</div>
            <div class="step active">2</div>
            <div class="step">3</div>
            <div class="step">4</div>
        </div>
        
        <div class="form-content">
            <h2>Steg 2: Fordonsinformation</h2>
            <form id="step2-form" method="post" action="/form/step2">
                <input type="hidden" name="csrf_token" value="{csrf_token}">
                
                <div class="form-group">
                    <label class="form-label" for="make">Märke *</label>
                    <select id="make" name="make" class="form-select" required>
                        <option value="">Välj märke</option>
                        <option value="Volvo">Volvo</option>
                        <option value="BMW">BMW</option>
                        <option value="Audi">Audi</option>
                        <option value="Mercedes">Mercedes-Benz</option>
                        <option value="Toyota">Toyota</option>
                        <option value="Volkswagen">Volkswagen</option>
                        <option value="Ford">Ford</option>
                        <option value="Nissan">Nissan</option>
                        <option value="Hyundai">Hyundai</option>
                        <option value="Kia">Kia</option>
                        <option value="Other">Annat märke</option>
                    </select>
                </div>
                
                <div class="form-group">
                    <label class="form-label" for="model">Modell *</label>
                    <input type="text" 
                           id="model" 
                           name="model" 
                           class="form-input" 
                           placeholder="T.ex. XC60, 3 Series, A4"
                           required>
                </div>
                
                <div class="form-group">
                    <label class="form-label" for="model_year">Modellår *</label>
                    <select id="model_year" name="model_year" class="form-select" required>
                        <option value="">Välj år</option>
                    </select>
                </div>
                
                <div class="form-group">
                    <label class="form-label" for="fuel_type">Bränsletyp *</label>
                    <select id="fuel_type" name="fuel_type" class="form-select" required>
                        <option value="">Välj bränsletyp</option>
                        <option value="Bensin">Bensin</option>
                        <option value="Diesel">Diesel</option>
                        <option value="Hybrid">Hybrid</option>
                        <option value="Plugin-Hybrid">Plugin-Hybrid</option>
                        <option value="El">El</option>
                        <option value="Etanol">Etanol</option>
                        <option value="Gas">Gas</option>
                    </select>
                </div>
                
                <div class="form-group">
                    <label class="form-label" for="mileage">Aktuellt mätarställning (km)</label>
                    <input type="number" 
                           id="mileage" 
                           name="mileage" 
                           class="form-input" 
                           placeholder="120000"
                           min="0"
                           max="1000000">
                </div>
                
                <a href="/form" class="form-button secondary">← Föregående</a>
                <button type="submit" class="form-button">Nästa steg →</button>
            </form>
        </div>
    </div>
    
    <script>
        // Populate year dropdown
        const yearSelect = document.getElementById('model_year');
        const currentYear = new Date().getFullYear();
        for (let year = currentYear; year >= 1980; year--) {{
            const option = document.createElement('option');
            option.value = year;
            option.textContent = year;
            yearSelect.appendChild(option);
        }}
        
        // Form submission handling
        document.getElementById('step2-form').addEventListener('submit', function(e) {{
            const submitBtn = this.querySelector('button[type="submit"]');
            submitBtn.disabled = true;
            submitBtn.textContent = 'Behandlar...';
        }});
    </script>
</body>
</html>"""
    
    return Response(html, mimetype="text/html")

@app.route("/form/step2", methods=["POST"])
def form_step2():
    """Process step 2 and show step 3"""
    # Validate CSRF token
    if request.form.get('csrf_token') != session.get('csrf_token'):
        return Response("CSRF token mismatch", status=403)
    
    # Update form data
    session['form_data'].update({
        'make': request.form.get('make', '').strip(),
        'model': request.form.get('model', '').strip(),
        'model_year': request.form.get('model_year', '').strip(),
        'fuel_type': request.form.get('fuel_type', '').strip(),
        'mileage': request.form.get('mileage', '').strip()
    })
    session['form_step'] = 3
    
    csrf_token = generate_csrf_token()
    
    html = f"""<!doctype html>
<html>
<head>
    <meta charset="utf-8">
    <title>Fordonsregistrering - Steg 3/4</title>
    <style>
        body {{ 
            font-family: Arial, sans-serif; 
            margin: 0; 
            padding: 20px; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }}
        .container {{
            max-width: 600px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        .header {{
            background: #4f46e5;
            color: white;
            padding: 30px;
            text-align: center;
        }}
        .step-indicator {{
            display: flex;
            justify-content: center;
            margin: 20px 0;
        }}
        .step {{
            width: 40px;
            height: 40px;
            border-radius: 50%;
            background: #e5e7eb;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 10px;
            font-weight: bold;
        }}
        .step.active {{
            background: #4f46e5;
            color: white;
        }}
        .step.completed {{
            background: #10b981;
            color: white;
        }}
        .form-content {{
            padding: 40px;
        }}
        .form-group {{
            margin-bottom: 25px;
        }}
        .form-label {{
            display: block;
            margin-bottom: 8px;
            font-weight: bold;
            color: #374151;
        }}
        .form-input, .form-textarea, .form-checkbox {{
            width: 100%;
            padding: 12px 16px;
            border: 2px solid #e5e7eb;
            border-radius: 8px;
            font-size: 16px;
            transition: border-color 0.3s;
        }}
        .form-textarea {{
            min-height: 100px;
            resize: vertical;
        }}
        .form-input:focus, .form-textarea:focus {{
            outline: none;
            border-color: #4f46e5;
        }}
        .form-button {{
            background: #4f46e5;
            color: white;
            padding: 12px 30px;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            cursor: pointer;
            transition: background-color 0.3s;
            margin-right: 10px;
        }}
        .form-button:hover {{
            background: #4338ca;
        }}
        .form-button.secondary {{
            background: #6b7280;
        }}
        .form-button.secondary:hover {{
            background: #4b5563;
        }}
        .checkbox-group {{
            display: flex;
            align-items: center;
            margin-bottom: 15px;
        }}
        .checkbox-group input[type="checkbox"] {{
            width: auto;
            margin-right: 10px;
        }}
        .progress-bar {{
            width: 100%;
            height: 6px;
            background: #e5e7eb;
            margin-bottom: 30px;
        }}
        .progress-fill {{
            height: 100%;
            background: #4f46e5;
            width: 75%;
            transition: width 0.3s;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚗 Fordonsregistrering</h1>
            <p>{session['form_data']['make']} {session['form_data']['model']} ({session['form_data']['model_year']})</p>
        </div>
        
        <div class="progress-bar">
            <div class="progress-fill" style="width: 75%;"></div>
        </div>
        
        <div class="step-indicator">
            <div class="step completed">✓</div>
            <div class="step completed">✓</div>
            <div class="step active">3</div>
            <div class="step">4</div>
        </div>
        
        <div class="form-content">
            <h2>Steg 3: Kontaktinformation & Samtycke</h2>
            <form id="step3-form" method="post" action="/form/step3">
                <input type="hidden" name="csrf_token" value="{csrf_token}">
                
                <div class="form-group">
                    <label class="form-label" for="email">E-postadress *</label>
                    <input type="email" 
                           id="email" 
                           name="email" 
                           class="form-input" 
                           placeholder="din@email.com"
                           required>
                </div>
                
                <div class="form-group">
                    <label class="form-label" for="phone">Telefonnummer</label>
                    <input type="tel" 
                           id="phone" 
                           name="phone" 
                           class="form-input" 
                           placeholder="070-123 45 67">
                </div>
                
                <div class="form-group">
                    <label class="form-label" for="address">Adress *</label>
                    <input type="text" 
                           id="address" 
                           name="address" 
                           class="form-input" 
                           placeholder="Gatuadress"
                           required>
                </div>
                
                <div class="form-group">
                    <label class="form-label" for="postal_code">Postnummer *</label>
                    <input type="text" 
                           id="postal_code" 
                           name="postal_code" 
                           class="form-input" 
                           placeholder="12345"
                           pattern="[0-9]{{5}}"
                           required>
                </div>
                
                <div class="form-group">
                    <label class="form-label" for="city">Ort *</label>
                    <input type="text" 
                           id="city" 
                           name="city" 
                           class="form-input" 
                           placeholder="Stockholm"
                           required>
                </div>
                
                <div class="form-group">
                    <label class="form-label" for="notes">Kommentarer</label>
                    <textarea id="notes" 
                              name="notes" 
                              class="form-textarea" 
                              placeholder="Eventuella kommentarer eller anmärkningar..."></textarea>
                </div>
                
                <div class="form-group">
                    <div class="checkbox-group">
                        <input type="checkbox" 
                               id="terms_accepted" 
                               name="terms_accepted" 
                               value="1" 
                               required>
                        <label for="terms_accepted">Jag accepterar användarvillkoren *</label>
                    </div>
                    
                    <div class="checkbox-group">
                        <input type="checkbox" 
                               id="privacy_accepted" 
                               name="privacy_accepted" 
                               value="1" 
                               required>
                        <label for="privacy_accepted">Jag accepterar hantering av personuppgifter *</label>
                    </div>
                    
                    <div class="checkbox-group">
                        <input type="checkbox" 
                               id="newsletter" 
                               name="newsletter" 
                               value="1">
                        <label for="newsletter">Jag vill prenumerera på nyhetsbrev</label>
                    </div>
                </div>
                
                <a href="/form/step1" class="form-button secondary">← Föregående</a>
                <button type="submit" class="form-button">Granska & Skicka →</button>
            </form>
        </div>
    </div>
    
    <script>
        // Phone number formatting
        document.getElementById('phone').addEventListener('input', function(e) {{
            let value = e.target.value.replace(/[^0-9]/g, '');
            if (value.length >= 3) {{
                value = value.substring(0, 3) + '-' + value.substring(3);
            }}
            if (value.length >= 7) {{
                value = value.substring(0, 7) + ' ' + value.substring(7);
            }}
            if (value.length >= 10) {{
                value = value.substring(0, 10) + ' ' + value.substring(10);
            }}
            if (value.length > 13) value = value.substring(0, 13);
            e.target.value = value;
        }});
        
        // Postal code validation
        document.getElementById('postal_code').addEventListener('input', function(e) {{
            let value = e.target.value.replace(/[^0-9]/g, '');
            if (value.length > 5) value = value.substring(0, 5);
            e.target.value = value;
        }});
        
        // Form submission
        document.getElementById('step3-form').addEventListener('submit', function(e) {{
            const submitBtn = this.querySelector('button[type="submit"]');
            submitBtn.disabled = true;
            submitBtn.textContent = 'Behandlar...';
        }});
    </script>
</body>
</html>"""
    
    return Response(html, mimetype="text/html")

@app.route("/form/step3", methods=["POST"])
def form_step3():
    """Process step 3 and show confirmation"""
    # Validate CSRF token
    if request.form.get('csrf_token') != session.get('csrf_token'):
        return Response("CSRF token mismatch", status=403)
    
    # Update form data
    session['form_data'].update({
        'email': request.form.get('email', '').strip(),
        'phone': request.form.get('phone', '').strip(),
        'address': request.form.get('address', '').strip(),
        'postal_code': request.form.get('postal_code', '').strip(),
        'city': request.form.get('city', '').strip(),
        'notes': request.form.get('notes', '').strip(),
        'terms_accepted': bool(request.form.get('terms_accepted')),
        'privacy_accepted': bool(request.form.get('privacy_accepted')),
        'newsletter': bool(request.form.get('newsletter'))
    })
    session['form_step'] = 4
    
    # Store submission (simulate database save)
    submission_id = session['submission_id']
    SUBMISSIONS[submission_id] = {
        'id': submission_id,
        'data': session['form_data'].copy(),
        'timestamp': datetime.now().isoformat(),
        'status': 'pending'
    }
    
    csrf_token = generate_csrf_token()
    
    html = f"""<!doctype html>
<html>
<head>
    <meta charset="utf-8">
    <title>Fordonsregistrering - Bekräftelse</title>
    <style>
        body {{ 
            font-family: Arial, sans-serif; 
            margin: 0; 
            padding: 20px; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }}
        .container {{
            max-width: 600px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        .header {{
            background: #10b981;
            color: white;
            padding: 30px;
            text-align: center;
        }}
        .step-indicator {{
            display: flex;
            justify-content: center;
            margin: 20px 0;
        }}
        .step {{
            width: 40px;
            height: 40px;
            border-radius: 50%;
            background: #10b981;
            color: white;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 10px;
            font-weight: bold;
        }}
        .form-content {{
            padding: 40px;
        }}
        .summary-section {{
            background: #f9fafb;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 20px;
        }}
        .summary-title {{
            font-weight: bold;
            margin-bottom: 15px;
            color: #374151;
            border-bottom: 2px solid #e5e7eb;
            padding-bottom: 5px;
        }}
        .summary-row {{
            display: flex;
            justify-content: space-between;
            margin-bottom: 8px;
            padding: 5px 0;
        }}
        .summary-label {{
            font-weight: 500;
            color: #6b7280;
        }}
        .summary-value {{
            color: #374151;
        }}
        .form-button {{
            background: #10b981;
            color: white;
            padding: 12px 30px;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            cursor: pointer;
            transition: background-color 0.3s;
            margin-right: 10px;
        }}
        .form-button:hover {{
            background: #059669;
        }}
        .form-button.secondary {{
            background: #6b7280;
        }}
        .form-button.secondary:hover {{
            background: #4b5563;
        }}
        .success-icon {{
            font-size: 48px;
            text-align: center;
            margin-bottom: 20px;
        }}
        .submission-id {{
            background: #eff6ff;
            border: 2px solid #3b82f6;
            border-radius: 8px;
            padding: 15px;
            text-align: center;
            margin: 20px 0;
        }}
        .progress-bar {{
            width: 100%;
            height: 6px;
            background: #e5e7eb;
            margin-bottom: 30px;
        }}
        .progress-fill {{
            height: 100%;
            background: #10b981;
            width: 100%;
            transition: width 0.3s;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="success-icon">✅</div>
            <h1>Registrering Slutförd!</h1>
            <p>Ditt fordon har registrerats i vårt system</p>
        </div>
        
        <div class="progress-bar">
            <div class="progress-fill"></div>
        </div>
        
        <div class="step-indicator">
            <div class="step">✓</div>
            <div class="step">✓</div>
            <div class="step">✓</div>
            <div class="step">✓</div>
        </div>
        
        <div class="form-content">
            <div class="submission-id">
                <strong>Registreringsnummer:</strong> {submission_id}
            </div>
            
            <div class="summary-section">
                <div class="summary-title">Fordonsinformation</div>
                <div class="summary-row">
                    <span class="summary-label">Registreringsnummer:</span>
                    <span class="summary-value">{session['form_data']['registration_number']}</span>
                </div>
                <div class="summary-row">
                    <span class="summary-label">Märke & Modell:</span>
                    <span class="summary-value">{session['form_data']['make']} {session['form_data']['model']}</span>
                </div>
                <div class="summary-row">
                    <span class="summary-label">Modellår:</span>
                    <span class="summary-value">{session['form_data']['model_year']}</span>
                </div>
                <div class="summary-row">
                    <span class="summary-label">Bränsletyp:</span>
                    <span class="summary-value">{session['form_data']['fuel_type']}</span>
                </div>
            </div>
            
            <div class="summary-section">
                <div class="summary-title">Ägarinformation</div>
                <div class="summary-row">
                    <span class="summary-label">Namn:</span>
                    <span class="summary-value">{session['form_data']['owner_name']}</span>
                </div>
                <div class="summary-row">
                    <span class="summary-label">E-post:</span>
                    <span class="summary-value">{session['form_data']['email']}</span>
                </div>
                <div class="summary-row">
                    <span class="summary-label">Adress:</span>
                    <span class="summary-value">{session['form_data']['address']}, {session['form_data']['postal_code']} {session['form_data']['city']}</span>
                </div>
            </div>
            
            <form method="post" action="/form/complete">
                <input type="hidden" name="csrf_token" value="{csrf_token}">
                <input type="hidden" name="submission_id" value="{submission_id}">
                
                <button type="submit" class="form-button">Slutför Registrering</button>
                <a href="/form" class="form-button secondary">Ny Registrering</a>
            </form>
        </div>
    </div>
</body>
</html>"""
    
    return Response(html, mimetype="text/html")

@app.route("/form/complete", methods=["POST"])
def form_complete():
    """Final submission completion"""
    submission_id = request.form.get('submission_id')
    
    if submission_id in SUBMISSIONS:
        SUBMISSIONS[submission_id]['status'] = 'completed'
        SUBMISSIONS[submission_id]['completed_at'] = datetime.now().isoformat()
    
    # Clear session
    session.clear()
    
    html = """<!doctype html>
<html>
<head>
    <meta charset="utf-8">
    <title>Tack för din registrering!</title>
    <style>
        body { 
            font-family: Arial, sans-serif; 
            margin: 0; 
            padding: 20px; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .container {
            max-width: 500px;
            background: white;
            border-radius: 12px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
            padding: 60px 40px;
            text-align: center;
        }
        .success-icon {
            font-size: 72px;
            margin-bottom: 30px;
        }
        h1 {
            color: #10b981;
            margin-bottom: 20px;
        }
        p {
            color: #6b7280;
            line-height: 1.6;
            margin-bottom: 30px;
        }
        .form-button {
            background: #4f46e5;
            color: white;
            padding: 12px 30px;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            cursor: pointer;
            text-decoration: none;
            display: inline-block;
            transition: background-color 0.3s;
        }
        .form-button:hover {
            background: #4338ca;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="success-icon">🎉</div>
        <h1>Tack för din registrering!</h1>
        <p>Din fordonsregistrering har slutförts framgångsrikt. Du kommer att få en bekräftelse via e-post inom kort.</p>
        <a href="/form" class="form-button">Registrera Nytt Fordon</a>
    </div>
</body>
</html>"""
    
    return Response(html, mimetype="text/html")

@app.route("/api/submissions")
def api_submissions():
    """API endpoint för att hämta alla submissions (för testning)"""
    return jsonify({
        "submissions": list(SUBMISSIONS.values()),
        "total": len(SUBMISSIONS)
    })

@app.route("/api/submission/<submission_id>")
def api_submission_detail(submission_id):
    """API endpoint för individual submission"""
    if submission_id not in SUBMISSIONS:
        return jsonify({"error": "Submission not found"}), 404
    
    return jsonify(SUBMISSIONS[submission_id])

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8083))
    print(f"🚀 Starting Synthetic Form Flow Service on port {port}")
    print(f"📝 Available endpoints:")
    print(f"   GET /form                      - Multi-step form start")
    print(f"   POST /form/step1               - Process step 1")
    print(f"   POST /form/step2               - Process step 2") 
    print(f"   POST /form/step3               - Process step 3")
    print(f"   POST /form/complete            - Complete submission")
    print(f"   GET /api/submissions           - List all submissions")
    print(f"   GET /api/submission/{{id}}      - Individual submission")
    
    app.run(host="0.0.0.0", port=port, debug=False)
