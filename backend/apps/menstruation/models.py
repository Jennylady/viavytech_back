from django.db import models

from apps.users.models import User


class Symptom(models.Model):
    id_symptom = models.AutoField(primary_key=True)
    
    TYPE_CHOICES = [
        ('general', 'Général'),
        ('ovulation', 'Ovulation'),
        ('menstrual', 'Menstruel')
    ]
    CATEGORY_CHOICES = [
        ('physique', 'Physique'),
        ('emotion', 'Émotion'),
        ('humeur', 'Humeur')
    ]
    title = models.CharField(max_length=100)
    description = models.TextField()
    symptom_type = models.CharField(max_length=10, choices=TYPE_CHOICES, default='general')
    category = models.CharField(max_length=10, choices=CATEGORY_CHOICES, default='physique')
    
    def __str__(self):
        return f"Symptôme {self.description} - Type: {self.symptom_type}, Catégorie: {self.category}"
    
    class Meta:
        db_table = 'symptom'

class Woman(models.Model):
    REGLE_TYPE = [
        ('regulier','Régulier'),
        ('irregulier', 'Irrégulier')
    ]
    id_woman = models.AutoField(primary_key=True)
    
    user = models.OneToOneField(User,on_delete=models.CASCADE,related_name='woman')
    
    average_cycle_length = models.IntegerField(default=28)
    average_menstruation_duration = models.IntegerField(default=5)
    last_period_date = models.DateField(null=True, blank=True)
    symptoms = models.ManyToManyField(Symptom,related_name='symptoms')
    regle_type = models.CharField(max_length=50, choices=REGLE_TYPE, default='regulier')
    
    def __str__(self):
        return str(self.woman)
    
    def get_cycle(self):
        menstruations = self.menstruations.all().order_by('-start_date')
        if menstruations.count()<2: irregulier_cycle_length = self.average_cycle_length
        else:
            last_date = menstruations.first().start_date
            next_last_date = menstruations[1].start_date
            irregulier_cycle_length = (last_date - next_last_date).days
        return self.average_cycle_length if self.regle_type=='regulier' else irregulier_cycle_length
    
    def update_average_menstruation_length(self):
        menstruations = self.menstruations.all()
        if menstruations.count() > 1:
            total_average_menstruation_duration = 0
            for m in menstruations:
                if not m.end_date is None:
                    total_average_menstruation_duration += abs((m.end_date - m.start_date).days)
            if menstruations.count() == 0:
                self.average_menstruation_duration = 5
            else:
                self.average_menstruation_duration = total_average_menstruation_duration // (menstruations.count())
            self.save()
            
    def update_average_cycle_length(self):
        menstruations = self.menstruations.all()
        if menstruations.count() > 1:
            total_cycle = []
            last_date = None
            for m in menstruations:
                if last_date is not None:
                    total_cycle.append(abs((m.start_date - last_date).days))
                last_date = m.start_date
            if menstruations.count() < 2:
                self.average_cycle_length = 28
            else:
                self.average_cycle_length = sum(total_cycle) // len(total_cycle)
        self.save()
    
    class Meta:
        db_table = 'woman'
      
class SymptomLinkWoman(models.Model):
    id_symptom_link = models.AutoField(primary_key=True)
    woman = models.ForeignKey(Woman, on_delete=models.CASCADE, related_name="symptoms_link_date")
    date = models.DateField()
    symptoms = models.ManyToManyField(Symptom, related_name='symptoms_link_date')
    
    def __str__(self):
        return f'{self.woman} : {self.date} ==> {" , ".join([str(s)for s in self.symptoms])}'
    
    class Meta:
        db_table = 'symptom_link'
    
class Menstruation(models.Model):
    id_menstruation = models.AutoField(primary_key=True)
    woman = models.ForeignKey(Woman, on_delete=models.CASCADE, related_name='menstruations')
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    length = models.IntegerField(blank=True, null=True)
    
    def __str__(self):
        return f"Cycle from {self.start_date} to {self.end_date} (Duration: {self.length} days)"
    
    def save(self, *args, **kwargs):
        if self.end_date:
            self.length = (self.end_date - self.start_date).days
        else:
            self.length = 5
        super().save(*args, **kwargs)

    class Meta:
        db_table = 'menstruation'

class Ovulation(models.Model):
    id_ovulation = models.AutoField(primary_key=True)
    woman = models.ForeignKey(Woman, on_delete=models.CASCADE, related_name='ovulations')
    predicted_ovulation_date = models.DateField()
    fertility_window_start = models.DateField()
    fertility_window_end = models.DateField()
    symptoms = models.ManyToManyField(Symptom, related_name='ovulation_symptoms', blank=True)
    
    def __str__(self):
        return f"Ovulation le {self.predicted_ovulation_date}"

    class Meta:
        db_table = 'ovulation'

class Notification(models.Model):
    id_notification = models.AutoField(primary_key=True)
    woman = models.ForeignKey(Woman, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.message

    class Meta:
        db_table = 'notification'
