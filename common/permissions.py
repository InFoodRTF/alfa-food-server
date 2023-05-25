from rest_framework.permissions import BasePermission


class IsCustomRole(BasePermission):
    """
    Пользовательская роль разрешений.

    Проверяет, что у пользователя есть определенная роль.
    """
    def __init__(self, role: str):
        """
        Инициализация класса разрешений.

        :param role: str ("parent", "teacher", "canteenemployee") Роль, которая должна быть у пользователя.
        """
        self.role = role

    def has_permission(self, request, view):
        # Проверка роли пользователя
        user = request.user
        return hasattr(user, self.role)
