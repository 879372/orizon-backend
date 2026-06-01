from django.db import models
from uuid import uuid4
from core.fields import CompressedImageField

class ProjectUpdate(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, related_name='updates')
    title = models.CharField(max_length=200)
    description = models.TextField()
    phase_category = models.ForeignKey('phases.PhaseCategory', on_delete=models.SET_NULL, null=True, blank=True)
    created_by = models.ForeignKey('accounts.User', on_delete=models.CASCADE)
    video_url = models.URLField(blank=True, null=True, help_text="Link para vídeo (YouTube, Vimeo, etc)")
    video_file = models.FileField(upload_to='updates/videos/%Y/%m/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.project.name} - {self.title}"

class UpdatePhoto(models.Model):
    update = models.ForeignKey(ProjectUpdate, on_delete=models.CASCADE, related_name='photos')
    image = CompressedImageField(upload_to='updates/%Y/%m/', max_width=1200, max_height=1200)
    caption = models.CharField(max_length=200, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return f"Photo for {self.update.title} - {self.caption or self.id}"
