### How to Connect Python Flask to HTML and CSS
- Step 1. Move all HTML code into a folder named `templates`
- Step 2. all CSS and assets need to be moved to a folder named `static`

- To connect the HTML pages to app.py use the following template:
```
@app.route('/')
def index():
    return 'Index Page'
```

- To connect CSS to HTML add this link to `<head>`
```
 <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
```
