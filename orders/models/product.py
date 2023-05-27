from django.db import models

from classes.models.meal_features import MealCategory
from common.models import DateTimeFieldsModel
from decimal import Decimal


class Product(DateTimeFieldsModel):
    """ Модель товара. """

    class Meta:
        db_table = "products"
        verbose_name = "Товар"
        verbose_name_plural = "Товары"

    name = models.CharField('Название товара', max_length=256, db_index=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    grams = models.IntegerField('Развесовка товара', null=True)
    description = models.CharField(max_length=500, null=True)

    meal_category = models.ForeignKey(MealCategory, default=1, on_delete=models.PROTECT)

    image = models.ImageField(upload_to="static/images/%d/%m/%Y", null=True, blank=True)

    def __str__(self):
        return f"{self.name} (ID:{self.id})"

    @property
    def imageURL(self):
        try:
            url = self.image.url
        except:
            url = ''
        return url

    # def save(self):
    #     # Opening the uploaded image
    #     im = Image.open(self.image)
    #
    #     output = BytesIO()
    #
    #     original_width, original_height = im.size
    #     # aspect_ratio = round(original_width / original_height)
    #     # desired_height = 100  # Edit to add your desired height in pixels
    #     # desired_width = desired_height * aspect_ratio
    #
    #     # Resize/modify the image
    #     im = im.resize((original_width, original_height))
    #
    #     # after modifications, save it to the output
    #     im.save(output, format='JPEG', quality=90)
    #     output.seek(0)
    #
    #     # change the imagefield value to be the newley modifed image value
    #     self.image = InMemoryUploadedFile(output, 'ImageField', "%s.jpg" % self.image.name.split('.')[0], 'image/jpeg',
    #                                       sys.getsizeof(output), None)
    #
    #     super(Product, self).save()

    # def save(self):
    #     # if not self.id:
    #     #     self.image = self.compress_image(self.image)
    #
    #     #self.image = self.compress_image(self.image)
    #
    #     super(Product, self).save()

    # @staticmethod
    # def compress_image(image):
    #     img = Image.open(image).quantize(colors=256, method=Image.FASTOCTREE)#.convert("RGB")
    #     im_io = BytesIO()
    #
    #     if image.name.split('.')[1] == 'jpeg' or image.name.split('.')[1] == 'jpg':
    #         img.save(im_io, format='jpeg', optimize=True, quality=90)
    #         new_image = File(im_io, name="%s.jpeg" % image.name.split('.')[0], )
    #     else:
    #         img.save(im_io, format='png', optimize=True, quality=90)
    #         new_image = File(im_io, name="%s.png" % image.name.split('.')[0], )
    #
    #     return new_image
