from app.models import User, Collection

statuses = [
    ('completed', 'Просмотрено'),
    ('watching', 'Смотрю'),
    ('planned', 'Запланировано'),
    ('paused', 'На паузе'),
    ('dropped', 'Брошено'),
]

for user in User.objects.all():
    for status, label in statuses:
        if not Collection.objects.filter(user=user, status=status).exists():
            Collection.objects.create(
                user=user,
                collection_name=label,
                status=status
            )
print("Коллекции созданы для всех пользователей.") 