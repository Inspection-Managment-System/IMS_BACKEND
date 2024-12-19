from rest_framework import serializers


class ManyToManyRelatedFieldSerializer(serializers.RelatedField):
    def __init__(self, **kwargs):
        self.serializer = kwargs.pop("serializer", None)
        if self.serializer is not None and not issubclass(
            self.serializer, serializers.Serializer
        ):
            raise TypeError('"serializer" is not a valid serializer class')

        super().__init__(**kwargs)

    def to_representation(self, value):
        if self.serializer:
            return [
                self.serializer(instance, context=self.context).data
                for instance in value.all()
            ]
        return super().to_representation(value)

    def to_internal_value(self, data):
        queryset = self.get_queryset()
        try:
            if isinstance(data, list):
                return queryset.filter(pk__in=data)
            return queryset.get(pk=data)
        except queryset.model.DoesNotExist:
            raise serializers.ValidationError(
                f'Invalid pk "{data}" - object does not exist.'
            )
