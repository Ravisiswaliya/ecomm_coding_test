from rest_framework import serializers
from rest_framework.fields import ReadOnlyField
from uauth.models import Account, Product


class LoginSerializer(serializers.Serializer):
    email = serializers.CharField(max_length=128)
    password = serializers.CharField(max_length=128)


class SellerSerializer(serializers.ModelSerializer):

    class Meta:
        model = Account
        fields = ['id', 'email', 'name', 'contact', 'password', "role_type"]
        read_only_fields = ("role_type", )

    def to_representation(self, instance):
        data = super(SellerSerializer, self).to_representation(instance)
        del data['password']
        return data


class SellerInfoSerializer(serializers.ModelSerializer):

    class Meta:
        model = Account
        fields = ['name', ]


class ProductSerializer(serializers.ModelSerializer):
    seller = SellerInfoSerializer(read_only=True)

    class Meta:
        model = Product
        fields = ["id", "seller", "product_name", "product_description", "total_quantity",
                  "sold_cout", "remaining_items", "product_price"]

        read_only_fields = ("seller", "remaining_items")


class SellProductSerializer(serializers.ModelSerializer):
    seller = SellerInfoSerializer(read_only=True)

    class Meta:
        model = Product
        fields = ["id", "seller", "product_name", "product_description", "total_quantity",
                  "sold_cout", "remaining_items" ]

        read_only_fields = ("seller", "product_name", "product_description",
                            "total_quantity", "remaining_items")
