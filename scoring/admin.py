from django.contrib import admin
from scoring.models import Fighter, Match, Score


class ScoreAdmin(admin.ModelAdmin):
    list_filter = ('match', 'fighter', 'judge')


admin.site.register(Score, ScoreAdmin)
admin.site.register(Match)
admin.site.register(Fighter)
