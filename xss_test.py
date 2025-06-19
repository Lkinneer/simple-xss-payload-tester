from flask import Flask, request, render_template_string, redirect, url_for

app = Flask(__name__)
inject = ''''''


@app.route("/test_bed/html_element")
def test_bed_html_element():
   return f'''<div>{inject}</div>'''

@app.route("/test_bed/js_html_element")
def test_bed_js_html_element():
   return '''
       <div id='elmtId'></div>
       <script>
       window.onload = () => {{
           const payload = decodeURIComponent(window.location.hash.substr(1));
           document.getElementById('elmtId').innerHTML = payload;
       }}
       </script>'''

@app.route("/test_bed/html_attribute_value_double_quoted")
def test_bed_html_attribute_value_double_quoted():
   return f'''<div class="{inject}">content</div>'''

@app.route("/test_bed/html_attribute_value_single_quoted")
def test_bed_html_attribute_value_single_quoted():
   return f'''<div class='{inject}'>content</div>'''

@app.route("/test_bed//html_attribute_value_not_quoted")
def test_bed_html_attribute_value_not_quoted():
   return f'''<div class={inject}>content</div>'''

@app.route("/test_bed/html_attribute_name")
def test_bed_html_attribute_name():
   return f'''<div {inject}='class'>content</div>'''

@app.route("/test_bed/js_script_element")
def test_bed_js_script_element():
   return f'''
       <script id='elmtId'></script>
       <script>
       const payload = decodeURIComponent(window.location.hash.substr(1));
       document.getElementById('elmtId').innerHTML = payload;
       </script>'''

@app.route("/test_bed/script_element")
def test_bed_script_element():
   return f'''<script>{inject}</script>'''


@app.route("/test_bed/script_double_quoted")
def test_bed_script_double_quoted():
   return f'''<script>var hello="{inject}";</script>'''

@app.route("/test_bed/script_single_quoted")
def test_bed_script_single_quoted():
   return f'''<script>var hello='{inject}';</script>'''

@app.route("/test_bed/iframe_src")
def test_bed_iframe_src():
   return f'''<iframe src="{inject}"></iframe>'''

@app.route("/test_bed/js_iframe_src")
def test_bed_js_iframe_src():
   return f'''
       <iframe id='elmtId'></iframe>
       <script>
       const payload = decodeURIComponent(window.location.hash.substr(1));
       document.getElementById('elmtId').setAttribute('src', payload);
       </script>'''

@app.route("/test_bed/html_comment")
def test_bed_html_comment():
   return f'''<!-- {inject} -->'''

@app.route("/test_bed/textarea_element")
def test_bed_textarea_element():
   return f'''<textarea>{inject}</textarea>'''

@app.route("/")
def serve_js():
    js_code = """
    // JavaScript served at root
    fetch('/record_success', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: 'value=' + encodeURIComponent(window.location.href)
    });
    """
    return app.response_class(js_code, mimetype='application/javascript')

# Store submitted values in a global list
submitted_values = []

@app.route("/record_success", methods=["POST"])
def record_success():
    value = request.form.get('value')
    if value is not None:
        submitted_values.append(value)
    return f"Array contents: {submitted_values}"

@app.route("/clear_success", methods=["POST"])
def clear_success():
    submitted_values.clear()
    return '<script>window.location.href = "/success_table";</script>'

@app.route("/success_table")
def success_table():
    def extract_path_segment(url):
        try:
            return url.split("/")[-1] if url else ""
        except Exception:
            return url
    table_rows = ''.join(f'<tr><td>{extract_path_segment(v)}</td></tr>' for v in submitted_values)
    html = f'''
    <html>
    <head>
        <title>Submitted Successes</title>
        <style>
            body {{ text-align: center; }}
            table {{ margin-left: auto; margin-right: auto; }}
            form {{ margin-top: 20px; }}
        </style>
        <script>
            let lastCount = {len(submitted_values)};
            setInterval(function() {{
                fetch('/success_count').then(r => r.json()).then(data => {{
                    if (data.count > lastCount) {{
                        window.location.reload();
                    }}
                    lastCount = data.count;
                }});
            }}, 2000);
        </script>
    </head>
    <body>
        <h2>Submitted Successes</h2>
        <table border="1">
            <tr><th>Test case XSS was triggered in</th></tr>
            {table_rows}
        </table>
        <form method="post" action="/clear_success">
            <button type="submit">Clear Results</button>
        </form>
    </body>
    </html>
    '''
    return html

