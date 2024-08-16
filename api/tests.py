from django.test import TestCase
from django.core.exceptions import ValidationError, PermissionDenied
from .models import Author, Post, Comment
from .services import create_author, update_author, create_post, update_post, delete_post, create_comment
from django.contrib.auth.models import User
from graphene_django.utils.testing import graphql_query

class BlogApiTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.author = create_author(name="John Doe", email="john@example.com", bio="Author bio.", user_id=self.user.id)

    def test_create_author(self):
        author = create_author(name="Jane Doe", email="jane@example.com", bio="Another bio.", user_id=self.user.id)
        self.assertEqual(author.name, "Jane Doe")
        self.assertEqual(author.email, "jane@example.com")

    def test_create_duplicate_author_email(self):
        with self.assertRaises(ValidationError):
            create_author(name="John Doe", email="john@example.com", bio="Duplicate email.", user_id=self.user.id)

    def test_update_author(self):
        updated_author = update_author(id=self.author.id, name="John Updated", email="johnupdated@example.com")
        self.assertEqual(updated_author.name, "John Updated")
        self.assertEqual(updated_author.email, "johnupdated@example.com")

    def test_create_post(self):
        post = create_post(title="Test Post", content="This is a test post.", author_id=self.author.id)
        self.assertEqual(post.title, "Test Post")
        self.assertEqual(post.content, "This is a test post.")

    def test_update_post(self):
        post = create_post(title="Test Post", content="This is a test post.", author_id=self.author.id)
        updated_post = update_post(id=post.id, title="Updated Post", content="Updated content.")
        self.assertEqual(updated_post.title, "Updated Post")
        self.assertEqual(updated_post.content, "Updated content.")

    def test_delete_post(self):
        post = create_post(title="Test Post", content="This is a test post.", author_id=self.author.id)
        result = delete_post(id=post.id)
        self.assertTrue(result)

    def test_create_comment(self):
        post = create_post(title="Test Post", content="This is a test post.", author_id=self.author.id)
        comment = create_comment(content="This is a comment.", post_id=post.id)
        self.assertEqual(comment.content, "This is a comment.")
        self.assertEqual(comment.post.id, post.id)

    def test_create_comment_post_not_found(self):
        with self.assertRaises(ValidationError):
            create_comment(content="This is a comment.", post_id=9999)

    def test_post_last_updated_on_comment(self):
        post = create_post(title="Test Post", content="This is a test post.", author_id=self.author.id)
        original_updated_at = post.updated_at
        comment = create_comment(content="This is a comment.", post_id=post.id)
        post.refresh_from_db()
        self.assertNotEqual(post.updated_at, original_updated_at)


class BlogAPIQueryTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpassword")
        self.author = Author.objects.create(name="John Doe", email="john@example.com", bio="A passionate writer.", user=self.user)
        self.client.login(username="testuser", password="testpassword")

    def graphql_query(self, query):
        response = self.client.post(
            '/graphql/',
            data={'query': query},
            content_type='application/json'
        )
        return response.json()

    def test_create_author(self):
        query = '''
            mutation {
                createAuthor(name: "Jane Doe", email: "jane@example.com", bio: "Another writer.") {
                    author {
                        id
                        name
                        email
                        bio
                    }
                    errors
                }
            }
        '''
        content = self.graphql_query(query)
        self.assertIsNone(content.get("errors"))
        self.assertEqual(content["data"]["createAuthor"]["author"]["name"], "Jane Doe")

    def test_create_post(self):
        query = '''
            mutation {
                createPost(title: "New Post", content: "This is a new post.", authorId: %d) {
                    post {
                        id
                        title
                        content
                        author {
                            id
                            name
                        }
                    }
                    errors
                }
            }
        ''' % self.author.id
        content = self.graphql_query(query)
        self.assertIsNone(content.get("errors"))
        self.assertEqual(content["data"]["createPost"]["post"]["title"], "New Post")

    def test_update_post(self):
        post = Post.objects.create(title="Old Post", content="Old content.", author=self.author)
        query = '''
            mutation {
                updatePost(id: "%s", title: "Updated Post", content: "Updated content.") {
                    post {
                        id
                        title
                        content
                    }
                    errors
                }
            }
        ''' % post.id
        content = self.graphql_query(query)
        self.assertIsNone(content.get("errors"))
        self.assertEqual(content["data"]["updatePost"]["post"]["title"], "Updated Post")

    def test_delete_post(self):
        post = Post.objects.create(title="Post to Delete", content="This post will be deleted.", author=self.author)
        query = '''
            mutation {
                deletePost(id: "%s") {
                    success
                    errors
                }
            }
        ''' % post.id
        content = self.graphql_query(query)
        self.assertIsNone(content.get("errors"))
        self.assertTrue(content["data"]["deletePost"]["success"])

    def test_create_comment(self):
        post = Post.objects.create(title="Post with Comments", content="This post will have comments.", author=self.author)
        query = '''
            mutation {
                createComment(content: "This is a comment.", postId: %d) {
                    comment {
                        id
                        content
                        post {
                            id
                            title
                        }
                    }
                    errors
                }
            }
        ''' % post.id
        content = self.graphql_query(query)
        self.assertIsNone(content.get("errors"))
        self.assertEqual(content["data"]["createComment"]["comment"]["content"], "This is a comment.")

    def test_query_all_posts(self):
        Post.objects.create(title="First Post", content="First post content.", author=self.author)
        Post.objects.create(title="Second Post", content="Second post content.", author=self.author)
        query = '''
            {
                allPosts(authorId: %d) {
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
        ''' % self.author.id
        content = self.graphql_query(query)
        self.assertIsNone(content.get("errors"))
        self.assertEqual(len(content["data"]["allPosts"]["edges"]), 2)

    def test_query_single_post(self):
        post = Post.objects.create(title="Single Post", content="Single post content.", author=self.author)
        query = '''
            {
                post(id: %d) {
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
        ''' % post.id
        content = self.graphql_query(query)
        self.assertIsNone(content.get("errors"))
        self.assertEqual(content["data"]["post"]["title"], "Single Post")
