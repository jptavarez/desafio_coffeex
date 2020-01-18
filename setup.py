import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'desafio_estoque.settings')
django.setup()

def main():
    from django.core.management import call_command
    from django.db import migrations, models, transaction
    from django.contrib.auth.models import User
    call_command("migrate", interactive=False)
    
    with transaction.atomic():
        user = User.objects.create_user('manager_user', password='123456')
        user.is_superuser = True
        user.is_staff = True
        user.profile.coffeex_manager = True
        user.save()

        user = User.objects.create_user('normal_user', password='123456')
        user.is_superuser = True
        user.is_staff = True
        user.profile.coffeex_manager = False
        user.save()

if __name__ == '__main__':
    main()