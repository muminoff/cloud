# Django
from django.db import models
from django.contrib.auth.models import User
from django.template import defaultfilters
from django.dispatch import receiver
from django.db.models import signals, Sum, Q
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

# Minio
from minio import Minio
from minio.error import ResponseError

# Misc
import uuid
import itertools

# Choices
CAPACITY_CHOICES = (
    (536870912, '512MB'),
    (1073741824, '1GB'),
)


class Service(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    capacity = models.BigIntegerField(choices=CAPACITY_CHOICES, default=536870912)

    def __str__(self):
        return '{} ({})'.format(
        self.name, defaultfilters.filesizeformat(self.capacity))


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    service = models.OneToOneField(Service, on_delete=models.CASCADE, default=1)
    language = models.CharField(max_length=2, choices=settings.LANGUAGES, default=settings.LANGUAGE_CODE)

    def __str__(self):
        return self.user.username


class Storage(models.Model):
    storage_type = models.SmallIntegerField(default=0)
    owner = models.ForeignKey(Profile, on_delete=models.CASCADE)

    def __str__(self):
        storage_types = {
            1: 'main',
            2: 'trash',
            3: 'thumb'
        }

        return '{0} ({1})'.format(
            storage_types[self.storage_type],
            self.owner)

    @property
    def capacity_quota(self):
        quota_map = {
            1: self.owner.service.capacity,
            2: (self.owner.service.capacity / 10),
            3: self.owner.service.capacity
        }

        return quota_map[self.storage_type]

    @property
    def total_size(self):
        if FileMeta.objects.filter(storage=self).exists():
            return FileMeta.objects.filter(storage=self).aggregate(total_size=Sum('size')).get('total_size')
        
        return 0

    def create_dirmeta(self, parent=None, **kwargs):
        name = kwargs.get('name', None)
        
        if name:
            DirMeta.objects.create(
                storage=self,
                name=name,
                parent=parent)

    def create_filemeta(self, parent=None, **kwargs):
        name = kwargs.get('name', None)
        content_type = kwargs.get('content_type', None)
        size = kwargs.get('size', None)

        if not content_type:
            filename, extension = name.split('.') if '.' in name else (name, name)
            try:
                content_type = MimeContentType.objects.get(extension=extension)
            except MimeContentType.DoesNotExist:
                content_type = MimeContentType.objects.create(name=filename, extension=extension)
        
        if all([name, content_type, size]):
            FileMeta.objects.create(
                storage=self,
                name=name,
                parent=parent,
                content_type=content_type,
                size=size)

    def rename_file(self, parent=None, **kwargs):
        id = kwargs.get('id', None)
        name = kwargs.get('name', None)

        if all([id, name]):
            FileMeta.objects.filter(id=id, storage=self, parent=parent).update(name=name)

    def browse(self, parent=None):
        return list(itertools.chain(
            DirMeta.objects.filter(storage=self, parent=parent),
            FileMeta.objects.filter(storage=self, parent=parent)))

    def documents(self):
        document_mime_types = (
            'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.template',
            'application/vnd.ms-word.document.macroEnabled.12',
            'application/vnd.ms-word.template.macroEnabled.12',
            'application/vnd.ms-excel',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.template',
            'application/vnd.ms-excel.sheet.macroEnabled.12',
            'application/vnd.ms-excel.template.macroEnabled.12',
            'application/vnd.ms-excel.addin.macroEnabled.12',
            'application/vnd.ms-excel.sheet.binary.macroEnabled.12',
            'application/vnd.ms-powerpoint',
            'application/vnd.openxmlformats-officedocument.presentationml.presentation',
            'application/vnd.openxmlformats-officedocument.presentationml.template',
            'application/vnd.openxmlformats-officedocument.presentationml.slideshow',
            'application/vnd.ms-powerpoint.addin.macroEnabled.12',
            'application/vnd.ms-powerpoint.presentation.macroEnabled.12',
            'application/vnd.ms-powerpoint.template.macroEnabled.12',
            'application/vnd.ms-powerpoint.slideshow.macroEnabled.12',
        )
        return FileMeta.objects.filter(
            Q(storage=self),
            Q(content_type__name__in=document_mime_types)).order_by('-modified_at')

    def images(self):
        image_mime_types = (
            'image/gif',
            'image/jpeg',
            'image/png',
            'image/svg+xml',
        )
        return FileMeta.objects.filter(
            Q(storage=self),
            Q(content_type__name__in=image_mime_types)).order_by('-modified_at')

    def audios(self):
        return FileMeta.objects.filter(
            Q(storage=self),
            Q(content_type__name__icontains='audio')).order_by('-modified_at')

    def videos(self):
        return FileMeta.objects.filter(
            Q(storage=self),
            Q(content_type__name__icontains='video')).order_by('-modified_at')


class MetaObject(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    storage = models.ForeignKey(Storage, null=False, blank=False)
    path = models.CharField(max_length=4096, null=True, blank=True)
    created_at = models.DateTimeField(auto_now=True, db_index=True)
    modified_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        abstract = True


class DirMeta(MetaObject):
    name = models.CharField(max_length=4096, null=False, blank=False, db_index=True)
    parent = models.ForeignKey('self', null=True, blank=False, related_name='children')

    class Meta:
        unique_together = ('name', 'parent')
        index_together = ('name', 'parent')
        ordering = ('name',)

    def __str__(self):
        return self.name

    @property
    def content_type(self):
        return None

    @property
    def size(self):
        return 0

    def clean(self):
        if DirMeta.objects.filter(name=self.name, parent__isnull=True).exists():
            raise ValidationError(_('Duplicate directory name.'))

        super(DirMeta, self).clean()

    def save(self, *args, **kwargs):
        self.clean()
        super(DirMeta, self).save(*args, **kwargs)

    @property
    def has_parent(self):
        return self.parent is not None

    @property
    def is_empty(self):
        return not any([
            DirMeta.objects.filter(parent=self).exists(),
            FileMeta.objects.filter(parent=self).exists()])


class MimeContentType(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=4096, db_index=True)
    extension = models.CharField(max_length=16, db_index=True)

    def __str__(self):
        return self.name


class FileMeta(MetaObject):
    name = models.CharField(max_length=4096, db_index=True)
    parent = models.ForeignKey(DirMeta, null=True, blank=False)
    content_type = models.ForeignKey(MimeContentType, null=True, blank=True)
    size = models.BigIntegerField()

    class Meta:
        unique_together = ('name', 'parent')
        index_together = ('name', 'parent')
        ordering = ('name',)

    def __str__(self):
        return self.name

    def clean(self):
        if FileMeta.objects.filter(Q(name=self.name), Q(parent__isnull=True)).exists():
            raise ValidationError(_('Duplicate file name.'))

        super(FileMeta, self).clean()

    def save(self, *args, **kwargs):
        self.clean()
        super(FileMeta, self).save(*args, **kwargs)

    @property
    def has_parent(self):
        return self.parent is not None

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

# Create thumb storage for user profile
@receiver(signals.post_save, sender=Profile)
def create_thumb_storage(sender, instance, created, **kwargs):
    if created:
        Storage.objects.create(storage_type=3, owner=instance)
