# FastAPI Notes and Tags API Documentation

## Overview
A FastAPI-based application for managing notes and tags, where each note can have multiple tags. Users can register, login, and perform CRUD operations on notes and tags.

---

### General Information

- **Base URL**: `http://localhost:8000/`
- **Authentication**: Bearer Token (JWT)

---

## Setup
Install the required packages using pip:
```bash
pip install -r requirements.txt
```

### Configuring `.env` for Environment Variables

1. **Create `.env` in Root**: 
   Create a `.env` file in the project's root directory.

2. **Define Variables**: 
   Populate `.env` with the necessary configurations:

   ```env
   DB_URL=mysql+pymysql://username:password@address/db_table_name
   SECRET_KEY=secret
   ALGORITHM=algorithm
   ACCESS_TOKEN_EXPIRE_MINUTES=token_time_to_live
   OWN_EMAIL="hello@example.com"
   OWN_EMAIL_PASSWORD="your-password"
   ```

   Replace placeholders like `username`, `password`, etc., with actual values. `ACCESS_TOKEN_EXPIRE_MINUTES` should be an int.

3. **Load in App**: 
   Ensure your app reads from `.env` at startup. Libraries like `python-dotenv` can assist.

**Note**: 
- Always exclude `.env` from version control (e.g., add to `.gitignore`).
- Keep a secure backup of `.env` contents.

Run the FastAPI application:
```bash
uvicorn main:app --reload
```

---

## Endpoints

### User Operations

#### POST `/login`

- **Description**: Log in and obtain an access token.
- **Payload**: Form data with `username` and `password`.
- **Response**: JSON object containing `access_token` and `token_type`.

#### POST `/registration`

- **Description**: Register a new user.
- **Payload**: JSON object containing `username`, `email` (optional), `full_name` (optional), and `password`.
- **Response**: JSON object representing the newly registered user.

#### GET `/users`

- **Description**: Retrieve all users. (No authentication required)
- **Response**: JSON array of users.

#### GET `/users/me/`

- **Description**: Retrieve the current authenticated user's profile.
- **Authentication**: Required
- **Response**: JSON object representing the authenticated user.

#### GET `/users/me/notes`

- **Description**: Retrieve notes owned by the current authenticated user.
- **Authentication**: Required
- **Response**: JSON array of notes owned by the authenticated user.

#### GET `/users/me/tags`

- **Description**: Retrieve tags owned by the current authenticated user.
- **Authentication**: Required
- **Response**: JSON array of tags owned by the authenticated user.

---

### Note Operations

#### GET `/notes`

- **Description**: Retrieve all notes. (No authentication required)
- **Response**: JSON array of notes.

#### GET `/notes/{note_id}`

- **Description**: Retrieve a note by its ID.
- **Parameters**: `note_id` (integer, path)
- **Authentication**: Required if accessing a note owned by another user
- **Response**: JSON object representing the note.

#### POST `/notes/post`

- **Description**: Create a new note.
- **Payload**: JSON object containing `title` and `content`.
- **Authentication**: Required
- **Response**: JSON object representing the new note.

#### PATCH `/notes/{note_id}`

- **Description**: Update a note by its ID.
- **Parameters**: `note_id` (integer, path)
- **Payload**: JSON object containing updated `title` and/or `content`.
- **Authentication**: Required
- **Response**: JSON object representing the updated note.

#### DELETE `/notes/{note_id}`

- **Description**: Delete a note by its ID.
- **Parameters**: `note_id` (integer, path)
- **Authentication**: Required
- **Response**: JSON object representing the deleted note.

---

### Tag Operations

Note: Tag operations are not clearly defined in the provided code. Below are assumed endpoints based on common practices.

#### GET `/tags`

- **Description**: Retrieve all tags. (No authentication required)
- **Response**: JSON array of tags.

#### POST `/tags/post`

- **Description**: Create new tags.
- **Payload**: JSON object containing `tag_name`.
- **Authentication**: Required
- **Response**: JSON object representing the newly created tag.

#### PATCH `/tags/{tag_id}`

- **Description**: Update a tag by its ID.
- **Parameters**: `tag_id` (integer, path)
- **Payload**: JSON object containing the updated `tag_name`.
- **Authentication**: Required
- **Response**: JSON object representing the updated tag.

#### DELETE `/tags/{tag_id}`

- **Description**: Delete a tag by its ID.
- **Parameters**: `tag_id` (integer, path)
- **Authentication**: Required
- **Response**: JSON object representing the deleted tag.

---

For more detailed and interactive documentation, utilize FastAPI's built-in Swagger UI or ReDoc by visiting `http://localhost:8000/docs` or `http://localhost:8000/redoc`, respectively.

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
- ~~Implement a real database instead of the mock database.~~
- Add Metadata to API
- ~~Add Background task to send email to user email after registration and login~~
- Add Exception handling