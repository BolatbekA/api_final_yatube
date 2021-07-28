from django.shortcuts import get_object_or_404
from rest_framework import viewsets, mixins, permissions, filters
from rest_framework.pagination import LimitOffsetPagination

from api.serializers import PostSerializer, CommentSerializer
from api.serializers import GroupSerializer, FollowSerializer
from posts.models import Post, Group, Follow
from .permissions import AuthorOrReadOnly


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = (AuthorOrReadOnly,)
    pagination_class = LimitOffsetPagination

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (AuthorOrReadOnly,)

    def get_queryset(self):
        post = get_object_or_404(Post, pk=self.kwargs.get('post_id'))
        return post.comments

    def perform_create(self, serializer):
        get_object_or_404(Post, pk=self.kwargs.get('post_id'))
        serializer.save(author=self.request.user)


class ListRetrieveViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin,
                          viewsets.GenericViewSet):
    pass


class GroupViewSet(ListRetrieveViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = (AuthorOrReadOnly,)


class FollowViewSet(viewsets.ModelViewSet):
    queryset = Follow.objects.all()
    serializer_class = FollowSerializer
    permission_classes = (permissions.IsAuthenticated,)
    filter_backends = (filters.SearchFilter)
    search_fields = ('user__username', 'following__username',)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        return self.request.user.following.all()


#     def create(self, request):
#         serializer = FollowSerializer(data=request.data)
#         user = self.request.user
#         follow_obj = serializer.initial_data.get('following')
#         if user.username == follow_obj:
#             raise PermissionDenied('Невозможно подписаться на самого себя')
#         elif Follow.objects.filter(
#             user=user,
#             following=User.objects.get(username=follow_obj)
#         ).exists():
#             raise PermissionDenied('Вы уже подписаны')
#         elif serializer.is_valid():
#             serializer.save(user=user)
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)