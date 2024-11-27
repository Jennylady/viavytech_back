from django.db import models
from apps.users.models import User
from django.utils import timezone

class FileDF(models.Model):
    id_file = models.AutoField(primary_key=True)
    file = models.FileField(upload_to='forum/filess/')

    def __str__(self):
        return self.file.name.split('/')[-1]

    class Meta:
        db_table = 'file_forum'

class ImageDF(models.Model):
    id_image = models.AutoField(primary_key=True)
    image = models.ImageField(upload_to='forum/images/')

    def __str__(self):
        return self.image.name.split('/')[-1]
    
    class Meta:
        db_table = 'image_forum'
        

def default_created_at():
    return timezone.localtime(timezone.now())

class PublicationForum(models.Model):
    id_publication_forum = models.AutoField(primary_key=True)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="publicationF")
    contenu = models.TextField()
    files = models.ManyToManyField(FileDF, related_name="publicationF")
    images = models.ManyToManyField(ImageDF, related_name="publicationF")
    is_anonymous = models.BooleanField(default=False)
    likes = models.ManyToManyField(User, related_name="publication_like")
    dislikes = models.ManyToManyField(User, related_name="publication_dislike")
    created_at = models.DateTimeField(default=default_created_at)
    
    def __str__(self):
        return self.contenu
    
    class Meta:
        db_table = "publication_forum"

class DiscussionForum(models.Model):
    id_discussion_forum = models.AutoField(primary_key=True)
    membres = models.ManyToManyField(User, related_name='discussionsF')
    publicationF = models.ForeignKey(PublicationForum, on_delete=models.CASCADE, related_name="comments")
    profile = models.ImageField(upload_to='forum/profiles/groupes/', default='forum/profiles/groupes/default.jpg')
    created_at = models.DateTimeField(default=default_created_at)


    class Meta:
        db_table = 'discussionforum'

    def __str__(self):
        return str(self.id_discussion_forum)

class MessageDF(models.Model):
    id_messageDF = models.AutoField(primary_key=True)
    discussionF = models.ForeignKey(DiscussionForum, related_name='messages', on_delete=models.CASCADE)
    contenu = models.TextField(null=True, blank=True)
    sender = models.ForeignKey(User, related_name='sender', on_delete=models.CASCADE)
    is_anonymous=models.BooleanField(default=False)
    likes = models.ManyToManyField(User,related_name='messageDF_likes')
    dislikes = models.ManyToManyField(User,related_name='messageDF_dislikes')
    files = models.ManyToManyField(FileDF,related_name="messageDF")
    images = models.ManyToManyField(ImageDF, related_name="messageDF")
    created_at = models.DateTimeField(default=default_created_at)


    class Meta:
        db_table = 'message'