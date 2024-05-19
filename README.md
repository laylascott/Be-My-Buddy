### How to Connect Python Flask to HTML and CSS
 1. Move all HTML code into a folder named `templates`
 2. All CSS and assets (like images) need to be moved to a folder named `static`
 3. To connect CSS to HTML add this link to the `<head>` tag of all HTML files.
    ```
    <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
    ```

### Database Set Up
Before your app will work ensure you have run the following commands on your local machine, in the terminal *(This only needs to be done once to create and set up your database)*
*Note: do not include the `$`*
```
$ flask db init
$ flask db migrate
$ flask db upgrade
```

### Running in Debug
To run your app in debug mode on a local server you can run
```
python app.py
```
### Stopping Debug
Type `ctrl + C` in the terminal
