from django.db import models

# Create your models here.
class Person(models.Model):
    name = models.CharField(max_length=20, null=False)
    age= models.IntegerField(null=False)
    
    def __str__(self):
        return f"Person[id={self.pk} name={self.name}, age={self.age}]"
    
class MyStock(models.Model):
    code = models.CharField(max_length=7)
    name = models.CharField(max_length=20)
    reasons = models.TextField()
    
    def __str__(self):
        return f"MyStock[{self.name} ({self.code}) {self.reasons}]"