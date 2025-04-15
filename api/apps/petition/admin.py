from django.contrib import admin
from .models import Petition


class PetitionAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "mailing_list")
    search_fields = ("name", "email")
    list_filter = ("mailing_list",)
    ordering = ("name",)


admin.site.register(Petition, PetitionAdmin)
