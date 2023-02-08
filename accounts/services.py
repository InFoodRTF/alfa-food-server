from django.contrib.auth.models import User

from accounts.models import Parent, Teacher, CanteenEmployee

roles = {
    "Родитель": Parent,
    "Учитель": Teacher,
    "Работник столовой": CanteenEmployee,
}


def set_user_name(initial_data, user: User):
    user.first_name = str(initial_data.get('first_name') or "")
    user.last_name = str(initial_data.get('last_name') or "")
    user.profile.middle_name = str(initial_data.get('middle_name') or "")
