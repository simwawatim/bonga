from rest_framework import serializers
from django.contrib.auth.models import User
from base.models import CustomerInfo


class CustomerInfoSerializer(serializers.ModelSerializer):
    created_by = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), required=True, allow_null=False
    )
    updated_by = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), required=True, allow_null=False
    )

    class Meta:
        model = CustomerInfo
        fields = '__all__'
        read_only_fields = ('created_at',)

    def __init__(self, *args, **kwargs):
        """Force all non-read-only fields to be required."""
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if name not in self.Meta.read_only_fields:
                field.required = True
                field.allow_null = False

    def validate_customerTpin(self, value):
        """Ensure customerTpin is unique."""
        qs = CustomerInfo.objects.filter(customerTpin=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("This customerTpin is already in use.")
        return value

    def validate(self, attrs):
        """Ensure all required fields exist."""
        required_fields = ['name', 'address', 'customerTpin', 'created_by', 'updated_by']
        for field in required_fields:
            if field not in attrs or attrs.get(field) in [None, '']:
                raise serializers.ValidationError({field: f"{field.replace('_',' ').capitalize()} is required."})
        return attrs
