import os
# Set up Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
import django
django.setup()


from django.contrib.auth.models import User

def create_user(username, password):
    try:
        # Create the user
        user = User.objects.create_user(username=username, password=password)
        print(f"User '{username}' created successfully.")
        print(f"Username: {user.username}, password: {password}")
        return user
    except Exception as e:
        print(f"Error creating user: {e}")

if __name__ == "__main__":
    # Replace with the desired credentials
    create_user('Abdulbasit', 'marrwanah12')
