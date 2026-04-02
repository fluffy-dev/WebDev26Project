"""
Domain models for user identity: Avatar catalogue and extended Profile.
"""

from django.db import models
from django.contrib.auth.models import User


class Avatar(models.Model):
    """
    Pre-loaded avatar image selectable during registration.

    Avatars are uploaded once by an administrator via Django Admin.
    The image_url field stores the relative path under MEDIA_ROOT.
    """

    name = models.CharField(max_length=64, unique=True)
    image = models.ImageField(upload_to="avatars/")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Avatar"
        verbose_name_plural = "Avatars"

    def __str__(self) -> str:
        return self.name


class Profile(models.Model):
    """
    One-to-one extension of Django's built-in User model.

    total_score is denormalised and updated atomically after every
    completed attempt to avoid expensive aggregation on the leaderboard
    query path.  The db_index flag ensures ORDER BY on total_score
    uses an index scan instead of a sequential scan.
    """

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    avatar = models.ForeignKey(
        Avatar,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="profiles",
    )
    total_score = models.IntegerField(default=0, db_index=True)
    virtual_currency = models.IntegerField(default=0)
    best_wpm = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-total_score"]
        verbose_name = "Profile"
        verbose_name_plural = "Profiles"

    def __str__(self) -> str:
        return f"{self.user.username} — {self.total_score} pts"

    def award(self, points: int, wpm: float) -> None:
        """
        Atomically credit points to total_score and virtual_currency,
        and update best_wpm if the current attempt surpasses the record.

        Using F() expressions prevents lost updates under concurrent
        requests without requiring an explicit SELECT FOR UPDATE.
        """
        from django.db.models import F

        if wpm > self.best_wpm:
            self.best_wpm = wpm

        Profile.objects.filter(pk=self.pk).update(
            total_score=F("total_score") + points,
            virtual_currency=F("virtual_currency") + points,
            best_wpm=models.Case(
                models.When(best_wpm__lt=wpm, then=wpm),
                default=models.F("best_wpm"),
            ),
        )
        self.refresh_from_db()
