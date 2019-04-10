from django.db import models

# Create your models here.

class Paper(models.Model):
    paper_id = models.AutoField(primary_key=True)
    title = models.TextField()
    auther = models.TextField()
    link = models.TextField()

    def __str__(self):
        return self.title