@app.route("/success_count")
def success_count():
    return {"count": len(submitted_values)}

@app.route("/begin_test", methods=["GET", "POST"])
def begin_test():
    global inject
    message = ""
    refresh_iframes = False
    if request.method == "POST":
        new_inject = request.form.get("inject_value")
        if new_inject is not None:
            inject = new_inject
            message = "Inject value updated!"
            refresh_iframes = True
        # Redirect to GET after POST to prevent form resubmission dialog
        return redirect(url_for('begin_test'))
    test_bed_paths = [
        '/test_bed/html_element',
        '/test_bed/js_html_element',
        '/test_bed/html_attribute_value_double_quoted',
        '/test_bed/html_attribute_value_single_quoted',
        '/test_bed//html_attribute_value_not_quoted',
        '/test_bed/html_attribute_name',
        '/test_bed/js_script_element',
        '/test_bed/script_element',
        '/test_bed/script_double_quoted',
        '/test_bed/script_single_quoted',
        '/test_bed/iframe_src',
        '/test_bed/js_iframe_src',
        '/test_bed/html_comment',
        '/test_bed/textarea_element',
    ]
    iframes = ''.join(f'<iframe src="{path}" width="600" height="100" class="testbed-frame"></iframe><br>' for path in test_bed_paths)
    html = f'''
    <html>
    <head>
        <title>Begin Test</title>
        <style>
            .container {{ display: flex; justify-content: center; align-items: flex-start; }}
            .left {{ flex: 2; }}
            .right {{ flex: 1; margin-left: 40px; }}
            .description {{ max-width: 700px; margin: 0 auto 20px auto; text-align: left; font-size: 1.1em; background: #f8f8f8; padding: 16px; border-radius: 8px; border: 1px solid #ddd; }}
            .centered-heading {{ text-align: center; margin-top: 0; }}
            .centered-content {{ display: flex; flex-direction: column; align-items: center; }}
            .inject-form-wrapper {{ width: 100%; display: flex; flex-direction: column; align-items: center; margin-bottom: 20px; }}
        </style>
        <script>
        function refreshIframes() {{
            var frames = document.getElementsByClassName('testbed-frame');
            for (var i = 0; i < frames.length; i++) {{
                frames[i].contentWindow.location.reload();
            }}
        }}
        </script>
    </head>
    <body>
        <div class="container">
            <div class="left">
                <h2 class="centered-heading">A Slightly Jank XSS Testing Environment</h2>
                <div class="description">
                    <strong>Instructions:</strong><br>
                    Enter your XSS payloads in the <b>Set inject value</b> text box. The value you provide will be dynamically included in the responses of the test bed pages which are rendered in iframes below. If your payload successfully loads a script from the <code>/</code> endpoint, the event will be recorded and displayed in the <b>Submitted Successes</b> panel on the right. Use this interface to test and validate XSS payload effectiveness in a controlled environment.<br><br>
                    An example payload could be: &lt;script src=&quot;/&quot;&gt;&lt;/script&gt;<br><br>
                    Code for test cases comes from this excelent blog post on polyglot XSS.  <a href="https://blog.ostorlab.co/polyglot-xss.html" target="_blank">https://blog.ostorlab.co/polyglot-xss.html</a>.
                </div>
                <div class="centered-content">
                    <div class="inject-form-wrapper">
                        <form method="post">
                            <label for="inject_value">Set inject value:</label>
                            <input type="text" id="inject_value" name="inject_value" style="width:400px;">
                            <button type="submit">Update</button>
                        </form>
                        <div style="color:green;">{message}</div>
                    </div>
                    <div style="width: 100%; display: flex; flex-direction: column; align-items: center;">
                        {iframes}
                        {'<script>refreshIframes();</script>' if refresh_iframes else ''}
                    </div>
                </div>
            </div>
            <div class="right">
                <iframe src="/success_table" width="400" height="800" style="border:1px solid #ccc;"></iframe>
            </div>
        </div>
    </body>
    </html>
    '''
    return html

# Run the app
if __name__ == '__main__':
    app.run(debug=True)