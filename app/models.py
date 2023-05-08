import uuid
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinLengthValidator



class Person(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=100, default='Unknown')
    last_seen = models.DateTimeField(null=True, blank=True)
    pic_count = models.IntegerField(default=0)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='persons')

    def update_location_and_timestamp(self, camera, timestamp):
        self.location = camera.location
        self.last_seen = timestamp
        self.save()

    def __str__(self):
        return self.name

class FacePicture(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name='face_pictures', null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='face_pictures')
    image = models.ImageField(upload_to='face_pictures/')

    def __str__(self):
        return f"{self.person.name if self.person else 'Unclassified'} - {self.id}"

class IPCamera(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    location = models.CharField(max_length=100, default='Unknown')
    ip = models.GenericIPAddressField()
    port = models.PositiveIntegerField()
    connected = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.ip}:{self.port}"
    
class RecognitionEvent(models.Model):
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    camera = models.ForeignKey(IPCamera, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)