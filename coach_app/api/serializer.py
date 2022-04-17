from rest_framework import serializers
from coach_app.models import CoachDB
from person_app.models import PersonDB
from rating_app.api.serializer import RatesSerializer
from person_app.api.serializer import PersonSerializer
from django.shortcuts import get_object_or_404


class CoachSerializer(serializers.ModelSerializer):
    person = PersonSerializer(read_only=True)
    rates = serializers.SerializerMethodField()


    class Meta:
        model = CoachDB
        fields = "__all__"

    def get_rates(self, obj):
        return RatesSerializer(obj.rates.all(), many=True).data

    # def update(self, instance, validated_data):
    #     # if validated_data.get('person') is not None:
    #     person_data = validated_data.pop('person')
    #     person = get_object_or_404(PersonDB, pk=person_data["id"])
    #     person_serializer = PersonSerializer(person, data=person_data)
    #     if person_serializer.is_valid():
    #         person_serializer.save()

        # instance.user.first_name = user.get('first_name')

        # print("hey")
        # items = validated_data.get('items')
        #
        # for item in items:
        #     item_id = item.get('id', None)
        #     if item_id:
        #         inv_item = InvoiceItem.objects.get(id=item_id, invoice=instance)
        #         inv_item.name = item.get('name', inv_item.name)
        #         inv_item.price = item.get('price', inv_item.price)
        #         inv_item.save()
        #     else:
        #         InvoiceItem.objects.create(account=instance, **item)

        return instance
