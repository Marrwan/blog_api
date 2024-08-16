
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.db.models import Q
from .models import Author, Post, Comment
from django.contrib.auth import get_user_model

User = get_user_model()

def create_author(name, email, bio=None, user_id=None):
    if Author.objects.filter(email=email).exists():
        raise ValidationError("An author with this email already exists.")
    try:
        user = User.objects.get(pk=user_id) if user_id else None
        author = Author(name=name, email=email, bio=bio, user=user)
        author.save()
        return author
    except User.DoesNotExist:
        raise ValidationError("User not found.")
    except IntegrityError as e:
        raise ValidationError(f"Error creating author: {e}")


def update_author(id, name=None, email=None, bio=None):
    try:
        author = Author.objects.get(pk=id)
        if email and Author.objects.filter(email=email).exclude(id=id).exists():
            raise ValidationError("An author with this email already exists.")
        if name:
            author.name = name
        if email:
            author.email = email
        if bio:
            author.bio = bio
        author.save()
        return author
    except Author.DoesNotExist:
        raise ValidationError("Author not found.")
    except IntegrityError as e:
        raise ValidationError(f"Error updating author: {e}")

def create_post(title, content, author_id):
    if Post.objects.filter(title=title).exists():
        raise ValidationError("A post with this title already exists.")
    try:
        author = Author.objects.get(pk=author_id)
        post = Post(title=title, content=content, author=author)
        post.save()
        return post
    except Author.DoesNotExist:
        raise ValidationError("Author not found.")
    except IntegrityError as e:
        raise ValidationError(f"Error creating post: {e}")

def update_post(id, title=None, content=None):
    try:
        post = Post.objects.get(pk=id)
        if title and Post.objects.filter(title=title).exclude(id=id).exists():
            raise ValidationError("A post with this title already exists.")
        if title:
            post.title = title
        if content:
            post.content = content
        post.save()
        return post
    except Post.DoesNotExist:
        raise ValidationError("Post not found.")
    except IntegrityError as e:
        raise ValidationError(f"Error updating post: {e}")

def delete_post(id):
    try:
        post = Post.objects.get(pk=id)
        post.delete()
        return True
    except Post.DoesNotExist:
        raise ValidationError("Post not found.")
    except IntegrityError as e:
        raise ValidationError(f"Error deleting post: {e}")

def create_comment(content, post_id):
    try:
        post = Post.objects.get(pk=post_id)
        comment = Comment(content=content, post=post)
        comment.save()
        return comment
    except Post.DoesNotExist:
        raise ValidationError("Post not found.")
    except IntegrityError as e:
        raise ValidationError(f"Error creating comment: {e}")
