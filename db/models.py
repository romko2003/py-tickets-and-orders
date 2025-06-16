from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from typing import Any


class Movie(models.Model):
    title = models.CharField(max_length=255, db_index=True)
    description = models.TextField()
    genres = models.ManyToManyField("Genre", related_name="movies")

    def __str__(self):
        return self.title


class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"<Order: {self.created_at}>"


class Ticket(models.Model):
    movie_session = models.ForeignKey("MovieSession", on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    row = models.IntegerField()
    seat = models.IntegerField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["row", "seat", "movie_session"],
                name="unique_ticket_per_session"
            )
        ]

    def clean(self) -> None:
        max_rows = self.movie_session.cinema_hall.rows
        max_seats = self.movie_session.cinema_hall.seats_in_row

        errors = {}

        if not (1 <= self.row <= max_rows):
            errors["row"] = [
                f"row number must be in available range: "
                f"(1, rows): (1, {max_rows})"
            ]
        if not (1 <= self.seat <= max_seats):
            errors["seat"] = [
                f"seat number must be in available range: "
                f"(1, seats_in_row): (1, {max_seats})"
            ]
        if errors:
            raise ValidationError(errors)

    def save(self, *args: Any, **kwargs: Any) -> None:
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return (
            f"<Ticket: {self.movie_session.movie.title} "
            f"{self.movie_session.show_time} "
            f"(row: {self.row}, seat: {self.seat})>"
        )


class Actor(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}"


class Genre(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name