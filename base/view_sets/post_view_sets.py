from rest_framework import viewsets
from rest_framework import permissions


from base.serializers.post_serializers import PostSerializer
from base.models.post_models import Post

class PostViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]