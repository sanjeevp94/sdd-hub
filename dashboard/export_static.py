import os
import json
import shutil
from jinja2 import Environment, FileSystemLoader

DASHBOARD_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(DASHBOARD_DIR)
SPECS_DIR = os.path.join(ROOT_DIR, "specs")
OUTPUT_DIR = os.path.join(DASHBOARD_DIR, "out")

# Setup Jinja2
env = Environment(loader=FileSystemLoader(os.path.join(DASHBOARD_DIR, "templates")))
index_template = env.get_template("index.html")
spec_template = env.get_template("spec.html")
tutorial_template = env.get_template("tutorial.html")

# Create output dir
if os.path.exists(OUTPUT_DIR):
    shutil.rmtree(OUTPUT_DIR)
os.makedirs(OUTPUT_DIR)

# Copy static files
shutil.copytree(os.path.join(DASHBOARD_DIR, "static"), os.path.join(OUTPUT_DIR, "static"))

specs_list = []
if os.path.exists(SPECS_DIR):
    for feature_dir in os.listdir(SPECS_DIR):
        feature_path = os.path.join(SPECS_DIR, feature_dir)
        if os.path.isdir(feature_path):
            spec_file = os.path.join(feature_path, "spec.md")
            if os.path.exists(spec_file):
                with open(spec_file, "r") as f:
                    content = f.read()
                specs_list.append({
                    "name": feature_dir,
                    "content_preview": content[:200] + "...",
                    "url": f"spec/{feature_dir}.html"
                })

# Generate Index
index_html = index_template.render(specs=specs_list, is_static=True)
with open(os.path.join(OUTPUT_DIR, "index.html"), "w") as f:
    f.write(index_html)

# Generate Tutorial
tutorial_html = tutorial_template.render(is_static=True)
with open(os.path.join(OUTPUT_DIR, "tutorial.html"), "w") as f:
    f.write(tutorial_html)

# Generate Spec pages
os.makedirs(os.path.join(OUTPUT_DIR, "spec"))
for spec in specs_list:
    feature_dir = spec["name"]
    spec_file = os.path.join(SPECS_DIR, feature_dir, "spec.md")
    with open(spec_file, "r") as f:
        content = f.read()

    spec_html = spec_template.render(
        spec_name=feature_dir,
        content=content,
        comments=[],
        is_static=True
    )
    with open(os.path.join(OUTPUT_DIR, "spec", f"{feature_dir}.html"), "w") as f:
        f.write(spec_html)

print(f"Static site generated successfully at {OUTPUT_DIR}")
