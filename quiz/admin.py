from django.contrib import admin

from . models import Themes, User, TeamMembers, TeamNames, Quiz, QuizReviews, QuizInstance, Question, QuestionStep, Participant, Answers, ShowcaseQuiz, QuizTeam, QuizMember

admin.site.register(Themes)
admin.site.register(User)
admin.site.register(TeamMembers)
admin.site.register(TeamNames)
admin.site.register(Quiz)
admin.site.register(QuizReviews)
admin.site.register(QuizInstance)
admin.site.register(Question)
admin.site.register(QuestionStep)
admin.site.register(Participant)
admin.site.register(Answers)
admin.site.register(ShowcaseQuiz)
admin.site.register(QuizTeam)
admin.site.register(QuizMember)