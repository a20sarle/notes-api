"""
Notes API - a small REST API built with FastAPI.

Run locally:   uvicorn app.main:app --reload
Docs:          http://localhost:8000/docs   (interactive, generated automatically)
"""

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel

# FastAPI generates an OpenAPI specification from this app.
# The OpenAPI spec is what powers the interactive docs at /docs.
# The title and version show up in those docs.
# Versioning an API lets you change it later without breaking existing clients.
app = FastAPI(title="Notes API", version="1.0.0")


# ---------------------------------------------------------------------------
# SCHEMAS (data models)
# API DESIGN: schemas define the "contract" of the API, i.e. exactly what
# data goes in and what comes out.
# Pydantic validates incoming data automatically. Here is an example:
# A missing "title" makes FastAPI answer 422 Unprocessable Entity.
# A "title" of the wrong type also gets a 422.
# In both cases you don't write any validation code yourself.
# ---------------------------------------------------------------------------

class NoteIn(BaseModel):
    """What the CLIENT sends when creating a note (no id, since the server assigns it)."""
    title: str            # required field
    content: str = ""     # optional field, defaults to an empty string


class Note(NoteIn):
    """What the API RETURNS: the same fields plus the server-generated id."""
    id: int

# API DESIGN: keeping input and output models separate is good practice.
# The client can't choose its own id.
# You also never accidentally expose internal fields.


# ---------------------------------------------------------------------------
# STORAGE
# An in-memory dict acts as a fake database.
# Everything is lost when the app restarts, which is fine for a demo.
# Swapping it for a real database later would not change the API itself.
# This is a design point: the API contract stays independent of how data is stored.
# ---------------------------------------------------------------------------

notes: dict[int, Note] = {}
next_id = 1


# ---------------------------------------------------------------------------
# ENDPOINTS
# API DESIGN (REST): URLs name RESOURCES (nouns), and HTTP methods name ACTIONS.
#
#   GET    /notes        -> list all notes
#   GET    /notes/{id}   -> get one note
#   POST   /notes        -> create a note
#   DELETE /notes/{id}   -> delete a note
#
# Notice we have /notes, NOT /getNotes or /createNote.
# The HTTP method already says what the action is.
# The resource name is plural, and that is the common convention.
# ---------------------------------------------------------------------------

@app.get("/health")
def health():
    # API DESIGN: a health-check endpoint is standard practice.
    # Docker, Kubernetes, load balancers and monitoring tools call it to check
    # that the service is alive.
    return {"status": "ok"}


@app.get("/notes", response_model=list[Note])
def list_notes():
    # GET is "safe": it only reads and never changes data.
    # Returns 200 OK by default.
    # response_model guarantees that the response follows the Note schema.
    return list(notes.values())


@app.get("/notes/{note_id}", response_model=Note)
def get_note(note_id: int):
    # {note_id} is a PATH PARAMETER. It identifies ONE specific resource.
    # Declaring it as "int" makes FastAPI reject /notes/abc with a 422 automatically.
    if note_id not in notes:
        # API DESIGN: use correct status codes.
        # 404 Not Found tells the client clearly that the resource doesn't exist.
        # Don't return 200 with an error message inside the body.
        raise HTTPException(status_code=404, detail="Note not found")
    return notes[note_id]


@app.post("/notes", response_model=Note, status_code=status.HTTP_201_CREATED)
def create_note(note: NoteIn):
    # POST creates a new resource.
    # The request BODY (JSON) is validated against NoteIn automatically.
    # API DESIGN: 201 Created, not plain 200, is the correct code when something
    # is created.
    # We return the created object, including its new id, so the client knows
    # what it got.
    global next_id
    new_note = Note(id=next_id, **note.model_dump())
    notes[next_id] = new_note
    next_id += 1
    return new_note


@app.delete("/notes/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_note(note_id: int):
    # DELETE removes a resource.
    # API DESIGN: 204 No Content means "it worked, and there is nothing to return".
    # Deleting something that doesn't exist gives 404, consistent with GET above.
    # Consistency across endpoints is itself a design principle.
    if notes.pop(note_id, None) is None:
        raise HTTPException(status_code=404, detail="Note not found")


# ---------------------------------------------------------------------------
# STATUS CODES USED IN THIS API (summary)
#   200 OK                    - successful read
#   201 Created               - resource created (POST)
#   204 No Content            - success, empty response (DELETE)
#   404 Not Found             - resource doesn't exist
#   422 Unprocessable Entity  - invalid input (sent automatically by FastAPI)
#
# Possible next steps:
#   - PUT /notes/{id} to update a note (an idempotent full replacement)
#   - pagination, e.g. GET /notes?limit=10&offset=0
#   - a version prefix in the URL, e.g. /v1/notes
# ---------------------------------------------------------------------------