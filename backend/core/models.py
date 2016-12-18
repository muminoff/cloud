# Django
from django.db import models
from django.contrib.auth.models import User
from django.template import defaultfilters
from django.dispatch import receiver
from django.db.models import signals, Q
from django.conf import settings

# Minio
from minio import Minio
from minio.error import ResponseError

# Misc
import uuid


class Service(models.Model):
    CAPACITY_CHOICES = (
        (536870912, '512MB'),
        (1073741824, '1GB'),
    )
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    capacity = models.BigIntegerField(choices=CAPACITY_CHOICES, default=536870912)

    def __str__(self):
        return "{} ({})".format(
        self.name, defaultfilters.filesizeformat(self.capacity))


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    service = models.OneToOneField(Service, on_delete=models.CASCADE, default=1)
    language = models.CharField(max_length=2, choices=settings.LANGUAGES, default=settings.LANGUAGE_CODE)

    def __str__(self):
        return self.user.username


class StorageMetaObjectQuerySet(models.QuerySet):
    
    def directories(self):
        return DirectoryMetaObject.objects.filter(storage=self)

    def files(self):
        return FileMetaObject.objects.filter(storage=self)


class StorageManager(models.Manager):

    def get_queryset(self):
        return StorageMetaObjectQuerySet(self.model, using=self._db)

    def directories(self):
        return self.get_queryset().directories()

    def files(self):
        return self.get_queryset().files()


class Storage(models.Model):
    storage_type = models.SmallIntegerField(default=0)
    owner = models.ForeignKey(Profile, on_delete=models.CASCADE)

    objects = StorageManager()

    def __str__(self):
        storage_types = {
            1: 'main storage',
            2: 'trash storage'
        }

        return "{0} ({1})".format(
            storage_types[self.storage_type],
            self.owner)

    def create_directory(self, parent=None, **kwargs):
        name = kwargs.get('name')
        
        if name:
            DirectoryMetaObject.objects.create(
                storage=self,
                name=name,
                parent=parent)
        else:
            raise Exception('Not enough parameters to create directory.')

    def create_file(self, parent=None, **kwargs):
        name = kwargs.get('name')
        content_type = kwargs.get('content_type')
        size = kwargs.get('size')
        
        if all((name, content_type, size)):
            FileMetaObject.objects.create(
                storage=self,
                name=name,
                parent=parent,
                content_type=content_type,
                size=size)
        else:
            raise Exception('Not enough parameters to create file.')

    def rename_file(self, parent=None, **kwargs):
        old_name = kwargs.get('old_name')
        new_name = kwargs.get('new_name')
        
        if all((old_name, new_name)):

            if old_name != new_name:
                FileMetaObject.objects.filter(
                    storage=self,
                    name=old_name,
                    parent=parent).update(
                        name=new_name)
        else:
            raise Exception('Not enough parameters to rename file.')


class MetaObject(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    storage = models.ForeignKey(Storage, null=False, blank=False)
    created_at = models.DateTimeField(auto_now=True)
    modified_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True


class DirectoryMetaObject(MetaObject):
    name = models.CharField(max_length=4096, null=False, blank=False)
    parent = models.ForeignKey('self', null=True)

    def __str__(self):
        return self.name

    @property
    def has_parent(self):
        return self.parent is not None

    @property
    def has_children(self):
        return any([
            FileMetaObject.objects.filter(parent=self).exists(),
            DirectoryMetaObject.objects.filter(parent=self).exists()])


class FileMetaObject(MetaObject):
    name = models.CharField(max_length=4096, null=False, blank=False)
    parent = models.ForeignKey(DirectoryMetaObject, null=True)
    content_type = models.CharField(max_length=100, null=False, blank=False)
    size = models.BigIntegerField()

    class Meta:
        unique_together = ('name', 'parent')
        index_together = ["name", "parent"]

    def __str__(self):
        return self.name

# Create user profile
@receiver(signals.post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

# Create main storage for user profile
@receiver(signals.post_save, sender=Profile)
def create_main_storage(sender, instance, created, **kwargs):
    if created:
        Storage.objects.create(storage_type=1, owner=instance)

# Create trash storage for user profile
@receiver(signals.post_save, sender=Profile)
def create_trash_storage(sender, instance, created, **kwargs):
    if created:
        Storage.objects.create(storage_type=2, owner=instance)
