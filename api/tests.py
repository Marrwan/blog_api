
from django.test import TestCase
from django.contrib.auth import get_user_model
from graphene_django.utils import GraphQLTestCase
from .models import Author, Post, Comment


class AuthorTestCase(TestCase):
    def setUp(self):
        self.author = Author.objects.create(name="Author Name", email="author@example.com")

    def test_author_str(self):
        self.assertEqual(str(self.author), "Author Name")


class PostTestCase(TestCase):
    def setUp(self):
        self.author = Author.objects.create(name="Author Name", email="author@example.com")
        self.post = Post.objects.create(title="Post Title", content="Post Content", author=self.author)

    def test_post_str(self):
        self.assertEqual(str(self.post), "Post Title")


class CommentTestCase(TestCase):
    def setUp(self):
        self.author = Author.objects.create(name="Author Name", email="author@example.com")
        self.post = Post.objects.create(title="Post Title", content="Post Content", author=self.author)
        self.comment = Comment.objects.create(content="Comment Content", post=self.post)

    def test_comment_str(self):
        self.assertEqual(str(self.comment), "Comment by 1")


class BlogSchemaTestCase(GraphQLTestCase):
    def test_query_all_posts(self):
        response = self.query(
            '''
            query {
                allPosts {
                    title
                }
            }
            ''',
            op_name='query_all_posts'
        )
        self.assertResponseNoErrors(response)
        content = response.json()
        self.assertIn('data', content)
        self.assertIn('allPosts', content['data'])

    def test_create_post_mutation(self):
        response = self.query(
            '''
            mutation {
                createPost(title: "New Post", content: "Post Content", authorId: 1) {
                    post {
                        title
                        content
                    }
                }
            }
            ''',
            op_name='create_post'
        )
        self.assertResponseNoErrors(response)
        content = response.json()
        self.assertIn('data', content)
        self.assertIn('createPost', content['data'])
        self.assertEqual(content['data']['createPost']['post']['title'], "New Post")
