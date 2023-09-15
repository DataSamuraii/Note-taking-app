# Mock database for Notes
notes_db = [
    {
        "id": 1,
        "title": "Grocery List",
        "content": "Milk, Eggs, Bread",
        "tags": [{"tag_name": 'Personal'}],
        "created_at": "2023-09-11T12:00:00",
        "updated_at": "2023-09-11T12:00:00",
    },
    {
        "id": 2,
        "title": "To-Do",
        "content": "Fix bugs, Write documentation",
        "tags": [{"tag_name": "Work"}],
        "created_at": "2023-09-10T09:30:00",
        "updated_at": "2023-09-10T09:30:00",
    },
    {
        "id": 3,
        "title": "Meeting Notes",
        "content": "Discuss project roadmap, Assign tasks",
        "tags": [{"tag_name": "Meeting"}],
        "created_at": "2023-09-09T15:45:00",
        "updated_at": "2023-09-09T15:45:00",
    }
]

# Mock database for Tags
tags_db = [
    {
        "id": 1,
        "tag_name": "Personal"
    },
    {
        "id": 2,
        "tag_name": "Work"
    },
    {
        "id": 3,
        "tag_name": "Meeting"
    }
]
