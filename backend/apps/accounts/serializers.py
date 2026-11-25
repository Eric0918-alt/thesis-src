from __future__ import annotations

from django.contrib.auth import authenticate
from rest_framework import serializers

from apps.accounts.models import User


class UserProfileSerializer(serializers.ModelSerializer):
    role_label = serializers.CharField(source="get_role_display", read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "role",
            "role_label",
            "real_name",
            "cohort",
            "gender",
            "phone",
            "date_joined",
        ]
        read_only_fields = ["id", "username", "role", "role_label", "date_joined"]


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)
    role = serializers.ChoiceField(choices=User.ROLE_CHOICES, required=True)

    def validate(self, attrs):
        username = attrs["username"].strip()
        password = attrs["password"]
        role = attrs["role"]

        user = authenticate(username=username, password=password)
        if user is None:
            raise serializers.ValidationError("账号或密码错误")
        if not user.is_active:
            raise serializers.ValidationError("该账号已被禁用")
        if user.role != role:
            raise serializers.ValidationError("所选身份与该账号角色不匹配")

        attrs["user"] = user
        return attrs


class StudentRegisterSerializer(serializers.Serializer):
    student_no = serializers.CharField(max_length=64, required=True)
    password = serializers.CharField(min_length=6, write_only=True, required=True)
    confirm_password = serializers.CharField(min_length=6, write_only=True, required=True)
    name = serializers.CharField(max_length=64, required=True)
    cohort = serializers.CharField(max_length=32, required=True)
    gender = serializers.ChoiceField(choices=["男", "女"], required=True)
    phone = serializers.CharField(max_length=20, required=True)

    def validate_student_no(self, value: str) -> str:
        val = value.strip()
        if not val:
            raise serializers.ValidationError("学生学号不能为空")
        if User.objects.filter(username=val).exists():
            raise serializers.ValidationError("该学号已注册")
        return val

    def validate(self, attrs):
        if attrs["password"] != attrs["confirm_password"]:
            raise serializers.ValidationError("两次输入的密码不一致")
        return attrs

    def create(self, validated_data):
        return User.objects.create_user(
            username=validated_data["student_no"],
            password=validated_data["password"],
            role=User.ROLE_STUDENT,
            real_name=validated_data["name"].strip(),
            cohort=validated_data["cohort"].strip(),
            gender=validated_data["gender"],
            phone=validated_data["phone"].strip(),
        )


class TeacherRegisterSerializer(serializers.Serializer):
    teacher_no = serializers.CharField(max_length=64, required=True)
    name = serializers.CharField(max_length=64, required=True)
    password = serializers.CharField(min_length=6, write_only=True, required=True)
    confirm_password = serializers.CharField(min_length=6, write_only=True, required=True)
    gender = serializers.ChoiceField(choices=["", "男", "女"], required=False, allow_blank=True, default="")
    phone = serializers.CharField(max_length=20, required=False, allow_blank=True, default="")

    def validate_teacher_no(self, value: str) -> str:
        val = value.strip()
        if not val:
            raise serializers.ValidationError("教师工号不能为空")
        if User.objects.filter(username=val).exists():
            raise serializers.ValidationError("该教师工号已注册")
        return val

    def validate(self, attrs):
        if attrs["password"] != attrs["confirm_password"]:
            raise serializers.ValidationError("两次输入的密码不一致")
        return attrs

    def create(self, validated_data):
        return User.objects.create_user(
            username=validated_data["teacher_no"],
            password=validated_data["password"],
            role=User.ROLE_TEACHER,
            real_name=validated_data["name"].strip(),
            gender=validated_data.get("gender", ""),
            phone=validated_data.get("phone", "").strip(),
        )


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(min_length=6, required=True, write_only=True)
    confirm_password = serializers.CharField(min_length=6, required=True, write_only=True)

    def validate(self, attrs):
        user = self.context["request"].user
        if not user.check_password(attrs["old_password"]):
            raise serializers.ValidationError("原密码不正确")
        if attrs["new_password"] != attrs["confirm_password"]:
            raise serializers.ValidationError("两次输入的新密码不一致")
        if attrs["old_password"] == attrs["new_password"]:
            raise serializers.ValidationError("新密码不能与原密码相同")
        return attrs


class StudentManageSerializer(serializers.ModelSerializer):
    student_no = serializers.CharField(source="username", max_length=64)
    student_name = serializers.CharField(source="real_name", max_length=64)
    password = serializers.CharField(write_only=True, required=False, allow_blank=True, min_length=6)

    class Meta:
        model = User
        fields = [
            "id",
            "student_no",
            "student_name",
            "cohort",
            "gender",
            "phone",
            "password",
            "date_joined",
        ]
        read_only_fields = ["id", "date_joined"]

    def validate_student_no(self, value: str) -> str:
        val = value.strip()
        qs = User.objects.filter(username=val)
        if self.instance is not None:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("该学号已存在")
        return val

    def create(self, validated_data):
        password = validated_data.pop("password", "") or "123456"
        return User.objects.create_user(
            username=validated_data["username"],
            password=password,
            role=User.ROLE_STUDENT,
            real_name=validated_data.get("real_name", ""),
            cohort=validated_data.get("cohort", ""),
            gender=validated_data.get("gender", ""),
            phone=validated_data.get("phone", ""),
        )

    def update(self, instance, validated_data):
        password = validated_data.pop("password", "")
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance


class TeacherManageSerializer(serializers.ModelSerializer):
    teacher_no = serializers.CharField(source="username", max_length=64)
    teacher_name = serializers.CharField(source="real_name", max_length=64)
    password = serializers.CharField(write_only=True, required=False, allow_blank=True, min_length=6)

    class Meta:
        model = User
        fields = [
            "id",
            "teacher_no",
            "teacher_name",
            "gender",
            "phone",
            "password",
            "date_joined",
        ]
        read_only_fields = ["id", "date_joined"]

    def validate_teacher_no(self, value: str) -> str:
        val = value.strip()
        qs = User.objects.filter(username=val)
        if self.instance is not None:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("该教师工号已存在")
        return val

    def create(self, validated_data):
        password = validated_data.pop("password", "") or "123456"
        return User.objects.create_user(
            username=validated_data["username"],
            password=password,
            role=User.ROLE_TEACHER,
            real_name=validated_data.get("real_name", ""),
            gender=validated_data.get("gender", ""),
            phone=validated_data.get("phone", ""),
        )

    def update(self, instance, validated_data):
        password = validated_data.pop("password", "")
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance
