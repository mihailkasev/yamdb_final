import secrets
import string

from django.contrib.auth.hashers import check_password, make_password
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.decorators import action, permission_classes
from rest_framework.exceptions import ValidationError
from rest_framework.filters import SearchFilter
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.tokens import RefreshToken

from reviews.models import Category, Genre, Review, Title
from users.models import User
from .filters import TitleFilter
from .mixins import ModelMixinSet
from .permissions import (Admin, AdminOrRedOnly, CommentPermission,
                          RewiewPermission)
from .serializers import (CategorySerializer, CommentSerializer,
                          EmailSerializer, GenreSerializer, ReviewSerializer,
                          TitleReadSerializer, TitleWriteSerializer,
                          TokenSerializer, UserSerializer)

CODE_LEN = 20

DEFAULT_FROM_EMAIL = 'admin@admin.org'


class CategoryViewSet(ModelMixinSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AdminOrRedOnly]
    filter_backends = (SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'


class GenreViewSet(ModelMixinSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = [AdminOrRedOnly]
    filter_backends = (SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'


class TitleViewSet(ModelViewSet):
    queryset = Title.objects.all()
    permission_classes = [AdminOrRedOnly]
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return TitleReadSerializer
        return TitleWriteSerializer


class ReviewViewSet(ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [RewiewPermission]

    def get_title(self):
        return get_object_or_404(
            Title,
            pk=self.kwargs.get('title_id'))

    def get_queryset(self):
        """Определение queryset класса - отзывы запрашиваемого произведения."""
        return self.get_title().reviews.all()

    def perform_create(self, serializer):
        """Определение автора, произведения по user и title_id запроса."""
        if Review.objects.filter(author=self.request.user,
                                 title=self.get_title()).exists():
            raise ValidationError('Отзыв повторно невозможен')
        serializer.save(author=self.request.user,
                        title=self.get_title())


class CommentViewSet(ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [CommentPermission]

    def get_title(self):
        return get_object_or_404(
            Title,
            pk=self.kwargs.get('title_id')
        )

    def get_review(self):
        return get_object_or_404(
            Review,
            pk=self.kwargs.get('review_id')
        )

    def get_queryset(self):
        """Определение queryset класса - отзывы запрашиваемого произведения."""
        """return self.get_review().comments.all()"""
        review = get_object_or_404(Review, pk=self.kwargs.get('review_id'))
        return review.comments.all()

    def perform_create(self, serializer):
        """Определение автора, произведения по user и title_id запроса."""
        serializer.save(author=self.request.user,
                        review=self.get_review())


@permission_classes([AllowAny])
class signup(APIView):

    def post(self, request):
        serializer = EmailSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data.get('email')
            username = serializer.validated_data.get('username')
            if username == 'me':
                return Response(serializer.errors,
                                status=status.HTTP_400_BAD_REQUEST)
            confirmation_code = ''.join(
                secrets.choice(string.ascii_letters + string.digits)
                for _ in range(CODE_LEN)
            )
            User.objects.get_or_create(
                defaults={'username': username, 'email': email},
                confirmation_code=make_password(confirmation_code))
            send_mail('Токен подтверждения', confirmation_code,
                      DEFAULT_FROM_EMAIL, [email])
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@permission_classes([AllowAny])
class token(APIView):

    def post(self, request):
        serializer = TokenSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data.get('username')
            conf_code = serializer.validated_data.get('confirmation_code')
            user = get_object_or_404(User, username=username)
            if User.objects.filter(
                    username=username).exists() and \
                    check_password(conf_code, user.confirmation_code):
                return Response(get_tokens_for_user(user),
                                status=status.HTTP_200_OK)
            return Response(status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'username'
    permission_classes = [Admin]

    @action(permission_classes=[IsAuthenticated],
            methods=('GET', 'PATCH'),
            url_path='me',
            detail=False)
    def me(self, request, *args, **kwargs):
        user = self.request.user
        if request.method == 'PATCH':
            new_data = request.data.dict()
            if user.role == 'user':
                new_data['role'] = 'user'
            User.objects.filter(id=user.id).update(**new_data)
            updated_user = get_object_or_404(User, id=user.id)
            return Response(UserSerializer(updated_user).data,
                            status=status.HTTP_200_OK)

        return Response(UserSerializer(user).data)


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        'access': str(refresh.access_token),
    }
