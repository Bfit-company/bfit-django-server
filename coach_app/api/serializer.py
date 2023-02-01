from rest_framework import serializers
from coach_app.models import CoachDB
from location_app.api.serializer import LocationSerializer
from location_app.models import LocationDB
from rating_app.api.serializer import RatesSerializer
from person_app.api.serializer import PersonSerializer


class CoachSerializer(serializers.ModelSerializer):
    person = PersonSerializer(read_only=True)
    rates = serializers.SerializerMethodField()
    locations = LocationSerializer(many=True, read_only=True)

    def update(self, instance, validated_data):
        try:
            locations = validated_data.pop('locations')
            if locations:
                instance.locations.clear()
                for location in locations:
                    city = location.get('city')
                    locations_serializer = LocationSerializer(data=location)
                    if locations_serializer.is_valid():
                        location = locations_serializer.save(city=city)
                        if isinstance(location, LocationDB):
                            instance.locations.add(location.id)
                        else:
                            instance.locations.add(location["id"])
        except KeyError as ke:
            print(ke)

        try:
            person = validated_data.pop('person')
            if person:
                super(PersonSerializer, PersonSerializer()).update(instance.person, person)
        except KeyError as ke:
            print(ke)

        super(self.__class__, self).update(instance, validated_data)
        instance.save()
        return instance

    # formatted_address = location.get('formatted_address')
    # long = location.get('long')
    # lat = location.get('lat')
    #
    # location_result = LocationDB.objects.filter(city=city,
    #                                             formatted_address=formatted_address,
    #                                             long=long,
    #                                             lat=lat)
    # if location_result.exists():
    #     location_pk = list(location_result)[0].pk
    #     location_pk
    def to_representation(self, instance):
        data = super(CoachSerializer, self).to_representation(instance)
        person = data.pop("person")
        coach = data
        person.update({"coach": coach})
        return person

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
    # def save(self, **validated_data):
    #     locations = validated_data.get("locations")
    #     instance = super(CoachSerializer, self).create(validated_data)
    #     for item in locations:
    #         instance.locations.add(item)
    #
    #     instance.save()


