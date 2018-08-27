from datetime import timedelta

from rest_framework_xml.renderers import XMLRenderer

from django.db import models, transaction
from django.core.files.base import ContentFile
from django.utils import timezone
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.postgres.fields import JSONField
from django.contrib.contenttypes.models import ContentType

from .tasks import process_comments_to_file_task

ALLOWED_CONTENT_TYPES = ('comment', 'blogpost', 'userprofile')


class BlogPost(models.Model):
    """Some entity 1"""
    pass


class UserProfile(models.Model):
    """Some entity 2"""
    pass


class CommentManager(models.Manager):
    def get_descendants(self, parent, date_from=None, date_to=None):
        parent_id, parent_type_id = parent
        relations = Comment2Comment.objects.filter(
            from_comment__parent_id=parent_id,
            from_comment__parent_type__id=parent_type_id
        ).select_related('to_comment')
        if date_from:
            relations = relations.filter(to_comment__created_at__gte=date_from)
        if date_to:
            relations = relations.filter(to_comment__created_at__lte=date_to)
        return [r.to_comment for r in relations]

    def get_children(self, parent):
        parent_id, parent_type_id = parent
        return self.get_queryset().filter(
            parent_id=parent_id,
            parent_type_id=parent_type_id
        )


class Comment(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    author = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    text = models.TextField()

    parent_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    parent_id = models.PositiveIntegerField(db_index=True)
    parent = GenericForeignKey('parent_type', 'parent_id')

    descendants = models.ManyToManyField('self', symmetrical=False)
    children = GenericRelation(
        'self', content_type_field='parent_type', object_id_field='parent_id'
    )

    objects = CommentManager()

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.text[:100]

    def save(self, *args, **kwargs):
        if self.pk is None:
            with transaction.atomic():
                super().save()
        else:
            super().save()

    def get_entity(self):
        return self.get_root().parent

    def get_root(self):
        content_type = ContentType.objects.get_for_model(Comment)
        if self.parent_type_id != content_type.id:
            return self
        return self.get_ancestors().exclude(
            parent_type=content_type
        ).get()

    def get_ancestors(self, include_self=False):
        queryset = self._meta.default_manager.filter(descendants=self)
        if include_self:
            queryset |= self._meta.default_manager.filter(id=self.id)
            queryset = queryset.distinct()
        return queryset

    def as_data(self):
        return {
            'id': self.id,
            'created_at': str(self.created_at),
            'author_id': self.author_id,
            'parent_id': self.parent_id,
            'text': self.text
        }


Comment2Comment = Comment.descendants.through


class CommentLog(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    comment_id = models.PositiveIntegerField()
    event = models.CharField(max_length=10)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, null=True)
    changes = JSONField(default=dict)

    class Meta:
        ordering = ['-created_at']

    @classmethod
    def push(cls, event, *, user=None, instance=None, update=None):
        changes = {}
        if instance and update and instance.text != update['text']:
            changes['before'] = {'text': instance.text}
            changes['after'] = {'text': update['text']}
        cls.objects.create(user=user, event=event, comment_id=instance.id, changes=changes)


class CommentsAsFileTaskQuerySet(models.QuerySet):
    def create_task(self, file_format='xml', author_id=None, entity_id=None, entity_type_id=None,
                    date_from=None, date_to=None):
        assert author_id or entity_id and entity_type_id
        self.cleanup()
        params = {
            'file_format': file_format,
            'author_id': author_id,
            'entity_id': entity_id,
            'entity_type_id': entity_type_id,
            'date_from': date_from,
            'date_to': date_to,
        }
        task = self.filter(**params).first()
        created = False
        if task is None:
            task = self.create(**params)
            created = True
            process_comments_to_file_task.delay(task.id)
        return created, task

    def cleanup(self):
        self.filter(
            created_at__lt=timezone.now() - timedelta(seconds=self.model.EXPIRE_TIME)
        ).delete()


class CommentsAsFileTask(models.Model):
    EXPIRE_TIME = 60 * 60  # seconds
    FILE_FORMAT_CHOICES = (
        ('xml', 'Xml'),
        ('json', 'Json')
    )
    CONTENT_TYPES = {
        'xml': 'text/xml',
        'json': 'application/json'
    }

    created_at = models.DateTimeField(auto_now_add=True)
    author_id = models.PositiveIntegerField(blank=True, null=True)
    entity_id = models.PositiveIntegerField(blank=True, null=True)
    entity_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, blank=True, null=True)
    date_from = models.DateField(blank=True, null=True)
    date_to = models.DateField(blank=True, null=True)
    file_format = models.CharField(max_length=10, choices=FILE_FORMAT_CHOICES)
    file = models.FileField(blank=True, null=True, upload_to='comments/')

    objects = CommentsAsFileTaskQuerySet.as_manager()

    class Meta:
        ordering = ['-created_at']

    @property
    def ready(self):
        return bool(self.file)

    @property
    def file_content_type(self):
        return self.CONTENT_TYPES.get(self.file_format)

    def prepare_file(self):
        renderer = self.get_renderer()
        data = [c.as_data() for c in self.get_comments()]
        self.file.save(
            f'comment-{self.id}.{self.file_format}',
            ContentFile(renderer.render(data))
        )

    def get_renderer(self):
        if self.file_format == 'xml':
            return XMLRenderer()
        if self.file_format == 'json':
            pass
        raise Exception('Undefined format type')

    def get_comments(self):
        if self.author_id:
            comments = Comment.objects.filter(author_id=self.author_id)
            if self.date_from:
                comments = comments.filter(created_at__gte=self.date_from)
            if self.date_to:
                comments = comments.filter(created_at__lte=self.date_to)
            return comments
        if self.entity_id and self.entity_type_id:
            return Comment.objects.get_descendants(
                (self.entity_id, self.entity_type_id),
                date_from=self.date_from,
                date_to=self.date_to
            )
        raise Exception('Wrong task params')


class Subscription(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    entity_id = models.PositiveIntegerField()
    entity_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    entity = GenericForeignKey('entity_type', 'entity_id')

    class Meta:
        unique_together = ('user', 'entity_id', 'entity_type')

    def send_event(self, data):
        # Отправка события через какой-то бэкенд
        print(data)


@receiver(models.signals.post_save, sender=Comment)
def comment_create_handler(sender, instance, created, **kwargs):
    if created:
        if isinstance(instance.parent, Comment):
            ancestors = list(instance.parent.get_ancestors(include_self=True).values_list('id', flat=True))
            ancestors.append(instance.id)
        else:
            ancestors = [instance.id]
        Comment2Comment.objects.bulk_create([
            Comment2Comment(from_comment_id=aid, to_comment_id=instance.id)
            for aid in ancestors
        ])


@receiver([models.signals.post_save, models.signals.pre_delete], sender=Comment)
def comment_change_handler(sender, instance, **kwargs):
    entity = instance.get_entity()
    subscriptions = Subscription.objects.filter(
        entity_id=entity.id,
        entity_type=ContentType.objects.get_for_model(entity._meta.model)
    )
    created = kwargs.get('created')
    if created is None:
        event = 'DELETE'
    else:
        event = 'CREATED' if created else 'UPDATED'
    for subscription in subscriptions:
        subscription.send_event({'event': event, 'payload': instance.as_data()})
