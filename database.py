# Mock database for Notes
notes_db = [
    {
        "id": 1,
        "title": "Grocery List",
        "content": "Milk, Eggs, Bread",
        "created_at": "2023-09-11T12:00:00",
        "updated_at": "2023-09-11T12:00:00",
        "tags": [{"tag_name": 'Personal'}]
    },
    {
        "id": 2,
        "title": "To-Do",
        "content": "Fix bugs, Write documentation",
        "created_at": "2023-09-10T09:30:00",
        "updated_at": "2023-09-10T09:30:00",
        "tags": [{"tag_name": "Work"}]
    },
    {
        "id": 3,
        "title": "Meeting Notes",
        "content": "Discuss project roadmap, Assign tasks",
        "created_at": "2023-09-09T15:45:00",
        "updated_at": "2023-09-09T15:45:00",
        "tags": [{"tag_name": "Meeting"}]
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
