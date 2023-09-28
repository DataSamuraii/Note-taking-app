# FastAPI Notes and Tags API Documentation

## Overview
This API allows you to perform CRUD operations for notes and tags. Each note can have multiple tags.

---

### General Information

- **Base URL**: `http://localhost:8000/`
- **Authentication**: Bearer Token

---

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

### User Operations

#### POST `/login`

- **Description**: Login and get access token.
- **Payload**: Form data with `username` and `password`.
- **Response**: JSON object containing `access_token` and `token_type`.
  
#### POST `/registration`

- **Description**: Register a new user.
- **Payload**: JSON object containing `username`, `email`, `full_name`, and `password`.
- **Response**: JSON object representing the newly registered user.

#### GET `/users`

- **Description**: Retrieve all users.
- **Response**: JSON array of users.

#### GET `/users/me/`

- **Description**: Retrieve the current authenticated user's profile.
- **Response**: JSON object representing the authenticated user.

#### GET `/users/me/notes`

- **Description**: Retrieve notes owned by the current authenticated user.
- **Response**: JSON array of notes owned by the authenticated user.

#### GET `/users/me/tags`

- **Description**: Retrieve tags owned by the current authenticated user.
- **Response**: JSON array of tags owned by the authenticated user.

---

### Note Operations

#### GET `/notes`

- **Description**: Retrieve all notes.
- **Response**: JSON array of notes.

#### GET `/notes/{note_id}`

- **Description**: Retrieve a note by its ID.
- **Parameters**: `note_id` (integer, path)
- **Response**: JSON object representing the note.

#### POST `/notes/post`

- **Description**: Create a new note.
- **Payload**: JSON object containing `title`, `content`, and optionally `tags`.
- **Response**: JSON object representing the new note.

#### PUT `/notes/{note_id}`

- **Description**: Update a note by its ID.
- **Parameters**: `note_id` (integer, path)
- **Payload**: JSON object containing updated `title`, `content`, and optionally `tags`.
- **Response**: JSON object representing the updated note.

#### DELETE `/notes/{note_id}`

- **Description**: Delete a note by its ID.
- **Parameters**: `note_id` (integer, path)
- **Response**: JSON object representing the deleted note.

---

### Tag Operations

#### GET `/tags`

- **Description**: Retrieve all tags.
- **Response**: JSON array of tags.

#### POST `/tags/post`

- **Description**: Create new tags.
- **Payload**: JSON array of tags.
- **Response**: JSON array of the newly created tags.

#### PUT `/tags/{tag_id}`

- **Description**: Update a tag by its ID.
- **Parameters**: `tag_id` (integer, path)
- **Payload**: JSON object containing the updated `tag_name`.
- **Response**: JSON object representing the updated tag.

#### DELETE `/tags/{tag_id}`

- **Description**: Delete a tag by its ID.
- **Parameters**: `tag_id` (integer, path)
- **Response**: JSON object representing the deleted tag.

---

This is a simplified documentation. You can generate detailed, interactive documentation using FastAPI's built-in Swagger UI or ReDoc by visiting `http://localhost:8000/docs` or `http://localhost:8000/redoc`, respectively.

Certainly, Alex! Including a testing chapter in your documentation is a smart move. It helps both in ensuring the API works as expected and in providing example usages of your API endpoints. Here's how you can extend your documentation:

---

## Testing the API

To test the API, we use HTTP requests in a `.http` file format, which can be run using tools like [HTTPie](https://httpie.io/) or IDEs like [JetBrains IDEs](https://www.jetbrains.com/help/idea/http-client-in-product-code-editor.html) that support this format.

### How to Run the Tests

1. Make sure your FastAPI server is running.
2. Open `test_main.http` in your IDE.
3. Run each HTTP request.

### Environment Configuration

To manage environment variables such as the JWT token, you can use an `http-client.env.json` file. This allows you to specify different environments and corresponding variables.

**File: `http-client.env.json`**

```json
{
  "dev": {
    "token": ""
  }
}
```

In this file, the `token` under `dev` can be updated with an actual JWT token for authenticated requests. Make sure to replace the empty string with your actual token. To get your token, register first and save the token you receive in the response.

---
## Future Work
- Implement a real database instead of the mock database.
- Add metadata to API
- Add Background task to send email to user email after registration and login