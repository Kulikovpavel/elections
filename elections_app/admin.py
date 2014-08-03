from django.contrib import admin
from elections_app.models import Person, Info, Election


def import_data(modeladmin, request, queryset):
  print("hello")



admin.site.add_action(import_data)
admin.site.register(Person)
admin.site.register(Info)
admin.site.register(Election)
