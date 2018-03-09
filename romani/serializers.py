from rest_framework import serializers
from romani.models import Producte, Etiqueta, TipusProducte, UserProfile, Comanda, Productor
from django.contrib.auth.models import User


class ProducteSerializer(serializers.ModelSerializer):

    # formats_nom = serializers.RelatedField(source='formats', read_only=True)
    # formats = serializers.StringRelatedField(many=True)
    class Meta:
        model = Producte
        depth = 0
        fields = ('pk', 'nom', 'etiqueta', 'foto', 'productor', 'thumb', 'text_curt', 'formats')

class ProductorSerializer(serializers.ModelSerializer):

    # formats_nom = serializers.RelatedField(source='formats', read_only=True)
    # formats = serializers.StringRelatedField(many=True)
    class Meta:
        model = Productor
        depth = 0
        fields = "__all__"


class EtiquetaSerializer(serializers.ModelSerializer):

    # formats_nom = serializers.RelatedField(source='formats', read_only=True)
    # formats = serializers.StringRelatedField(many=True)
    class Meta:
        model = Etiqueta
        depth = 0
        fields = ('pk', 'nom', 'img')

class FormatSerializer(serializers.ModelSerializer):

    # formats_nom = serializers.RelatedField(source='formats', read_only=True)
    # formats = serializers.StringRelatedField(many=True)
    class Meta:
        model = TipusProducte
        depth = 0
        fields = ('pk', 'nom', 'preu', 'productor', 'producte')


class UserProfileSerializer(serializers.ModelSerializer):

    # formats_nom = serializers.RelatedField(source='formats', read_only=True)
    # formats = serializers.StringRelatedField(many=True)
    class Meta:
        model = UserProfile
        depth = 1
        fields = "__all__"
            # ('pk', 'nom', 'etiqueta', 'foto', 'productor', 'thumb', 'text_curt', 'formats')

class ComandaSerializer(serializers.ModelSerializer):

    # formats_nom = serializers.RelatedField(source='formats', read_only=True)
    # formats = serializers.StringRelatedField(many=True)
    class Meta:
        model = Comanda
        depth = 1
        fields = "__all__"