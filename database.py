# Mock database for Notes
notes_db = [
    {
        "id": 1,
        "title": "Grocery List",
        "content": "Milk, Eggs, Bread",
        "tags": [{"tag_name": 'Personal'}],
        "created_at": "2023-09-11T12:00:00",
        "updated_at": "2023-09-11T12:00:00",
        "owner": "johndoe"
    },
    {
        "id": 2,
        "title": "To-Do",
        "content": "Fix bugs, Write documentation",
        "tags": [{"tag_name": "Work"}],
        "created_at": "2023-09-10T09:30:00",
        "updated_at": "2023-09-10T09:30:00",
        "owner": "johndoe"
    },
    {
        "id": 3,
        "title": "Meeting Notes",
        "content": "Discuss project roadmap, Assign tasks",
        "tags": [{"tag_name": "Meeting"}],
        "created_at": "2023-09-09T15:45:00",
        "updated_at": "2023-09-09T15:45:00",
        "owner": "alice"
    }
]

# Mock database for Tags
tags_db = [
    {
        "id": 1,
        "tag_name": "Personal",
        "owner": "johndoe"
    },
    {
        "id": 2,
        "tag_name": "Work",
        "owner": "johndoe"
    },
    {
        "id": 3,
        "tag_name": "Meeting",
        "owner": "alice"
    }
]

users_db = {
    "johndoe": {
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
        'disabled': False
    },
    "alice": {
        "username": "alice",
        "full_name": "Alice Wonderson",
        "email": "alice@example.com",
        "hashed_password": "fakehashedsecret2",
        "disabled": True
    }
}
