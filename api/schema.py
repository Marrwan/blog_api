import graphene
from graphene_django.types import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from django.core.exceptions import ValidationError, PermissionDenied
from django.contrib.auth import get_user_model
from .models import Author, Post, Comment
from .services import create_author, update_author, create_post, update_post, delete_post, create_comment
import graphql_jwt
from graphene import relay

User = get_user_model()

class AuthorType(DjangoObjectType):
    class Meta:
        model = Author

class PostType(DjangoObjectType):
    class Meta:
        model = Post
        interfaces = (relay.Node,)
        filter_fields = {
            'title': ['icontains'],
            'content': ['icontains'],
        }

class CommentType(DjangoObjectType):
    class Meta:
        model = Comment

class Query(graphene.ObjectType):
    all_posts = DjangoFilterConnectionField(PostType, author_id=graphene.Int(), title_contains=graphene.String())
    post = graphene.Field(PostType, id=graphene.Int(required=True))
    all_comments = graphene.List(CommentType, post_id=graphene.Int(required=True))

    def resolve_all_posts(self, info, author_id=None, title_contains=None):
        posts = Post.objects.all()
        if author_id:
            posts = posts.filter(author_id=author_id)
        if title_contains:
            posts = posts.filter(title__icontains=title_contains)
        return posts

    def resolve_post(self, info, id):
        return Post.objects.get(pk=id)

    def resolve_all_comments(self, info, post_id):
        return Comment.objects.filter(post_id=post_id)

class CreateAuthor(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        email = graphene.String(required=True)
        bio = graphene.String()

    author = graphene.Field(AuthorType)
    errors = graphene.List(graphene.String)

    def mutate(self, info, name, email, bio=None):
        user = info.context.user
        if not user.is_authenticated:
            raise PermissionDenied("You must be logged in to create an author.")
        try:
            author = create_author(name, email, bio, user.id)
            return CreateAuthor(author=author, errors=[])
        except ValidationError as e:
            return CreateAuthor(author=None, errors=[str(e)])

class UpdateAuthor(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
        name = graphene.String()
        email = graphene.String()
        bio = graphene.String()

    author = graphene.Field(AuthorType)
    errors = graphene.List(graphene.String)

    def mutate(self, info, id, name=None, email=None, bio=None):
        user = info.context.user
        if not user.is_authenticated:
            raise PermissionDenied("You must be logged in to update an author.")
        try:
            author = update_author(id, name, email, bio)
            return UpdateAuthor(author=author, errors=[])
        except ValidationError as e:
            return UpdateAuthor(author=None, errors=[str(e)])

class CreatePost(graphene.Mutation):
    class Arguments:
        title = graphene.String(required=True)
        content = graphene.String(required=True)
        author_id = graphene.Int(required=True)

    post = graphene.Field(PostType)
    errors = graphene.List(graphene.String)

    def mutate(self, info, title, content, author_id):
        user = info.context.user
        if not user.is_authenticated:
            raise PermissionDenied("You must be logged in to create a post.")
        try:
            author = Author.objects.get(pk=author_id)
            if author.user != user:
                raise PermissionDenied("You are not allowed to create posts for this author.")
            post = create_post(title, content, author_id)
            return CreatePost(post=post, errors=[])
        except ValidationError as e:
            return CreatePost(post=None, errors=[str(e)])

class UpdatePost(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
        title = graphene.String()
        content = graphene.String()

    post = graphene.Field(PostType)
    errors = graphene.List(graphene.String)

    def mutate(self, info, id, title=None, content=None):
        user = info.context.user
        if not user.is_authenticated:
            raise PermissionDenied("You must be logged in to update a post.")
        try:
            post = Post.objects.get(pk=id)
            if post.author.user != user:
                raise PermissionDenied("You are not allowed to update this post.")
            post = update_post(id, title, content)
            return UpdatePost(post=post, errors=[])
        except ValidationError as e:
            return UpdatePost(post=None, errors=[str(e)])

class DeletePost(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)

    success = graphene.Boolean()
    errors = graphene.List(graphene.String)

    def mutate(self, info, id):
        user = info.context.user
        if not user.is_authenticated:
            raise PermissionDenied("You must be logged in to delete a post.")
        try:
            post = Post.objects.get(pk=id)
            if post.author.user != user:
                raise PermissionDenied("You are not allowed to delete this post.")
            success = delete_post(id)
            return DeletePost(success=success, errors=[])
        except ValidationError as e:
            return DeletePost(success=False, errors=[str(e)])

class CreateComment(graphene.Mutation):
    class Arguments:
        content = graphene.String(required=True)
        post_id = graphene.Int(required=True)

    comment = graphene.Field(CommentType)
    errors = graphene.List(graphene.String)

    def mutate(self, info, content, post_id):
        user = info.context.user
        if not user.is_authenticated:
            raise PermissionDenied("You must be logged in to create a comment.")
        try:
            comment = create_comment(content, post_id)
            return CreateComment(comment=comment, errors=[])
        except ValidationError as e:
            return CreateComment(comment=None, errors=[str(e)])

class Mutation(graphene.ObjectType):
    create_author = CreateAuthor.Field()
    update_author = UpdateAuthor.Field()
    create_post = CreatePost.Field()
    update_post = UpdatePost.Field()
    delete_post = DeletePost.Field()
    create_comment = CreateComment.Field()
    token_auth = graphql_jwt.ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()

schema = graphene.Schema(query=Query, mutation=Mutation)
