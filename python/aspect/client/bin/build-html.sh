#! /bin/sh
rm static/css/style.css
jinja2 templates/style.css.j2 static/test-data.yml --format=yaml >> static/css/style.css
rm static/index.html
jinja2 templates/index.html.j2 static/test-data.yml --format=yaml >> static/index.html
open static/index.html
