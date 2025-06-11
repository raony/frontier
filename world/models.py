"""Database models for world objects."""

from django.db import models


class HexTile(models.Model):
    """Model storing cube coordinate tiles."""

    q = models.IntegerField()
    r = models.IntegerField()
    s = models.IntegerField()
    terrain = models.CharField(max_length=32, default="plain")

    class Meta:
        unique_together = ("q", "r", "s")

    def __str__(self) -> str:
        return f"HexTile(q={self.q}, r={self.r}, s={self.s})"
