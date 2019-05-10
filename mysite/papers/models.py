from django.db import models

# Create your models here.


class Paper(models.Model):
    paper_id = models.AutoField(primary_key=True)
    title = models.TextField()
    author = models.TextField()
    link = models.TextField()
    re_auth = models.TextField(default='')
    tag = models.CharField(max_length=20, default='')
    re_paper = models.TextField(default='')

    def __str__(self):
        return self.title
