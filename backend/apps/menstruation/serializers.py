from rest_framework import serializers
from .models import Woman, Menstruation, Ovulation, Symptom, Notification, SymptomLinkWoman

from datetime import timedelta

class MenstruationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Menstruation
        fields = ['id_menstruation', 'start_date', 'end_date', 'length']

class SymptomSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Symptom
        fields = ['id_symptom', 'description','title','category']
        
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        exclude_category = self.context.get("exclude_category",False)
        if exclude_category:
            representation.pop('category',None)
        return representation

    
class SymptomLinkWomanSerializer(serializers.ModelSerializer):
    date = serializers.SerializerMethodField()
    symptoms = SymptomSerializer(many=True, read_only=True)
    
    class Meta:
        model = SymptomLinkWoman
        fields = ['id_symptom_link','woman','date','symptoms']
        
    def date(self, obj):
        return obj.date.strftime("%Y-%m-%d")

class OvulationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ovulation
        fields = ['id_ovulation', 'predicted_ovulation_date', 'fertility_window_start', 'fertility_window_end']

class WomanSerializer(serializers.ModelSerializer):
    menstruations = serializers.SerializerMethodField()
    ovulations = serializers.SerializerMethodField()
    symptoms = SymptomSerializer(many=True, read_only=True)
    symptoms_link_date = SymptomLinkWomanSerializer(many=True, read_only=True)

    class Meta:
        model = Woman
        fields = ['id_woman', 'average_cycle_length', 'average_menstruation_duration', 'regle_type', 'last_period_date', 'menstruations', 'ovulations', 'symptoms', 'symptoms_link_date']
        
    def get_menstruations(self,obj):
        return MenstruationSerializer(obj.menstruations.all().order_by('start_date'),many=True).data
    
    def get_ovulations(self,obj):
        return OvulationSerializer(obj.ovulations.all().order_by('predicted_ovulation_date'),many=True).data   
    
    def to_representation(self, instance):
        only_menstruations = self.context.get('only_menstruations',False)
        last_info = self.context.get('last_info', False)
        representation = super().to_representation(instance)
        if only_menstruations:
            representation.pop('ovulations', None)
            representation.pop('symptoms', None)
        if last_info:
            representation['ovulation_predict'] = OvulationSerializer(instance.ovulations.order_by("predicted_ovulation_date").last()).data
            last_menstruation = instance.menstruations.order_by('-start_date').first()
            predicted_start = last_menstruation.start_date + timedelta(days=instance.average_cycle_length)
            predicted_end = predicted_start + timedelta(days=instance.average_menstruation_duration)
            representation['menstruation_predict'] = {
                "start_date": predicted_start,
                "end_date": predicted_end
            }
            representation['menstruation_last'] = MenstruationSerializer(last_menstruation).data
            representation.pop('ovulations', None)
            representation.pop('mensturations', None)
        return representation

class NotificationSerializer(serializers.ModelSerializer):
    created_at = serializers.SerializerMethodField()
    class Meta:
        model = Notification
        fields = ['id_notification', 'message', 'created_at']
        
    def get_created_at(self, obj):
        return obj.created_at.strftime("%d-%m-%Y")