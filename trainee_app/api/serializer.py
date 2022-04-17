from rest_framework import serializers
from trainee_app.models import TraineeDB
from sport_type_app.api.serializer import SportTypeSerializer
from person_app.api.serializer import PersonSerializer,PersonRelatedField
from person_app.models import PersonDB
from sport_type_app.models import SportTypeDB
from datetime import date
from person_app.models import PersonDB


class TraineeSerializer(serializers.ModelSerializer):
    person = PersonSerializer(many=False,read_only=True)
    # person = PersonRelatedField()
    # person2 = serializers.SerializerMethodField("get_person2")
    # person = serializers.RelatedField(source='TraineeDB', read_only=True)
    # person = serializers.CharField(read_only=True)


    class Meta:
        model = TraineeDB
        fields = "__all__"
        # read_only_fields = ["person",]
        # depth = 1

    # def save(self):
    #     self.validated_data
    # def create(self, validated_data):
    #     person = validated_data.pop("person",None)
    #     instance = self.Meta.model(**validated_data)
    #     instance.save()
    #     instance.person.add(*person)
    #     instance.save()
    #     return instance
    # #
    # def get_person2(self,obj):
    #     serializer = PersonSerializer(obj.person)
    #     return serializer.data
    #
    # def create(self, validated_data):
    #     # persons = validated_data.get('person')
    #     person = validated_data.pop('person')
    #     fav_sport = validated_data.pop('fav_sport')
    #     trainee = TraineeDB.objects.create(person=person, **validated_data)
    #     for fs in fav_sport:
    #         trainee.fav_sport.add(fs)
    #     return trainee
    #     return TraineeDB.objects.create(**validated_data)
    #     # fav_sports = validated_data.pop('sport_type')
    #     persons = validated_data.get('person')
    #
    #     # for fav_sport_data in fav_sports:
    #     #     fs = PersonDB.objects.create(**fav_sport_data)
    #     # per1 = PersonSerializer(persons)
    #     # per = PersonDB.objects.create(**persons)
    #     # validated_data.update({'person': per.pk})
    #     # train = TraineeDB.objects.create(**validated_data)
    #     # return train
    #     for person_data in persons:
    #         per = PersonDB.objects.create(*person_data)
    #     validated_data.update({'person': per.pk})
    #     train = TraineeDB.objects.create(**validated_data)
    #     return train
    #
    # def update(self, instance, validated_data):
    #     person_data = validated_data.pop('person')
    #     fav_sports = validated_data.pop('fav_sport')
    #     instance = super(TraineeSerializer, self).update(instance, validated_data)
    #
    #     # Unless the application properly enforces that this field is
    #     # always set, the following could raise a `DoesNotExist`, which
    #     # would need to be handled.
    #     person = instance.person
    #     fav_sport = instance.fav_sport
    #
    #     instance.person = validated_data.get('person', instance.person)
    #     instance.fav_sport = validated_data.get('fav_sport', instance.fav_sport)
    #
    #
    #     for fav_sport in fav_sports:
    #         fav_sport_qs = SportTypeDB.objects.filter(name__iexact=fav_sport['name'])
    #
    #         if fav_sport_qs.exists():
    #             fs = fav_sport_qs.first()
    #         else:
    #             fs = SportTypeDB.objects.create(**fav_sport)
    #
    #         instance.fav_sport.add(fs)
    #
    #     return instance

        # instance.save()
        #
        # profile.is_premium_member = profile_data.get(
        #     'is_premium_member',
        #     profile.is_premium_member
        # )
        # profile.has_support_contract = profile_data.get(
        #     'has_support_contract',
        #     profile.has_support_contract
        #  )
        # profile.save()

        # return instance