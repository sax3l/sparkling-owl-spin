from flask import Flask, send_from_directory, request, jsonify, Response
app = Flask(__name__, static_folder="static")

@app.route("/")
def index():
    html = """<!doctype html><html><head>
      <meta charset="utf-8"><title>Infinite Scroll</title>
      <script src="/static/scroll.js" defer></script>
      <style>#container{height:600px;overflow:auto;border:1px solid #ccc}
      .item{padding:8px;border-bottom:1px solid #eee}</style></head>
      <body><h1>Infinite List</h1><div id="container"><div id="list"></div></div></body></html>"""
    return Response(html, mimetype="text/html")

@app.route("/static/<path:path>")
def static_files(path):
    return send_from_directory("static", path)

@app.route("/api/items")
def api_items():
    # returnera 10 items per "page"
    page = int(request.args.get("page", 1))
    per = 10
    start = (page - 1)*per + 1
    end = start + per - 1
    items = [{"id": i, "href": f"/item/{i}"} for i in range(start, end + 1)]
    has_more = end < 50
    return jsonify({"items": items, "has_more": has_more})

@app.route("/item/<int:id>")
def item_detail(id):
    html = f"""<!doctype html><html><body>
    <dl><dt>Registreringsnummer</dt><dd>ABC{id:03d}</dd></dl>
    <div data-spec="modelYear">Modellår: 2020</div>
    <span id="wltp-co2">CO₂ (WLTP): 120,0 g/km</span></body></html>"""
    return Response(html, mimetype="text/html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8082)