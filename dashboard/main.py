import os
import json
from datetime import datetime
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI(title="Spec-Driven Development Hub")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

SPECS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "specs")
COMMENTS_FILE = os.path.join(os.path.dirname(__file__), "data", "comments.json")

# Ensure directories exist
os.makedirs(SPECS_DIR, exist_ok=True)
os.makedirs(os.path.dirname(COMMENTS_FILE), exist_ok=True)

if not os.path.exists(COMMENTS_FILE):
    with open(COMMENTS_FILE, "w") as f:
        json.dump({}, f)

def get_comments():
    with open(COMMENTS_FILE, "r") as f:
        return json.load(f)

def save_comments(comments):
    with open(COMMENTS_FILE, "w") as f:
        json.dump(comments, f, indent=4)

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    specs = []
    if os.path.exists(SPECS_DIR):
        for feature_dir in os.listdir(SPECS_DIR):
            feature_path = os.path.join(SPECS_DIR, feature_dir)
            if os.path.isdir(feature_path):
                spec_file = os.path.join(feature_path, "spec.md")
                if os.path.exists(spec_file):
                    with open(spec_file, "r") as f:
                        content = f.read()
                    specs.append({"name": feature_dir, "content_preview": content[:200] + "..."})
    return templates.TemplateResponse(request=request, name="index.html", context={"specs": specs})

@app.get("/spec/{spec_name}", response_class=HTMLResponse)
async def read_spec(request: Request, spec_name: str):
    filepath = os.path.join(SPECS_DIR, spec_name, "spec.md")
    if not os.path.exists(filepath):
        return HTMLResponse("Spec not found", status_code=404)

    with open(filepath, "r") as f:
        content = f.read()

    all_comments = get_comments()
    spec_comments = all_comments.get(spec_name, [])

    return templates.TemplateResponse(request=request, name="spec.html", context={
        "spec_name": spec_name,
        "content": content,
        "comments": spec_comments
    })

@app.post("/spec/{spec_name}/comment")
async def add_comment(spec_name: str, author: str = Form(...), text: str = Form(...)):
    comments = get_comments()
    if spec_name not in comments:
        comments[spec_name] = []

    comments[spec_name].append({
        "author": author,
        "text": text,
        "timestamp": datetime.now().isoformat()
    })

    save_comments(comments)
    return RedirectResponse(url=f"/spec/{spec_name}", status_code=303)

@app.get("/tutorial", response_class=HTMLResponse)
async def tutorial(request: Request):
    return templates.TemplateResponse(request=request, name="tutorial.html", context={})
