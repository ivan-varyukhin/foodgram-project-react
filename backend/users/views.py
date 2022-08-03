from djoser.views import TokenCreateView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST

USER_BLOCKED_MESSAGE = 'Аккаунт заблокирован!'


class TokenCreateNonBlockedUserView(TokenCreateView):
    permission_classes = (AllowAny, )

    def _action(self, serializer):
        if serializer.user.is_not_active:
            return Response(
                {'errors': USER_BLOCKED_MESSAGE},
                status=HTTP_400_BAD_REQUEST,
            )
        return super()._action(serializer)
