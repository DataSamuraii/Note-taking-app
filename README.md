# FastAPI Notes and Tags API Documentation

## Overview
This API allows you to perform CRUD operations for notes and tags. Each note can have multiple tags.

## Setup
Install the required packages using pip:
```bash
pip install -r requirements.txt
```

Run the FastAPI application:
```bash
uvicorn main:app --reload
```

## Endpoints

### Notes

#### GET /notes
Fetch all notes.
- **Response**: List of notes

#### POST /notes
Add a new note.
- **Request Body**: { "title": "string", "content": "string", "tags": [ { "tag_name": "string" } ] }
- **Response**: Created note

#### GET /notes/{note_id}
Fetch a note by ID.
- **Path Params**: `note_id` (integer)
- **Response**: Note object

#### PUT /notes/{note_id}
Update a note by ID.
- **Path Params**: `note_id` (integer)
- **Request Body**: { "title": "string", "content": "string", "tags": [ { "tag_name": "string" } ] }
- **Response**: Updated note

#### DELETE /notes/{note_id}
Delete a note by ID.
- **Path Params**: `note_id` (integer)
- **Response**: Deleted note

#### GET /notes/search
Search notes by title or content.
- **Query Params**: `note_title` (string, optional), `note_content` (string, optional)
- **Response**: List of matching notes

#### PUT /notes/{note_id}/tags
Assign tags to a note by ID.
- **Path Params**: `note_id` (integer)
- **Request Body**: [ { "tag_name": "string" } ]
- **Response**: Updated note

#### DELETE /notes/{note_id}/tags
Remove tags from a note by ID.
- **Path Params**: `note_id` (integer)
- **Request Body**: [ { "tag_name": "string" } ]
- **Response**: Updated note

### Tags

#### GET /tags
Fetch all tags.
- **Response**: List of tags

#### POST /tags
Add new tags.
- **Request Body**: [ { "tag_name": "string" } ]
- **Response**: Created tags

#### GET /tags/{tag_id}
Fetch a tag by ID.
- **Path Params**: `tag_id` (integer)
- **Response**: Tag object

#### PUT /tags/{tag_id}
Update a tag by ID.
- **Path Params**: `tag_id` (integer)
- **Request Body**: { "tag_name": "string" }
- **Response**: Updated tag

#### DELETE /tags/{tag_id}
Delete a tag by ID.
- **Path Params**: `tag_id` (integer)
- **Response**: Deleted tag

#### GET /tags/search
Search tags by name.
- **Query Params**: `tag_name` (string, optional)
- **Response**: List of matching tags

## Schema

### Note Schema
- `id`: integer
- `title`: string
- `content`: string
- `created_at`: datetime string
- `updated_at`: datetime string
- `tags`: array of tag objects

### Tag Schema
- `id`: integer
- `tag_name`: string

## Error Codes
- `404`: Not Found
- `400`: Bad Request

## Future Work
- Implement a real database instead of the mock database.
- Add user authentication.