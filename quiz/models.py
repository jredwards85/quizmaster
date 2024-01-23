from django.db import models
from django.contrib.auth.models import AbstractUser


class Themes(models.Model):
    class Meta:
            verbose_name_plural = 'Themes'
    name = models.CharField('Theme name', blank=True, null=True, default="", max_length=255)
    text = models.CharField('Cover image text', blank=True, null=True, default="", max_length=255)
    image = models.ImageField(upload_to='covers/', null=True, blank=True)
    status = models.BooleanField('Active status', default=False, unique=True)

    def delete(self, *args, **kwargs):     
        self.image.delete()
        super().delete(*args, **kwargs)


# Default password for QuizInstance
def generate_unique_string():
    import uuid
    return str(uuid.uuid4())

class User(AbstractUser):

    public_host_name = models.CharField('Public Host Name', blank=True, null=True, default="", max_length=50)
    last_activity = models.DateTimeField(null=True, blank=True)
    profile = models.IntegerField('Initial profile steps', default=0)

    def __str__(self):
        return self.username


class TeamMembers(models.Model):
    class Meta:
        verbose_name_plural = 'TeamMembers'
    name = models.CharField('Member name', blank=True, null=True, default="", max_length=50)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='team_members')

    def delete(self, *args, **kwargs):     
        self.avatar.delete()
        super().delete(*args, **kwargs)

    def __str__(self):
        return str(self.name) if self.name is not None else str(self.user)


class TeamNames(models.Model):
    class Meta:
        verbose_name_plural = 'TeamNames'
    name = models.CharField('Team name', blank=True, null=True, default="", max_length=50)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='team_names')

    def __str__(self):
        return str(self.name) if self.name is not None else str(self.user)
    

class Quiz(models.Model):
    class Meta:
        verbose_name_plural = 'Quiz'
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField('Quiz title', max_length=200)
    title_url = models.CharField('Quiz title URL', max_length=255)
    description = models.TextField('Quiz description', blank=True, null=True, default="")
    category1 = models.CharField('Category 1', max_length=30, blank=True, null=True, default="")
    category2 = models.CharField('Category 2', max_length=30, blank=True, null=True, default="")
    category3 = models.CharField('Category 3', max_length=30, blank=True, null=True, default="")
    category4 = models.CharField('Category 4', max_length=30, blank=True, null=True, default="")
    featured = models.BooleanField('Featured status', default=False)
    private = models.BooleanField('Marked as private (no for public hosting)', default=False)
    complete = models.BooleanField('Complete status', default=False)
    edit_only = models.BooleanField('Editing only', default=False)
    hidden = models.BooleanField('Hidden', default=False)
    created_on = models.DateTimeField(auto_now_add=True)
    rating = models.IntegerField('Rating', default=0) #TODO: Do we need this field?

    def get_question_count(self):
        return self.question_set.count()

    def __str__(self):
        return self.title
    
class QuizReviews(models.Model):
    class Meta:
        verbose_name_plural = 'QuizReviews'
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    rating = models.IntegerField('Rating', default=0)

    def __str__(self):
        return f"{self.user} rated {self.quiz.title}: {self.rating} stars"
    

class QuizInstance(models.Model):
    class Meta:
        verbose_name_plural = 'QuizInstance'
    host = models.ForeignKey(User, related_name='host', on_delete=models.CASCADE, blank=True, null=True)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    quiz_step = models.IntegerField('step', default="0")
    question_number = models.IntegerField('Question number', default="1")
    password = models.CharField('Password', blank=True, null=True, default=generate_unique_string, max_length=50)
    hosted_at = models.DateTimeField('Hosted at', auto_now_add=True)
    completed_on = models.DateTimeField('Completed at', blank=True, null=True)
    archived = models.BooleanField('Archived status', default=False)
    play_type = models.IntegerField('Play Type', default="0")
    multichoice_only = models.BooleanField('Multichoice exclusive', default=False)
    local_mode = models.BooleanField('Local Mode', default=False)

    def __str__(self):
        return f"{self.id}: {self.quiz.title}"

class ShowcaseQuiz(models.Model):
    class Meta:
        verbose_name_plural = 'ShowcaseQuiz'
    quiz_instance = models.ForeignKey(QuizInstance, on_delete=models.CASCADE)
    
    def __str__(self):
            return f"Showcase with ID: {self.quiz_instance.id}. Quiz title: {self.quiz_instance.quiz.title}"


class Question(models.Model):
    class Meta:
        verbose_name_plural = 'Question'
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    question_text = models.CharField('Question text', max_length=200, null=True, blank=True)
    question_type = models.IntegerField('Question type', null=True, blank=True)
    answer1 = models.CharField('Answer 1', max_length=200, null=True, blank=True)
    answer2 = models.CharField('Answer 2', max_length=200, null=True, blank=True)
    answer3 = models.CharField('Answer 3', max_length=200, null=True, blank=True)
    answer4 = models.CharField('Answer 4', max_length=200, null=True, blank=True)
    correct_answer = models.IntegerField('Correct answer', null=True, blank=True)
    question_number = models.IntegerField('Question number', null=True, blank=True)
    image = models.ImageField(upload_to='question-images/', null=True, blank=True)
    audio = models.FileField(upload_to='question-audio/', null=True, blank=True)

    def delete(self, *args, **kwargs):     
        self.image.delete()
        self.audio.delete()
        super().delete(*args, **kwargs)

    def __str__(self):
        return f"ID: {self.id} - {self.quiz.title} - Question {self.question_number}: {self.question_text}"
    
class QuestionStep(models.Model):
    class Meta:
        verbose_name_plural = 'QuestionStep'
    quiz_instance = models.ForeignKey(QuizInstance, on_delete=models.CASCADE)
    question  = models.ForeignKey(Question, on_delete=models.CASCADE)
    step = models.BooleanField('Step', default=False)

class Participant(models.Model):
    class Meta:
        verbose_name_plural = 'Participant'
    quiz = models.ForeignKey(QuizInstance, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    points = models.IntegerField('Points', default=0)
    archived = models.BooleanField('Archived status', default=False)
    
    def __str__(self):
        return self.user.username

class Answers(models.Model):
    class Meta:
        verbose_name_plural = 'Answers'
    participant = models.ForeignKey(Participant, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer_type = models.IntegerField('Answer type', default="0")
    question_step = models.IntegerField('Question_step', default="1")
    given_answer = models.CharField('Given answer', default="", blank=True, null=True, max_length=200)
    points_awarded = models.IntegerField('Points awarded', default="0")
    verification = models.BooleanField('Verification needed', default=True)

class QuizTeam(models.Model):
    class Meta:
        verbose_name_plural = 'QuizTeam'
    participant = models.ForeignKey(Participant, on_delete=models.CASCADE)
    team_name = models.CharField('Team Name', blank=True, null=True, max_length=50)

class QuizMember(models.Model):
    class Meta:
        verbose_name_plural = 'QuizMember'
    quiz_team = models.ForeignKey(QuizTeam, on_delete=models.CASCADE)
    member_name = models.CharField('Member Name (string)', blank=True, null=True, max_length=50)
    member_data = models.ForeignKey(TeamMembers, on_delete=models.SET_NULL, null=True, blank=True)
