
from rest_framework.serializers import ModelSerializer

from orders.models.product import Product


class ProductSerializer(ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'
        # exclude = ['description']

    def to_representation(self, instance):
        rep = super(ProductSerializer, self).to_representation(instance)
        return rep
