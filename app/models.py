from django.db import models

class Person(models.Model):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=100, default='Unknown')
    last_seen = models.DateTimeField(null=True, blank=True)
    pic_count = models.IntegerField(default=0)

    def __str__(self):
        return self.name