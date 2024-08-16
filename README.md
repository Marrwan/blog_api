# Blog API

This is a simple GraphQL-based API for managing authors, posts, and comments. It is built with Django and Graphene.

## Setup Instructions

### Prerequisites

- Python 3.8+
- PostgreSQL
- Django
- Graphene-Django
- GraphQL-JWT

### Installation

1. **Clone the repository:**

```bash
   git clone https://github.com/Marrwan/blog_api.git
   cd blog-api
```
Create and activate a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
```

Install dependencies:
```bash
pip install -r requirements.txt
```
Set up PostgreSQL database:
Create a PostgreSQL database using the credentials provided in the .env file.
```sql
CREATE DATABASE blog_api;
CREATE USER postgres WITH PASSWORD 'your-password';
GRANT ALL PRIVILEGES ON DATABASE blog_api TO postgres;
```

Run migrations:
```bash
python manage.py migrate
```
Create a superuser:
```bash
python manage.py createsuperuser
```
Run the development server:
```bash
python manage.py runserver
```
## Access the GraphQL endpoint:

Open your browser and navigate to `http://127.0.0.1:8000/graphql/` to access the GraphQL playground.

## GraphQL Queries and Mutations
A. First Create a user
```bash
python manage.py create_user.py
```
You'll, get a reply like this:
```shell
User 'Abdulbasit' created successfully.
Username: Abdulbasit, password: marrwanah12
```
B. After that, Login using the below query:
```shell
mutation {
  tokenAuth(username: "Abdulbasit", password: "marrwanah12") {
    token
    payload
    refreshExpiresIn
  }
}
```
You'll get a reply that looks lke this:
```json
{
  "data": {
    "tokenAuth": {
      "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6IkFiZHVsYmFzaXQiLCJleHAiOjE3MjM5MDM4OTgsIm9yaWdJYXQiOjE3MjM4MTc0OTh9.RcLCT_fdKdiMt2c59eLvctsmTqiJChvcdJTqF3LSGjE",
      "payload": {
        "username": "Abdulbasit",
        "exp": 1723903898,
        "origIat": 1723817498
      },
      "refreshExpiresIn": 1724422298
    }
  }
}
```

C. Copy the token:
    In GraphQL Playground, you can set HTTP headers for authentication. Follow these steps:

    1. Open GraphQL Playground.

    2. Click on the "HTTP HEADERS" button at the bottom left.

    3. Add the Authorization header with the value Bearer YOUR_ACCESS_TOKEN.
like this
```shell
{
  "Authorization": "Bearer YOUR_ACCESS_TOKEN"
}
Continue
```
1. Create an Author
```shell
mutation {
  createAuthor(name: "John Doe", email: "john@example.com", bio: "A passionate writer.") {
    author {
      id
      name
      email
      bio
    }
    errors
  }
}
```
2. Update an Author
```graphql
mutation {
  updateAuthor(id: "1", name: "Jane Doe", email: "jane@example.com", bio: "An updated bio.") {
    author {
      id
      name
      email
      bio
    }
    errors
  }
}
```
3. Create a Post
```graphql
mutation {
  createPost(title: "My First Post", content: "This is the content of my first post.", authorId: 1) {
    post {
      id
      title
      content
      createdAt
      updatedAt
      author {
        id
        name
      }
    }
    errors
  }
}
```
4. Update a Post
```graphql
mutation {
  updatePost(id: "1", title: "Updated Title", content: "Updated content.") {
    post {
      id
      title
      content
      updatedAt
    }
    errors
  }
}
```
5. Delete a Post
```graphql
mutation {
  deletePost(id: "1") {
    success
    errors
  }
}
```
6. Create a Comment
```graphql
mutation {
  createComment(content: "This is a comment.", postId: 2) {
    comment {
      id
      content
      createdAt
      post {
        id
        title
      }
    }
    errors
  }
}
```
7. Query All Posts
```graphql
{
  allPosts(authorId: 1) {
    edges {
      node {
        id
        title
        content
        author {
          id
          name
        }
        comments {
          id
          content
        }
      }
    }
  }
}
```
8. Query a Single Post
```graphql
{
  post(id: 2) {
    id
    title
    content
    author {
      id
      name
    }
    comments {
      id
      content
    }
  }
}
```
9. Query All Comments for a Post
```graphql
{
  allComments(postId: 2) {
    id
    content
    createdAt
    post {
      id
      title
    }
  }
}

```
## Running Tests
### Prerequisites
Make sure the development server is running.

Run Tests
```bash
python manage.py test
```