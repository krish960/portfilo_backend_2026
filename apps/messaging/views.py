from rest_framework import serializers, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import ContactMessage
from apps.portfolios.models import Portfolio


class ContactMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model  = ContactMessage
        fields = ['id', 'sender_name', 'sender_email', 'subject', 'message', 'is_read', 'sent_at']
        read_only_fields = ['id', 'is_read', 'sent_at']


class SendMessageView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, slug):
        portfolio  = get_object_or_404(Portfolio, slug=slug, is_published=True)
        serializer = ContactMessageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(portfolio=portfolio)
            return Response({'message': 'Message sent successfully.'}, status=201)
        return Response(serializer.errors, status=400)


class InboxView(APIView):
    def get(self, request):
        messages     = ContactMessage.objects.filter(portfolio__user=request.user)
        unread_count = messages.filter(is_read=False).count()
        return Response({
            'messages':     ContactMessageSerializer(messages, many=True).data,
            'unread_count': unread_count,
        })


class MessageDetailView(APIView):
    def get_object(self, pk, user):
        return get_object_or_404(ContactMessage, pk=pk, portfolio__user=user)

    def patch(self, request, pk):
        msg         = self.get_object(pk, request.user)
        msg.is_read = True
        msg.save()
        return Response(ContactMessageSerializer(msg).data)

    def delete(self, request, pk):
        self.get_object(pk, request.user).delete()
        return Response(status=204)
