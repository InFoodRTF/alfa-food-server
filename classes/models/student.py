from django.db import models

from classes.models.grade import Grade

from accounts.models import Parent


class Student(models.Model):
    class Meta:
        db_table = "students"
        verbose_name = "Студент"
        verbose_name_plural = "Студенты"
    # parent_id = models.ForeignKey(User, on_delete=models.RESTRICT, verbose_name="Идентификатор пользователя", )
    last_name = models.CharField(max_length=150, blank=False)
    first_name = models.CharField(max_length=150, blank=False)
    middle_name = models.CharField(max_length=150, blank=True)

    grade = models.ForeignKey(Grade, null=True, on_delete=models.RESTRICT, verbose_name="Класс ученика")
    #TODO Сделай выборку классов, типо не "7 Г", а чтоб было grade.nums/grade.letters

    parent_id = models.ForeignKey(Parent, on_delete=models.RESTRICT, verbose_name="Идентификатор родителя")
    # teacher_id = models.ForeignKey(Teacher, on_delete=models.RESTRICT, verbose_name="Идентификатор учителя")
    # date_ordered = models.DateTimeField(auto_now_add=True)

    def get_full_name(self):
        return f"{self.last_name} {self.first_name} {self.middle_name}".strip()

    def __str__(self):
        return self.get_full_name() + f": {self.grade} // parent: {self.parent_id} - (id: {self.id})"