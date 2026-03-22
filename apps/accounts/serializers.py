from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User, UserSkill, Resume


class UserSkillSerializer(serializers.ModelSerializer):
    class Meta:
        model  = UserSkill
        fields = ['id', 'name', 'level', 'category', 'order']


class ResumeSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Resume
        fields = ['id', 'file', 'original_filename', 'uploaded_at']
        read_only_fields = ['original_filename', 'uploaded_at']


class UserSerializer(serializers.ModelSerializer):
    skills     = UserSkillSerializer(many=True, read_only=True)
    full_name  = serializers.CharField(read_only=True)
    has_resume = serializers.SerializerMethodField()

    class Meta:
        model  = User
        fields = [
            'id','email','username','first_name','last_name','full_name',
            'bio','location','profile_photo','phone',
            'github_url','linkedin_url','twitter_url','website_url',
            'skills','has_resume','email_verified',
            'github_id','linkedin_id','google_id','created_at',
        ]
        read_only_fields = ['id','email_verified','created_at']

    def get_has_resume(self, obj):
        return hasattr(obj, 'resume')


class RegisterSerializer(serializers.ModelSerializer):
    password  = serializers.CharField(write_only=True, min_length=8)
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model  = User
        fields = ['email','username','first_name','last_name','password','password2']

    def validate_username(self, value):
        v = value.lower().strip()
        if User.objects.filter(username__iexact=v).exists():
            raise serializers.ValidationError('This username is already taken.')
        if len(v) < 3:
            raise serializers.ValidationError('Username must be at least 3 characters.')
        return v

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError('An account with this email already exists.')
        return value.lower()

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError({'password2': 'Passwords do not match.'})
        return data

    def create(self, validated_data):
        validated_data.pop('password2')
        return User.objects.create_user(**validated_data)


class LoginSerializer(serializers.Serializer):
    email    = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(username=data['email'].lower(), password=data['password'])
        if not user:
            raise serializers.ValidationError('Invalid email or password.')
        if not user.is_active:
            raise serializers.ValidationError('This account has been disabled.')
        data['user'] = user
        return data


class UpdateProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model  = User
        fields = ['first_name','last_name','bio','location','phone',
                  'github_url','linkedin_url','twitter_url','website_url']


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, min_length=8)

    def validate_old_password(self, value):
        if not self.context['request'].user.check_password(value):
            raise serializers.ValidationError('Current password is incorrect.')
        return value
