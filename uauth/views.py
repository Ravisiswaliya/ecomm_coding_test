from django.shortcuts import render
from django.db import transaction
from django.db.models import F
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework.exceptions import ValidationError
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny
from django.contrib.auth.hashers import make_password
from uauth.serializers import SellerSerializer, LoginSerializer, ProductSerializer, SellProductSerializer
from uauth.models import Account, Product
from uauth.common import CreateModelMixin, GetListModelMixin, PutUpdateModelMixin, success_response
from uauth.roles import required_role


@csrf_exempt
def index(request):
    template = "index.html"
    context = {}
    return render(request, template, context)


class LoginViewView(GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = (AllowAny, )

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = Account.objects.filter(email=request.data['email']).first()
        if user:
            if not user.check_password(request.data['password']):
                raise ValidationError(
                    detail={'email': ["email or password does not match"]})
        else:
            raise ValidationError(detail={'email': ["email does not exists"]})

        data = SellerSerializer(user, context={'request': request}).data
        # data.pop("password")
        return success_response(message="login successfully", data=data, extra_data={'token': user.get_token()})


class SellerView(CreateModelMixin, GetListModelMixin, GenericAPIView):
    queryset = Account.objects.all()
    serializer_class = SellerSerializer

    def get_queryset(self):
        return super().get_queryset().filter(role_type=Account.SELLER)

    @method_decorator(required_role(Account.FA))
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @transaction.atomic
    @method_decorator(required_role(Account.FA))
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(password=make_password(
            self.request.data['password']), role_type=Account.SELLER, is_active=True)
        # password should be sent to user on mobile or email


class ProductList(GetListModelMixin, GenericAPIView, CreateModelMixin):

    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.role_type == Account.FA:
            qs = qs.filter(seller_id=self.request.query_params.get('seller_id'))
        else:
            qs = qs.filter(seller=self.request.user) 

        return  qs

    #@method_decorator(required_role(Account.FA))
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @transaction.atomic
    @method_decorator(required_role(Account.SELLER))
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(seller=self.request.user)


class SellProduct(PutUpdateModelMixin, GenericAPIView):
    queryset = Product.objects.all()
    serializer_class = SellProductSerializer

    @transaction.atomic
    @method_decorator(required_role(Account.SELLER))
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def perform_update(self, serializer):
        product = serializer.save()  # Product.objects.get(seller=self.request.user, id=id)
        if product.total_quantity == product.sold_cout:
            return None
        product.sold_cout += 1
        product.save()
