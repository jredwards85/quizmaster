from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, get_user_model, update_session_auth_hash
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.db import IntegrityError, transaction
from django.db.models import Q, Count, Avg
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from datetime import timedelta
from .models import User,TeamMembers, TeamNames, Quiz, QuizReviews, QuizInstance, Question, QuestionStep, Participant, Answers, Themes, QuizTeam, QuizMember
import json, re

def redirect_to_index(request):
    if request.user.is_authenticated:
        return redirect('logged_in_index')
    else:
        return redirect('logged_out_index')


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def logged_out_index(request):

    if request.method == "POST":

        if "login" in request.POST:

            username = request.POST["username"]
            password = request.POST["password"]

            if ' ' in username:
                messages.error(request, "Spaced are not allowed in the username.")
                return HttpResponseRedirect(reverse("logged_out_index"))
            
            if 0 < len(username) <= 50 and 0 < len(password) <= 50:
                
                user = authenticate(request, username=username, password=password)
                
                if user is not None:
                    login(request, user)
                    return HttpResponseRedirect(reverse("logged_in_index"))
                else:
                    messages.error(request, "Invalid username and/or password.")
                    return HttpResponseRedirect(reverse("logged_out_index"))

            else:
                messages.error(request, "The username or password provided was too long (max. 50 characters).")
                return HttpResponseRedirect(reverse("logged_out_index"))
            
        if "register" in request.POST:

            username = request.POST["username"]
            password = request.POST["password"]
            password_confirm = request.POST["password_confirm"]

            if 0 < len(username) <= 50 and 0 < len(password) <= 50 and 0 < len(password_confirm) <= 50:
                
                if password == password_confirm:
                    try:
                        user_model = get_user_model()
                        user = user_model.objects.create_user(username=username, password=password)
                        user = authenticate(request, username=username, password=password)

                        if user is not None:
                            login(request, user)

                    except IntegrityError:
                        messages.error(request, "The username provided is already in user.")
                        return HttpResponseRedirect(reverse("logged_out_index"))

                    return HttpResponseRedirect(reverse("logged_in_index"))

                else:
                    messages.error(request, "Your password and confirmation password did not match.")
                    return HttpResponseRedirect(reverse("logged_out_index"))

            else:
                messages.error(request, "One of the fields provided was too long (max. 50 characters).")
                return HttpResponseRedirect(reverse("logged_out_index"))

    else:
            
            return render(request, "logged_out_index.html")

@login_required
def setup(request):
    if request.method == "POST":

        if "first_name" in request.POST:
            
            name = request.POST["name"]
            
            try:
                if 0 < len(name) <= 50: 

                    TeamMembers.objects.create(user = request.user, name = name)
                    request.user.profile = int(1)
                    request.user.save()
                    return redirect('setup')
                
                else: 
                    messages.error(request, "The name provided was either too short or too long (max. 50 characters).")
                    return redirect('setup')
            
            except Exception as e:
                messages.error(request, "An error occurred whilst saving the name. Error {}".format(e))
                return redirect('setup')
            
        elif "member_name" in request.POST:
            
            name = request.POST["name1"]
            
            try:
                if 0 < len(name) <= 50: 
                    TeamMembers.objects.create(user = request.user, name = name)
                    return redirect('setup')
                
                else: 
                    messages.error(request, "The name provided was either too short or too long (max. 50 characters).")
                    return redirect('setup')
            
            except Exception as e:
                messages.error(request, "An error occurred whilst saving the name. Error {}".format(e))
                return redirect('setup')

        elif "teamname" in request.POST:

            teamname = request.POST["name"]
            
            try:
                if 0 < len(teamname) <= 50: 
                    
                    team_name_obj, created = TeamNames.objects.get_or_create(user=request.user, defaults={'name': teamname})

                    if not created:
                        team_name_obj.name = teamname
                        team_name_obj.save()

                    request.user.profile = 3 
                    request.user.save()

                    return redirect('setup')
                
                else: 
                    messages.error(request, "The teamname provided was either too short or too long (max. 50 characters).")
                    return redirect('setup')
            
            except Exception as e:
                messages.error(request, "An error occurred whilst saving the teamname. Error {}".format(e))
                return redirect('setup')
        
        elif "upload_avatar" in request.POST:
            
            id = request.POST['id']
            uploaded_image = request.FILES.get('image')

            if uploaded_image:

                image_data = TeamMembers.objects.filter(id = id).first()
                
                if image_data.avatar:
                    default_storage.delete(image_data.avatar.path)

                image_data.avatar.save(uploaded_image.name, ContentFile(uploaded_image.read()))
                return redirect("setup")
            
            else:
                messages.error(request, "No image was provided.")
                return HttpResponseRedirect(reverse("setup"))
            
        elif "delete_avatar" in request.POST:
                
                id = request.POST['id']
                image_data = TeamMembers.objects.filter(id = id).first()
                
                if image_data.avatar:
                    try:
                        default_storage.delete(image_data.avatar.path)
                        image_data.avatar = None
                        image_data.save()

                        messages.success(request, "The avatar was successfully deleted.")
                        return HttpResponseRedirect(reverse("setup"))

                    except Exception as e:
                        messages.error(request, "An unexpected error occurred: {}".format(e))
                        return HttpResponseRedirect(reverse("setup"))

                else:
                    messages.error(request, "No avatar available to delete.")
                    return HttpResponseRedirect(reverse("setup"))
    

        elif "next" in request.POST:
            
            step = request.POST["step"]
           
            try:
                request.user.profile = int(step)
                request.user.save()
                return redirect('setup')

            except Exception as e:
                messages.error(request, "An error occurred whilst moving to the next step. Error {}".format(e))
                return redirect('setup')
        
        else:
            messages.error(request, "Invalid request.")
            return redirect('setup')

    else:

        if request.user.profile == 4:
            return redirect('index')
        
        else:
            team_members = TeamMembers.objects.filter(user=request.user)
            
            return render(request, "setup.html", {
            "teammembers": team_members,
            })
        
            
                  
@login_required
def logged_in_index(request):

    # Read the active cover data
    #TODO: How are themes to be handled?
    cover_data = Themes.objects.filter(status=True).first()

    return render(request, "logged_in_index.html", {
        "cover_data": cover_data,
        })

@login_required
def profile(request):
        
    if request.method == "POST":

        if "create" in request.POST:

            teamname = request.POST["teamname"]

            if len(teamname) <= 50:
                
                if TeamNames.objects.filter(user = request.user).exists():
                        TeamNames.objects.filter(user = request.user).update(name=teamname)
                        messages.success(request, "The team name was successfully saved.")
                        return HttpResponseRedirect(reverse("profile"))
                else:
                    TeamNames.objects.create(name = teamname, user = request.user)
                    messages.success(request, "The team name was successfully saved.")
                    return HttpResponseRedirect(reverse("profile"))
            else:
                messages.error(request, "The team name provided was too long (max. 50 characters).")
                return HttpResponseRedirect(reverse("profile"))
            
        elif "add_member" in request.POST:

            member = request.POST["member"]

            if 0 < len(member) <= 50:
                TeamMembers.objects.create(name = member, user = request.user)
                messages.success(request, "The team member '{}' was successfully added.".format(member))
                return HttpResponseRedirect(reverse("profile"))
            else:
                messages.error(request, "The member name provided was too long (max. 50 characters).")
                return HttpResponseRedirect(reverse("profile"))
            
        elif "change_name" in request.POST:

            name = request.POST["name"]
            id = request.POST["id"]

            if len(name) <=50:

                try:
                    edit_member = TeamMembers.objects.get(id = id)
                    edit_member.name = name
                    edit_member.save()

                    messages.success(request, "Name changed successfully")
                    return redirect("profile")
                
                except Exception as e:

                    messages.error(request, "An unexpected error occurred: {}".format(e))
                    return redirect("profile")
            
            else:
                messages.error(request, "The name was too long (max. 50 characters).")
                return redirect("profile")

            
        elif "public" in request.POST:

            name = request.POST["publicname"]

            if len(name) <=50:
                    
                try: 
                    user = request.user
                    user.public_host_name = name
                    user.save()

                except Exception as e:

                    messages.error(request, "An unexpected error occurred: {}".format(e))
                    return redirect("profile")
            
            else:
                messages.error(request, "The name was too long (max. 50 characters).")
                return redirect("profile")
            

        elif "delete_member" in request.POST:

            id = request.POST["id"]

            try:
                delete_member = TeamMembers.objects.get(id=id, user = request.user)
                delete_member.delete()

                messages.success(request, "The team member was successfully deleted.")
                return HttpResponseRedirect(reverse("profile"))
            
            except Exception as e:

                messages.error(request, "An unexpected error occurred: {}".format(e))
                return redirect("profile")
        
        elif "upload_avatar" in request.POST:
            
            id = request.POST['id']
            uploaded_image = request.FILES.get('image')

            if uploaded_image:

                image_data = TeamMembers.objects.filter(id = id).first()
                if image_data.avatar:
                    default_storage.delete(image_data.avatar.path)

                image_data.avatar.save(uploaded_image.name, ContentFile(uploaded_image.read()))
                return redirect("profile")
            
            else:
                messages.error(request, "No image was provided.")
                return HttpResponseRedirect(reverse("profile"))
            
        elif "delete_avatar" in request.POST:
                
                id = request.POST['id']
                image_data = TeamMembers.objects.filter(id = id).first()
                
                if image_data.avatar:
                    try:
                        default_storage.delete(image_data.avatar.path)
                        image_data.avatar = None
                        image_data.save()

                        messages.success(request, "The avatar was successfully deleted.")
                        return HttpResponseRedirect(reverse("profile"))

                    except Exception as e:
                        messages.error(request, "An unexpected error occurred: {}".format(e))
                        return HttpResponseRedirect(reverse("profile"))

                else:
                    messages.error(request, "No avatar available to delete.")
                    return HttpResponseRedirect(reverse("profile"))
        
        else:
                messages.error(request, "An invalid request was made.")
                return HttpResponseRedirect(reverse("profile"))

    team_name = TeamNames.objects.filter(user = request.user).first()
    team_members = TeamMembers.objects.filter(user = request.user)

    return render(request, "profile.html", {
        "teamname": team_name,
        "teammembers": team_members,
    })

@login_required
def account(request):

    if request.method == "POST":

        if "update_username" in request.POST:

            username = request.POST["username"]

            if ' ' in username:
                messages.error(request, "Spaces are not allowed in the username.")
                return redirect("account")

            if 0 < len(username) <= 50:
                
                try:
                    request.user.username = username
                    request.user.save()
                    messages.success(request, "The username was successfully updated.")
                    return redirect("account") 
                
                except IntegrityError:
                    messages.error(request, "The username '{}' is already taken.".format(username))
                    return redirect("account") 

            else:
                messages.error(request, "The username provided was too long or too short (min. 1 - max. 50 characters).")
                return redirect("account")
        
        elif "change_password" in request.POST:

            current_password = request.POST["current_password"]
            new_password = request.POST["new_password"]
            new_password_confirm = request.POST["new_password_confirm"]

            if 0 < len(new_password) <= 50:
                
                if new_password == new_password_confirm:
                    
                    if request.user.check_password(current_password):
                        # Set the new password
                        request.user.set_password(new_password)
                        request.user.save()

                        # Update the session to prevent the user from being logged out
                        update_session_auth_hash(request, request.user)
                        messages.success(request, "Password successfully changed.") 
                        return redirect("account")

                    else: 
                        messages.error(request, "Incorrect password.") 
                        return redirect("account")
                else:
                    messages.error(request, "The password and confirmation password did not match.") 
                    return redirect("account")
                
            else:
                messages.error(request, "The password provided was too long or too short (min. 1 - max. 50 characters).") 
                return redirect("account")

        elif "delete_account" in request.POST:

            password = request.POST['password']

            try:
                if request.user.check_password(password):
                    request.user.delete()
                    messages.success(request, "Account successfully deleted.") 
                    return redirect('index')
                
                else:
                    messages.error(request, "Incorrect password.") 
                    return redirect("account")
            
            except Exception as e:
                messages.error(request, "An unexpected error occurred: {}".format(e))
                return HttpResponseRedirect(reverse("profile"))

        else:
            messages.error(request, "Invalid request.")
            return redirect("account")
    else:
        return render(request, 'account.html')


@login_required
def join_quiz(request, quiz_id = None):
    if quiz_id == None:
        messages.error(request, "Unable to find the requested quiz.")
        return HttpResponseRedirect(reverse("index"))
    else:
        try:
            quiz_data = QuizInstance.objects.get(id=quiz_id)

            if QuizInstance.objects.filter(id=quiz_id, participant__user=request.user).exists():
                url = reverse('quiz_redirection', args=[quiz_id])
                return HttpResponseRedirect(url)
            
            else:              
                if quiz_data.password =="":

                    if quiz_data.quiz_step == 0:
                        Participant.objects.create(quiz=quiz_data, user=request.user)
                        url = reverse('quiz_redirection', args=[quiz_id])
                        return HttpResponseRedirect(url)
                    
                    else: 
                        messages.error(request, "Sorry, this quiz has already started. It is no longer possible to join.")
                        return HttpResponseRedirect(reverse("index"))
                
                else:
                    if quiz_data.quiz_step == 0:

                        url = reverse('quiz_registration', args=[quiz_id])
                        return HttpResponseRedirect(url)
                    
                    else:
                        messages.error(request, "Sorry, this quiz has already started. It is no longer possible to join.")
                        return HttpResponseRedirect(reverse("index"))
                    
        except QuizInstance.DoesNotExist:
            messages.error(request, "Unable to find the requested quiz.")
            return HttpResponseRedirect(reverse("index"))

@login_required
def quiz_registration(request, quiz_id = None):

    if request.method == "POST":

        if "register" in request.POST:

            quiz_id = request.POST["quiz_id"]
            password = request.POST["password"]
            
            try:
                quiz_data = QuizInstance.objects.get(id=quiz_id)

                if quiz_data.quiz_step != 0:
                    messages.error(request, "Quiz has already started. Registration is no longer possible.")
                    return redirect("browse")
                
                if quiz_data.password != password:
                    messages.error(request, "Incorrect password.")
                    url = reverse('quiz_registration', args=[quiz_id])
                    return HttpResponseRedirect(url)

                else:
                    Participant.objects.create(quiz=quiz_data, user=request.user)

                    messages.success(request, "Registration successful.")
                    url = reverse('quiz_redirection', args=[quiz_id])
                    return HttpResponseRedirect(url)


            except QuizInstance.DoesNotExist:
                messages.error(request, "Sorry, unable to find the requested quiz.")
                return redirect("browse")

        else:
            messages.error(request, "Invalid Request")
            return redirect("index")

    if quiz_id == None:
        return redirect("index")
    
    else:
        try:
            quiz_data = QuizInstance.objects.get(id=quiz_id, quiz_step=0)

            return render(request, "quiz_registration.html", {
                "quiz_data": quiz_data,
            })

        except QuizInstance.DoesNotExist:
            messages.error(request, "Either the requested quiz doesn't exist or has already started.")
            return HttpResponseRedirect(reverse("index"))


@login_required
def quiz_redirection(request, quiz_id = None):
    if quiz_id == None:
        messages.error(request, "Unable to find the requested quiz.")
        return HttpResponseRedirect(reverse("index"))
    else:
        try:
            quiz_data = QuizInstance.objects.get(id = quiz_id)

            # Quiz has not yet started
            if quiz_data.quiz_step == 0:
                url = reverse('waiting', args=[quiz_id])
                return HttpResponseRedirect(url)
            
            # Quiz has finished
            elif quiz_data.quiz_step == 2:
                url = reverse('results', args=[quiz_id])
                return HttpResponseRedirect(url)
            
            # Quiz is in process
            else:
                url = reverse('question', args=[quiz_id])
                return HttpResponseRedirect(url)
            
        except QuizInstance.DoesNotExist:
            messages.error(request, "Unable to find the requested quiz.")
            return HttpResponseRedirect(reverse("index"))


@login_required
def waiting(request, quiz_id = None):
    
    if request.method == "POST":
        
        if "start" in request.POST:

            quiz_id = request.POST["quiz_id"]

            try:
                # Find quiz data for registered participants
                quiz_data = QuizInstance.objects.get(id = quiz_id, play_type=2, participant__user=request.user)

                quiz_data.quiz_step = 1
                quiz_data.save()

                # Redirect to question page
                url = reverse('quiz_redirection', args=[quiz_id])
                return HttpResponseRedirect(url)


            except Exception as e:
                messages.error(request, "Invalid request.")
                return redirect("my_quizzes")
            
        else:
            messages.error(request, "Invalid request.")
            return redirect("my_quizzes")

    else:
    
        if quiz_id == None: 
            messages.error(request, "Waiting room only available for valid quizzes.")
            return redirect("my_quizzes")
        
        else: 

            try:
                # Find quiz data for registered participants
                quiz_data = QuizInstance.objects.get(id = quiz_id, quiz_step=0, participant__user=request.user)
                
                return render(request, "waiting_page.html", {
                    "quiz_data": quiz_data,
                })
            
            except QuizInstance.DoesNotExist:
                messages.error(request, "Waiting room only available for valid quizzes or registered participants.")
                return redirect("my_quizzes")


@csrf_exempt
def forward_waiting(request):
    data = json.loads(request.body.decode("utf-8"))
    quiz_id = data.get("quiz_id")
    #TODO: Do we need to check quiz exists and if the user is registered?
    quiz_data = QuizInstance.objects.get(id = quiz_id)
    if quiz_data.quiz_step == 0:
        #TODO: Quiz is still waiting, so no action yet
        response_data = {
            'status': 0,
        }
    elif quiz_data.quiz_step == 1:
        #TODO: Forward to question page of relevant question
        response_data = {
            'status': 1,
            'quiz_id': quiz_id,
        }
    else:
        #TODO: Forward to results page
        response_data = {
            'status': 2,
            'quiz_id': quiz_id,
        }
    return JsonResponse(response_data)


@login_required
def question(request, quiz_id = None):
    
    if request.method == "POST":
        
        if "submit_question_multi" in request.POST:

            # Read data from post
            quiz_id = request.POST["quiz_id"]
            question_id = request.POST["question_id"]
            answer_value = request.POST.get('answer')

            try:
                # Read Quiz & Participant data
                quiz_data = QuizInstance.objects.get(id=quiz_id)
                participant_data = Participant.objects.get(quiz=quiz_data, user=request.user)
                
                #Read Question data, step data and answer data
                question_data = Question.objects.get(id=question_id, question_number=quiz_data.question_number)
                question_step = QuestionStep.objects.get(quiz_instance=quiz_data, question=question_data, step=False)
                answer_data = Answers.objects.get(participant=participant_data, question=question_data)

                # Answer handling
                if answer_value != None:
                    answer =int(answer_value)

                    if answer == question_data.correct_answer:
                        answer_state = True
                        answer_submitted = True
                        answer_data.answer_type = 2
                        answer_data.points_awarded = 1
                    else:
                        answer_state = False
                        answer_submitted = True
                        answer_data.answer_type = 2
                        answer_data.points_awarded = 0
                else:
                    answer_state = False
                    answer_submitted = False
                    answer_data.answer_type = 0
                    answer_data.points_awarded = 0
                
                answer_data.question_step = 4
                answer_data.verification = False
                
                if answer_submitted:
                    if answer == 1:
                        answer_data.given_answer = question_data.answer1
                    elif answer == 2:
                        answer_data.given_answer = question_data.answer2
                    elif answer == 3:
                        answer_data.given_answer = question_data.answer3
                    else:
                        answer_data.given_answer = question_data.answer4
                else:
                    answer_data.given_answer = ""

                if answer_state == True:
                    participant_data.points += 1
                    participant_data.save()

                answer_data.save()

                # Set question step
                question_step.step = True
                question_step.save()

                # Determine next question
                current_logical_order = question_data.question_number
                next_question = Question.objects.filter(quiz=quiz_data.quiz, question_number__gt=current_logical_order).order_by('question_number').first()
                
                # Verify if next question exists
                if next_question is not None:
                    quiz_data.question_number = next_question.question_number
                    quiz_data.save()

                    # Create next question step
                    QuestionStep.objects.create(quiz_instance=quiz_data, question=next_question)

                else:
                    quiz_data.quiz_step = 2
                    quiz_data.completed_on = timezone.now()
                    quiz_data.save()

                url = reverse('quiz_redirection', args=[quiz_id])
                return HttpResponseRedirect(url)

            except Exception as e:
                messages.error(request, "Unexpected error. Error: {}".format(e))
                return redirect("my_quizzes")

        else:
            messages.error(request, "Invalid request.")
            return redirect("my_quizzes")


    elif quiz_id == None: 
        messages.error(request, "Unable to find the requested quiz.")
        return HttpResponseRedirect(reverse("index"))
    
    else: 
        # Read quiz and question data
        try:
            quiz_data = QuizInstance.objects.get(id = quiz_id)

            # Quiz has not started or is finished
            if quiz_data.quiz_step == 0 or quiz_data.quiz_step == 2:
                url = reverse('quiz_redirection', args=[quiz_id])
                return HttpResponseRedirect(url)
            
            # Quiz in play
            else: 
                question_data = Question.objects.get(quiz = quiz_data.quiz, question_number = quiz_data.question_number)
                participant_data = Participant.objects.get(quiz = quiz_data, user = request.user)

                # Load or create answer data for given participant
                try:
                    answer = Answers.objects.get(participant = participant_data, question = question_data)

                except Answers.DoesNotExist:
                    Answers.objects.create(participant = participant_data, question = question_data)
                    # I create above, and read below, because the rendering doesn't work otherwise (a bug?)
                    answer = Answers.objects.get(participant = participant_data, question = question_data)

                return render(request, "questions.html", {
                    "quiz_data": quiz_data,
                    "answer_data": answer,
                    "question_data": question_data,
                })

        except QuizInstance.DoesNotExist:
            messages.error(request, "Unable to find the requested quiz.")
            return HttpResponseRedirect(reverse("index"))
        except Question.DoesNotExist:
            messages.error(request, "Unable to find the requested question.")
            return HttpResponseRedirect(reverse("index"))
        except Participant.DoesNotExist:
            messages.error(request, "Unable to find the requested participant.")
            return HttpResponseRedirect(reverse("index"))

@csrf_exempt
def next_step_one(request):
    # Set question state to 1
    data = json.loads(request.body.decode("utf-8"))
    answer_id = int(data.get("answer_id"))
    try:
        answer = Answers.objects.get(id =  answer_id)
        answer.question_step = 2
        answer.save()
        response_data = {"success": True, "message": "PUT request successful"}

    except Answers.DoesNotExist:
        response_data = {"success": False, "message": "Unable to find requested answer."}

    return JsonResponse(response_data)

@csrf_exempt
def submit_open_answer(request):
    data = json.loads(request.body.decode("utf-8"))
    
    answer_id = data['data']['answer_id']
    given_answer = data['data']['given_answer']

    try:
        answer = Answers.objects.get(id = answer_id)
        question = answer.question
        
        # Identify correct answer text
        correct_answer_number = question.correct_answer
        answer_mapping = {
            1: question.answer1,
            2: question.answer2,
            3: question.answer3,
            4: question.answer4,
        }
        correct_answer = answer_mapping.get(correct_answer_number)

        # Check user manipulation cannot submit another answer
        if answer.question_step != 4:

            # Check user input and update database
            if given_answer.lower() == correct_answer.lower():
                answer.answer_type = 1
                answer.given_answer = given_answer
                answer.points_awarded = 3
                answer.question_step = 4
                answer.verification = False
                answer.save()
            else:
                answer.answer_type = 1
                answer.given_answer = given_answer
                answer.question_step = 4
                answer.verification = True
                answer.save()

            response_data = {"success": True, "message": "PUT request successful"}

        else: 
            response_data = {"success": False, "message": "PUT request declined. Answer already provided."}

    except Exception as e:
        response_data = {"success": False, "message": f"PUT request not successful: {e}"}

    return JsonResponse(response_data)

@csrf_exempt
def see_multichoice_answers(request):
    data = json.loads(request.body.decode("utf-8"))
    answer_id = int(data.get("answer_id"))

    try:
        answer = Answers.objects.get(id = answer_id)

        # Check user manipulation cannot submit another answer
        if answer.question_step != 4:

            answer.answer_type = 2
            answer.question_step = 2
            answer.save()

            response_data = {"success": True, "message": "PUT request successful"}

        else:
            response_data = {"success": False, "message": "PUT request declined. Answer already provided."}
    
    except Exception as e:
        response_data = {"success": False, "message": f"PUT request not successful: {e}"}

    return JsonResponse(response_data)

@csrf_exempt
def submit_multi_answer(request):

    # Read JSON data
    response_data = {"success": False, "message": "", "redirect": False, "quiz_id": 0,}
    data = json.loads(request.body.decode("utf-8"))
    
    # Read data from JSON PUT request
    quiz_id = data['data']['quiz_id']
    question_id = data['data']['question_id']
    answer_value = data['data']['given_answer']

    try:
        # Read Quiz & Participant data
        quiz_data = QuizInstance.objects.get(id=quiz_id)
        participant_data = Participant.objects.get(quiz=quiz_data, user=request.user)

        response_data["quiz_id"] = quiz_data.id
        
        #Read Question data, step data and answer data
        question_data = Question.objects.get(id=question_id, question_number=quiz_data.question_number)
        question_step = QuestionStep.objects.get(quiz_instance=quiz_data, question=question_data, step=False)
        answer_data = Answers.objects.get(participant=participant_data, question=question_data)

        # Check user manipulation cannot submit another answer
        if answer_data.question_step != 4:

            # Answer handling
            if answer_value != "None":
                answer =int(answer_value)

                if answer == question_data.correct_answer:
                    answer_state = True
                    answer_submitted = True
                    answer_data.answer_type = 2
                    answer_data.points_awarded = 1
                else:
                    answer_state = False
                    answer_submitted = True
                    answer_data.answer_type = 2
                    answer_data.points_awarded = 0
            else:
                answer_state = False
                answer_submitted = False
                answer_data.answer_type = 0
                answer_data.points_awarded = 0
            
            answer_data.question_step = 4
            answer_data.verification = False
            
            if answer_submitted:
                if answer == 1:
                    answer_data.given_answer = question_data.answer1
                elif answer == 2:
                    answer_data.given_answer = question_data.answer2
                elif answer == 3:
                    answer_data.given_answer = question_data.answer3
                else:
                    answer_data.given_answer = question_data.answer4
            else:
                answer_data.given_answer = ""

            if answer_state == True:
                participant_data.points += 1
                participant_data.save()

            answer_data.save()

        # Next step handling on quiz play type

        if quiz_data.play_type == 0:

            # Stored answer data above. Next steps are driven by host
            response_data["success"] = True
            response_data["message"] = "PUT request successful"
            return JsonResponse(response_data)
        
        elif quiz_data.play_type == 1:

            # Stored answer data above. Next steps are driven by team completion.
            all_participants = Participant.objects.filter(quiz=quiz_data)

            # Verifies all participants have answered
            all_participants_answered = Answers.objects.filter(
                    participant__in=all_participants, question=question_data, question_step=4
                ).count() == all_participants.count()

            if all_participants_answered:

                # Set question step
                question_step.step = True
                question_step.save()

                # Determine next question
                current_logical_order = question_data.question_number
                next_question = Question.objects.filter(quiz=quiz_data.quiz, question_number__gt=current_logical_order).order_by('question_number').first()

                response_data["redirect"] = True
                
                # Verify if next question exists
                if next_question is not None:
                    quiz_data.question_number = next_question.question_number
                    quiz_data.save()

                    # Create next question step
                    QuestionStep.objects.create(quiz_instance=quiz_data, question=next_question)

                else:
                    quiz_data.quiz_step = 2
                    quiz_data.completed_on = timezone.now()
                    quiz_data.save()
                    
            response_data["success"] = True
            response_data["message"] = "PUT request successful"
            return JsonResponse(response_data)

    except Exception as e:
        print(e)
        response_data["message"] = f"Error: {str(e)}"
        return JsonResponse(response_data)

@login_required
def results(request, quiz_id = None, team_id = None):
    if quiz_id == None and team_id == None: 
        messages.error(request, "Unable to find the requested quiz.")
        return HttpResponseRedirect(reverse("index"))
    
    else: 
        try:
            quiz_data = QuizInstance.objects.get(id = quiz_id)

            if quiz_data.quiz_step == 2:

                if team_id == None:

                    if quiz_data.play_type == 2:

                        url = reverse('results_detailed', args=[quiz_data.id])

                        return redirect(url)

                    else:

                        quiz_data.participant_set.prefetch_related('quizteam_set', 'quizteam_set__quizmember_set')
                        
                        participant_points = {}

                        if quiz_data.local_mode:
                            participants = Participant.objects.filter(quiz = quiz_data).exclude(user=quiz_data.host)
                        else: 
                            participants = Participant.objects.filter(quiz = quiz_data)

                        # Calculate total points for each participant
                        for participant in participants:
                            answers = Answers.objects.filter(participant=participant)
                            total_points = sum(answer.points_awarded for answer in answers)
                            participant_points[participant.user.username] = (participant, total_points)

                        # Sort participants by total points in descending order
                        sorted_participants = sorted(participant_points.items(), key=lambda x: x[1][1], reverse=True)

                        # Calculate ranks
                        rank = 1
                        prev_points = None
                        for index, (username, (participant, points)) in enumerate(sorted_participants):
                            if points != prev_points:
                                rank = index + 1
                            participant_points[username] = (participant, points, rank)
                            prev_points = points

                        # Now, sorted_participant_points is a dictionary with ranks included
                        sorted_participant_points = dict(sorted(participant_points.items(), key=lambda x: x[1][1], reverse=True))

                        return render(request, "quiz_results_teams.html", {
                            "sorted_participant_points": sorted_participant_points,
                            "quiz_data": quiz_data,
                        })
                
                else:
                    
                    if quiz_data.host == request.user:

                        quiz_data.participant_set.prefetch_related('participant_set__quizteam_set')
                        print(quiz_data)
                        
                        team_data = User.objects.get(id=team_id)
                        participant = Participant.objects.get(user = team_data, quiz = quiz_data)
                        answers = Answers.objects.filter(participant = participant).order_by('question__question_number')

                        return render(request, "quiz_results_detailed.html", {
                            "team_data": participant,
                            "answers": answers,
                            "quiz_data": quiz_data,
                        })
                    
                    else:

                        return HttpResponseRedirect(reverse("index"))
                        
            else:
                messages.error(request, "The quiz {} is not yet complete. The results are not available.".format(quiz_data.quiz.title))
                return HttpResponseRedirect(reverse("index"))

        except Exception as e:
            messages.error(request, "Error: {}".format(e))
            return HttpResponseRedirect(reverse("index"))

        
@login_required
def results_detailed(request, quiz_id = None):
    if quiz_id == None: 
        messages.error(request, "Unable to find the requested results.")
        return HttpResponseRedirect(reverse("index"))
    else:
        try:
            quiz_data = QuizInstance.objects.get(id = quiz_id)

            if quiz_data.quiz_step == 2:

                if quiz_data.local_mode and quiz_data.host == request.user:
                    messages.error(request, "Unable to find the requested results.")
                    return HttpResponseRedirect(reverse("index"))
                
                else:

                    participant = Participant.objects.get(user = request.user, quiz = quiz_data)
                    answers = Answers.objects.filter(participant = participant).order_by('question__question_number')
                    
                    total_correct = 0
                    for answer in answers:
                        if answer.points_awarded > 0:
                            total_correct += 1
                    
                    question_count = len(answers)

                    return render(request, "quiz_results_detailed.html", {
                        "team_data": participant,
                        "answers": answers,
                        "quiz_data": quiz_data,
                        "total_correct": total_correct,
                        "question_count": question_count,
                    })

            else:
                messages.error(request, "The quiz {} is not yet complete. The results are not available.".format(quiz_data.quiz.title))
                return HttpResponseRedirect(reverse("index"))
            
        except QuizInstance.DoesNotExist:
            messages.error(request, "Unable to find the requested results.")
            return HttpResponseRedirect(reverse("index"))


@login_required
def create(request, name=None, number=None):

    if request.method == "POST":
        if "create_quiz" in request.POST:
            
            title = request.POST["title"]
            description = request.POST["description"]
            category1 = request.POST.get("cat1")
            category2 = request.POST.get("cat2")
            category3 = request.POST.get("cat3")
            category4 = request.POST.get("cat4")
            
            if "private" in request.POST:
                private = True
            else:
                private = False

            if 0 < len(title) <= 200:

                title_url_hyphen = title.replace(" ", "-").lower()
                title_url_clean = re.sub('[^a-zA-Z0-9_.-]', '', title_url_hyphen)
                
                new_quiz = Quiz.objects.create(author = request.user, title = title, title_url = title_url_clean, description = description, 
                                               category1=category1, category2=category2, category3=category3, category4=category4, private = private)

                new_quiz.title_url += f"-{new_quiz.id}"
                new_quiz.save()

                messages.success(request, "Quiz created successfully.")
                return redirect("quiz_management", quiz_id=new_quiz.id)
            
            else:
                messages.error(request, "The quiz title was too long.")
                return redirect('create')

        elif "edit_quiz" in request.POST:

            title = request.POST["title"]
            description = request.POST["description"]
            category1 = request.POST.get("cat1")
            category2 = request.POST.get("cat2")
            category3 = request.POST.get("cat3")
            category4 = request.POST.get("cat4")
            id = request.POST["id"]
            
            if "private" in request.POST:
                private = True
            else:
                private = False

            try:
                quiz_data = Quiz.objects.get(author = request.user, id = id)
                
                if 0 < len(title) <= 200:

                    title_url_hyphen = title.replace(" ", "-").lower()
                    title_url_clean = re.sub('[^a-zA-Z0-9_.-]', '', title_url_hyphen)

                    quiz_data.title = title
                    quiz_data.title_url = title_url_clean
                    quiz_data.title_url += f"-{quiz_data.id}"
                    quiz_data.description = description
                    quiz_data.category1 = category1
                    quiz_data.category2 = category2
                    quiz_data.category3 = category3
                    quiz_data.category4 = category4
                    quiz_data.private = private
                    quiz_data.save()

                    messages.success(request, "Quiz data successfully updated.")
                    return redirect("quiz_management", quiz_id=quiz_data.id)

                else:
                    messages.error(request, "The quiz title was too long.")
                    return redirect('create', name=quiz_data.title_url)
            
            except Quiz.DoesNotExist:
                messages.error(request, "Save unsuccessful. The requested quiz either doesn't exist or you do not have access rights.")
                return redirect('my_quizzes')


        elif "delete_quiz" in request.POST:
            
            id = request.POST["id"]

            try:
                quiz_data = Quiz.objects.get(author = request.user, id = id)
                quiz_data.delete()

                messages.success(request, "Quiz successfully deleted.")
                return redirect('my_quizzes')
            
            except Quiz.DoesNotExist:
                messages.error(request, "Deletion unsuccessful. The requested quiz either doesn't exist or you do not have access rights.")
                return redirect('my_quizzes')

        elif any(field in request.POST for field in ["submit_question", "submit_question_2"]):
            
            try:
                #Quiz verification
                quiz_id = int(request.POST["id"])
                quiz_instance = Quiz.objects.get(author=request.user, id=quiz_id)

                # Main content
                question_text = request.POST["question"]

                question_type = int(request.POST["question_type"])
                answer1 = request.POST["answer1"]
                answer2 = request.POST["answer2"]
                answer3 = request.POST["answer3"]
                answer4 = request.POST["answer4"]
                correct_answer = int(request.POST["answer"])
                question_number = int(request.POST["number"])
                
                # Check status of the question id field
                if request.POST["question_id"] != "":
                    question_id = int(request.POST["question_id"])
                else:
                    question_id = -1

                if (
                    not (0 < len(question_text) <= 200) or
                    not (0 < len(answer1) <= 200) or
                    not (0 < len(answer2) <= 200) or
                    not (0 < len(answer3) <= 200) or
                    not (0 < len(answer4) <= 200) or
                    question_type not in {1, 2, 3} or
                    correct_answer not in {1, 2, 3, 4}
                    ):

                    messages.error(request, "A field was provided with invalid data. Request cancelled.")
                    url = reverse('create', kwargs={'name': quiz_instance.title_url, 'number': question_number})
                    return redirect(url)
                
                if question_number > 200:
                    
                    messages.error(request, "There is a maximum of 200 questions per quiz.")
                    url = reverse('create', kwargs={'name': quiz_instance.title_url, 'number': 0})
                    return redirect(url)

                # Media amd handling
                existing_image_str = request.POST["image-previous"]
                existing_image = True if existing_image_str == "True" else False
                existing_audio_str = request.POST["audio-previous"]
                existing_audio = True if existing_audio_str == "True" else False
                image = request.FILES.get("image")
                audio = request.FILES.get("audio")

                if Question.objects.filter(quiz=quiz_instance, question_number=question_number).exists():

                    # Checks if the question ID matches the found query
                    update_check = Question.objects.get(quiz=quiz_instance, question_number=question_number)
                    
                    if question_id == update_check.id:

                        # Load query data - question update
                        question_data = Question.objects.get(quiz=quiz_instance, question_number=question_number)

                    else: 
                        # Create new query - question number was duplicate
                        questions = Question.objects.filter(quiz=quiz_instance).order_by('question_number')

                        first_free_number = 1

                        for question in questions:
                            current_number = question.question_number

                            # Check if the current number is the expected one
                            if current_number == first_free_number:
                                first_free_number += 1
                            else:
                                break
                        
                        # Create new question with alternative question number
                        
                        messages.error(request, "Warning: There was a conflicting question number. \
                                       The questions was saved with question number {}.".format(first_free_number))
                        question_data = Question.objects.create(quiz=quiz_instance, question_number=first_free_number)
                                
                else:
                    # Creates new question if no results found
                    question_data = Question.objects.create(quiz=quiz_instance, question_number=question_number)
                
                question_valid = True

                # Question creation
                question_data.question_text = question_text
                question_data.question_type = question_type
                question_data.answer1 = answer1
                question_data.answer2 = answer2
                question_data.answer3 = answer3
                question_data.answer4 = answer4
                question_data.correct_answer = correct_answer
                
                if question_type == 1:
                    
                    if question_data.image:
                        default_storage.delete(question_data.image.path)
                        question_data.image = None

                    if question_data.audio: 
                        default_storage.delete(question_data.audio.path)
                        question_data.audio = None

                elif question_type == 2:
                    
                    # Delete existing audio file
                    if question_data.audio:                         
                        default_storage.delete(question_data.audio.path)
                        question_data.audio = None

                    # Previous image exists, and will be replaced
                    if question_data.image and existing_image and image:
                        
                        # Delete old image                        
                        default_storage.delete(question_data.image.path)

                        # Save new image
                        question_data.image.save(image.name, image)

                    # No previous image, and new image will be saved
                    elif not existing_image and image:
                        
                        # Save new image
                        question_data.image.save(image.name, image)

                    # Previous image exists, but doesn't need to be replaced.
                    elif question_data.image and existing_image and not image:
                        pass

                    else:
                        question_valid = False
                        messages.success(request, "Question saved successfully. No image file provided.")
                        messages.error(request, "An image question type was selected, but no image file was provided.")
                        

                elif question_type == 3:

                    # Delete existing image file
                    if question_data.image:                        
                        default_storage.delete(question_data.image.path)
                        question_data.image = None
                    
                    # Previous audio exists, and will be replaced
                    if question_data.audio and existing_audio and audio:
                        
                        # Delete old audio                        
                        default_storage.delete(question_data.audio.path)

                        # Save new audio
                        question_data.audio.save(audio.name, audio)
                        
                    # No previous audio, and new audio will be saved
                    elif not question_data.audio and not existing_audio and audio:

                        # Save new audio
                        question_data.audio.save(audio.name, audio)

                    # Previous audio exists, but doesn't need to be replaced.
                    elif question_data.audio and existing_audio and not audio:
                        pass

                    else:
                        question_valid = False
                        messages.success(request, "Question saved successfully. No audio file provided.")
                        messages.error(request, "An audio question type was selected, but no audio file was provided.")

                question_data.save()

                if question_valid:

                    messages.success(request, "Question was successfully saved.")

                    # Create another question
                    if "submit_question" in request.POST:    
                        return redirect("create", name=quiz_instance.title_url, number=0)
                    # Return to quiz management (save and exit)
                    else:
                        url = reverse('quiz_management', kwargs={'quiz_id': quiz_instance.id})
                        return redirect(url)
                
                else:
                    return redirect("create", name=quiz_instance.title_url, number=question_number)

            except Exception as e:
                messages.error(request, "An unexpected error occurred: {}".format(e))
                return redirect('create')

        elif "cancel" in request.POST:

            id = request.POST["quiz_id"]

            if id == "":
                
                return redirect(my_quizzes)
            
            else:

                url = reverse('quiz_management', kwargs={'quiz_id': id})
                return redirect(url)

        else:
            messages.error(request, "Invalid request.")
            return redirect('create')

    # URL: create/name/
    # HTML: create_quiz
    elif name is not None and number is None:
        
        page_view = 'edit'

        try:
            quiz_data = Quiz.objects.get(author = request.user, title_url = name)
            return render(request, "create_quiz.html", {
                "page_view": page_view,
                "quiz_data": quiz_data,
            })

        
        except Quiz.DoesNotExist:
            messages.error(request, "The requested quiz either doesn't exist or you do not have access rights.")
            return redirect('index')

    # URL: create/name/number
    # HTML: create_question
    elif name is not None and number is not None:

        try:
            quiz_data = Quiz.objects.get(author = request.user, title_url = name)

            if quiz_data.complete:
                messages.error(request, "The requested quiz is marked as complete. Editing is no longer possible. Please 'mark for edit' to make changes.")
                return redirect("quiz_management", quiz_id=quiz_data.id)


            else:
            
                # Create new question
                if number == 0:

                    # Find a new question number
                    questions = Question.objects.filter(quiz = quiz_data).order_by('question_number')
                    new_question_number = 1
                    
                    for question in questions:
                        current_number = question.question_number
                        
                        # Check if the current number is the expected one
                        if current_number == new_question_number:
                            new_question_number += 1
                        else:
                            break
                    
                    question_data = None

                    
                    return render(request, 'create_question.html', {
                        "quiz_data": quiz_data,
                        "question_number": new_question_number,
                        "question_data": question_data,
                        "page_view": True,
                    })
                
                # Edit existing question
                else:

                    try:
                        question_data = Question.objects.get(quiz = quiz_data, question_number = number)
                        if question_data.audio:
                            url = question_data.audio.url
                            file_name = url.rsplit('/', 1)[-1]
                        else:
                            file_name = ""
                        

                        return render(request, 'create_question.html', {
                            "quiz_data": quiz_data,
                            "question_number": number,
                            "question_data": question_data,
                            "page_view": False,
                            "file_name": file_name,
                        })

                    except Question.DoesNotExist:
                        
                        messages.error(request, "Unable to find the requested question.")
                        return redirect("create", name=quiz_data.title_url, number=0)

        
        except Quiz.DoesNotExist:
            messages.error(request, "The requested quiz either doesn't exist or you do not have access rights.")
            return redirect('create')


    # URL: create/
    # HTML: create_quiz
    else:
        
        page_view = 'create'
        quiz_data = None

        return render(request, "create_quiz.html", {
            "page_view": page_view,
            "quiz_data": quiz_data,
        })


@login_required
def my_quizzes(request):

    if request.method == "POST":

        if "host" in request.POST:

            quiz_id = int(request.POST["quiz_id"])

            try:
                quiz_data = Quiz.objects.get(author=request.user, id=quiz_id)

                if quiz_data.private == True:
                
                    if quiz_data.author == request.user:                        
                        pass

                    else:
                        messages.error(request, "Access denied. This is a private quiz.")
                        return redirect('my_quizzes')


                if quiz_data.hidden == True or quiz_data.complete == False:
                    messages.error(request, "Access denied. This quiz is unavailable.")
                    return redirect('my_quizzes')


                # Read in initial question data
                question_data = Question.objects.filter(quiz=quiz_data).order_by('question_number').first()

                # Create quiz instance
                quiz_instance = QuizInstance.objects.create(host=request.user, quiz=quiz_data, question_number=question_data.question_number, play_type=0)

                # Create question step
                QuestionStep.objects.create(quiz_instance = quiz_instance, question = question_data)
            
                messages.success(request, "You have successfully created a hosting session.")
                return redirect('my_quizzes')
            
            except Exception as e:
                messages.error(request, "Unexpected error. Error: {}".format(e))
                return redirect('my_quizzes')

        elif "delete" in request.POST:

            quiz_id = int(request.POST["quiz_id"])

            try: 

                quiz_data = QuizInstance.objects.get(host=request.user, id=quiz_id)
                
                if quiz_data.quiz_step == 0 or quiz_data.quiz_step == 1:
                    quiz_data.delete()
                    messages.success(request, "This quiz session was successfully deleted.")
                
                else: 
                    messages.error(request, "This quiz has been completed. You may only archive this quiz session.")

                return redirect('my_quizzes')

            except Exception as e:
                messages.error(request, "Unexpected error. Error: {}".format(e))
                return redirect('my_quizzes')

            
        elif "archive" in request.POST:

            quiz_id = int(request.POST["quiz_id"])

            try: 

                quiz_data = QuizInstance.objects.get(host=request.user, id=quiz_id)
                
                if quiz_data.quiz_step == 2:
                    quiz_data.archived = True
                    quiz_data.save()

                    messages.success(request, "This quiz session was successfully archived.")
                
                else: 
                    messages.error(request, "This quiz instance is not yet complete. You may only archive once complete.")

                return redirect('my_quizzes')

            except Exception as e:
                messages.error(request, "Unexpected error. Error: {}".format(e))
                return redirect('my_quizzes')           
        
        elif "leave" in request.POST:

            quiz_id = int(request.POST["quiz_id"])

            try:
                quiz_data = QuizInstance.objects.get(id=quiz_id)
                
                if quiz_data.quiz_step == 0 or quiz_data.quiz_step == 1:

                    # Remove player from quiz if not yet started or in progress
                    participation = Participant.objects.get(quiz=quiz_data, user=request.user)
                    participation.delete()

                    # Delete the quiz instance if the host leaves
                    if quiz_data.play_type == 1 and quiz_data.host == request.user:
                        quiz_data.delete()

                    # Delete the quiz instance if the quiz is solo
                    elif quiz_data.play_type == 2: 
                        quiz_data.delete()

                    messages.success(request, "You successfully left the quiz.")

                else:
                    messages.error(request, "This quiz is complete. You can only archive this quiz.")
                
                return redirect('my_quizzes') 
            
            except Exception as e:
                messages.error(request, "Unexpected error. Error: {}".format(e))
                return redirect('my_quizzes') 
            

        elif "archive_participant" in request.POST:

            quiz_id = int(request.POST["quiz_id"])
            
            try:
                quiz_data = QuizInstance.objects.get(id=quiz_id)
                
                if quiz_data.quiz_step == 2:
                    
                    participation = Participant.objects.get(quiz=quiz_data, user=request.user)
                    participation.archived = True
                    participation.save()
                    messages.success(request, "This quiz session was successfully archived.")

                else:
                    messages.error(request, "This quiz is not yet complete. You cannot archive this quiz.")

                return redirect('my_quizzes') 

            except Exception as e:
                messages.error(request, "Unexpected error. Error: {}".format(e))
                return redirect('my_quizzes') 
            
        
        else:

            messages.error(request, "Invalid request.")
            return redirect('my_quizzes')
       
    else:
    
        # Queryset for quizzes created by this user
        created_quizzes = Quiz.objects.filter(author = request.user, hidden=False).annotate(
                                avg_rating=Avg('quizreviews__rating')).order_by('-created_on', 'title')

        # Queryset for quizzes hosted by this user
        hosted_quizzes = QuizInstance.objects.filter(host = request.user, archived=False).annotate(
                                avg_rating=Avg('quiz__quizreviews__rating')).order_by('-hosted_at')

        # Queryset for quizzes with user as player (solo) or participant (team play with 3rd party host)
        joined_quizzes = QuizInstance.objects.filter(participant__user=request.user, participant__archived=False
            ).annotate(avg_rating=Avg('quiz__quizreviews__rating')).order_by('-hosted_at')

        # Generate ID list for JavaScript in page
        joined_quiz_ids = "quiz_instances = ["
        for quiz in joined_quizzes:
            id_string = f"'{quiz.id}',"
            joined_quiz_ids += id_string
        joined_quiz_ids += "]"
        
        # Finds archived quizzes for hosts        
        archived_quizzes = QuizInstance.objects.filter(
            Q(host=request.user) & Q(archived=True) | 
            Q(participant__user=request.user) & Q(participant__archived=True)
            ).order_by('-completed_on').prefetch_related('participant_set__quizteam_set', 'participant_set__quizteam_set__quizmember_set')
        
        # Create a list to store the additional data
        additional_data_list = []

        # Iterate over the queryset and generate additional data
        for quiz_instance in archived_quizzes:
            participants_data = []

            for participant in quiz_instance.participant_set.all():
                team_data = []

                for quiz_team in participant.quizteam_set.all():
                    team_name = quiz_team.team_name

                    quiz_members_data = []

                    for quiz_member in quiz_team.quizmember_set.all():
                        member_name = quiz_member.member_name

                        # Append QuizMember data to the list
                        quiz_members_data.append(f"{member_name}")

                    # Only append team data if there are members
                    if quiz_members_data:
                        team_data.append(f"{team_name} ({', '.join(quiz_members_data)})")

                # Only append participant data if there are teams
                if team_data:
                    participants_data.append(', '.join(team_data))

            # Append the list of participants data to the additional_data_list
            additional_data_list.append({'quiz_instance': quiz_instance, 'participants': participants_data})

        # Update each QuizInstance in the original queryset with the additional data
        for idx, additional_data in enumerate(additional_data_list):
            archived_quizzes[idx].additional_data = additional_data

        
        return render(request, "my_quizzes.html", {
            "quizzes": created_quizzes,
            "hosted": hosted_quizzes,
            "archived": archived_quizzes,
            "joined": joined_quizzes,
            "joined_quizzes_ids": joined_quiz_ids,
        })
    
@csrf_exempt
def voting(request):

    data = json.loads(request.body.decode("utf-8"))
    
    try:
        # Read JSON data
        score = int(data['data']['score'])
        quiz_id = int(data['data']['quiz_instance'])

        # Read quiz instance with matching ID, complete status and user as participant or player
        quiz_instance = QuizInstance.objects.get(participant__user=request.user, id=quiz_id, quiz_step=2)

        # Read quiz data
        quiz_data = quiz_instance.quiz

        if 0 < (score) <= 5:
            try:
                vote = QuizReviews.objects.get(user=request.user, quiz=quiz_data)
                vote.rating = score
                vote.save()
            
            except QuizReviews.DoesNotExist:
                QuizReviews.objects.create(user=request.user, quiz=quiz_data, rating=score)

            total_votes = QuizReviews.objects.filter(quiz=quiz_data).count()
            new_average = QuizReviews.objects.filter(quiz=quiz_data).aggregate(avg_rating=Avg('rating'))['avg_rating']


            response_data = {"success": True, 
                             "message": "PUT request successful",
                             "quiz_id": quiz_id,
                             "quiz_id2": quiz_data.id,
                             "your_vote": score,
                             "total_votes": total_votes,
                             "new_average": new_average}

        else:
            response_data = {"success": False, "message": "PUT request failed"}

    except Exception as e:
        response_data = {"success": False, "message": "PUT request failed"}

    return JsonResponse(response_data)




@login_required
def quiz_management(request, quiz_id = None):

    if request.method == "POST":

        if "delete_question" in request.POST:
            
            quiz_id = request.POST["quiz_id"]
            question_id = request.POST["question_id"]

            try:
                quiz_data = Quiz.objects.get(author=request.user, id=quiz_id)
                question = Question.objects.get(quiz=quiz_data,id=question_id)
                question.delete()
                
                messages.success(request, "Question successfully deleted.")
                url = reverse('quiz_management', args=[quiz_id])
                return HttpResponseRedirect(url)

            except Exception as e:
                messages.error(request, "Unexpected error: {}".format(e))
                return redirect("my_quizzes")
            
        elif "delete_quiz"  in request.POST:
            
            quiz_id = request.POST["quiz_id"]

            try:
                quiz_data = Quiz.objects.get(author=request.user, id=quiz_id)

                if quiz_data.edit_only == True:
                    messages.success(request, "Unable to delete quiz. Please mark as hidden.")

                else:
                    quiz_data.delete()                
                    messages.success(request, "Quiz successfully deleted.")

                return redirect("my_quizzes")

            except Exception as e:
                messages.error(request, "Unexpected error: {}".format(e))
                return redirect("my_quizzes")

            
        elif "mark_complete" in request.POST:

            quiz_id = request.POST["quiz_id"]

            try:
                quiz_data = Quiz.objects.get(author=request.user, id=quiz_id)
                quiz_data.complete = True
                quiz_data.edit_only = True
                quiz_data.save()

                messages.success(request, "Quiz successfully marked as complete.")
                url = reverse('quiz_management', args=[quiz_id])
                return HttpResponseRedirect(url)

            except Exception as e:
                messages.error(request, "Unexpected error: {}".format(e))
                return redirect("index")

        elif "mark_edit" in request.POST:

            quiz_id = request.POST["quiz_id"]

            try:
                quiz_data = Quiz.objects.get(author=request.user, id=quiz_id)
                quiz_data.complete = False
                quiz_data.save()

                messages.success(request, "Quiz successfully marked for edit.")
                url = reverse('quiz_management', args=[quiz_id])
                return HttpResponseRedirect(url)

            except Exception as e:
                messages.error(request, "Unexpected error: {}".format(e))
                return redirect("index")

        elif "hide_quiz" in request.POST:

            quiz_id = request.POST["quiz_id"]
            
            try:
                quiz_data = Quiz.objects.get(author=request.user, id=quiz_id)
                quiz_data.hidden = True
                quiz_data.save()

                messages.success(request, "Quiz successfully marked for edit.")
                url = reverse('quiz_management', args=[quiz_id])
                return redirect('my_quizzes')

            except Exception as e:
                messages.error(request, "Unexpected error: {}".format(e))
                return redirect('my_quizzes')

        elif "duplicates" in request.POST:
            
            quiz_id = request.POST["quiz_id"]
            
            try:
                quiz_data = Quiz.objects.get(author=request.user, id=quiz_id)

                questions = Question.objects.filter(quiz=quiz_data).order_by('question_number')
                question_text_list = []
                deletion_list = []

                for question in questions:
                    
                    # Checks for duplicates with identical questions (may occur if incorrectly numbering)
                    trigger_warning = next((pair for pair in question_text_list if pair[1] == question.question_text), None)
                
                    if trigger_warning:
                        deletion_list.append(question.id)
                                        
                    value_pair = [question.question_number, question.question_text]
                    question_text_list.append(value_pair)
                
                questions_to_delete = Question.objects.filter(id__in=deletion_list)
                questions_to_delete.delete()

                messages.success(request, "All duplicates successfully deleted.")
                url = reverse('quiz_management', args=[quiz_id])
                return HttpResponseRedirect(url)                   
                    

            except Exception as e:
                messages.error(request, "Unexpected error: {}".format(e))
                return redirect("index")

        elif "reorder" in request.POST:
            
            quiz_id = request.POST["quiz_id"]

            try:
                quiz_data = Quiz.objects.get(author=request.user, id=quiz_id)

                questions = Question.objects.filter(quiz=quiz_data).order_by('question_number')

                starting_number = 1

                with transaction.atomic():

                    for question in questions:
                        question.question_number = starting_number
                        starting_number +=1
                        
                    Question.objects.bulk_update(questions, ['question_number'])
                
                messages.success(request, "All questions successfully reordered.")
                url = reverse('quiz_management', args=[quiz_id])
                return HttpResponseRedirect(url)
                
            except Exception as e:
                messages.error(request, "Unexpected error: {}".format(e))
                return redirect("index")

        else:
            messages.error(request, "Invalid request.")
            return redirect("my_quizzes")

    elif quiz_id == None:
        messages.error(request, "Unable to find the requested quiz.")
        return redirect("my_quizzes")
    
    else:

        try:
            quiz_data = Quiz.objects.get(author=request.user, id=quiz_id)
            questions = Question.objects.filter(quiz=quiz_data).order_by('question_number')

            errors = []
            error = False
            warnings = []
            warning = False
            question_text_list = []
            expected_next_question = 1

            duplicates = False
            order_issues = False
            
            if len(questions) < 1:
                errors.append("This quiz has no questions.")
            else:
                if questions[0].question_number != 1:
                    warnings.append(f"The first question is not number 1. Instead it is {questions[0].question_number}.")
                
            # Check for missing audio or images, and question duplicates
            for question in questions:
                
                # Checks for duplicates with identical questions (may occur if incorrectly numbering)
                trigger_warning = next((pair for pair in question_text_list if pair[1] == question.question_text), None)
                
                if trigger_warning:
                    warnings.append(f"Question {question.question_number} may be a duplicate of question {trigger_warning[0]}")
                    duplicates = True
                
                value_pair = [question.question_number, question.question_text]
                question_text_list.append(value_pair)

                # Check for gaps in question numbering
                current_question_number = question.question_number
                report = False
                while current_question_number > expected_next_question:
                    if not report:
                        errors.append(f"Question sequence issue. Incorrect sequence following question {expected_next_question - 1}.")
                        report = True
                        order_issues = True
                    
                    expected_next_question += 1
                
                expected_next_question += 1


                if question.question_type == 2:
                    if question.image:
                        pass
                    else:
                        errors.append(f"Question {question.question_number} is missing an image file.")
                elif question.question_type == 3:
                    if question.audio:
                        pass
                    else:
                        errors.append(f"Question {question.question_number} is missing an audio file.")
            
            if len(errors) > 0:
                error = True

            if len(warnings) > 0:
                warning = True

            return render(request, "quiz_management.html", {
                "quiz_data": quiz_data,
                "questions": questions,
                "errors": errors,
                "error_status": error,
                "warnings": warnings,
                "warning_status": warning,
                "duplicates": duplicates,
                "order_issues": order_issues,
            })
        
        except Quiz.DoesNotExist:

            messages.error(request, "Unable to find the requested quiz.")
            return redirect("my_quizzes")
        
@login_required
def browse(request, filter = None, category = None):

    if request.method == "POST":

        if "sort-by" in request.POST:
            
            sort_type = request.POST.get("sort-by")

            url = reverse('browse', args=[sort_type])
            return HttpResponseRedirect(url)

        elif "quiz-category" in request.POST:
        
            category_type = request.POST.get("quiz-category").lower()
            arg1 = "filter-by-category"

            url = reverse('browse', args=[arg1, category_type])
            return HttpResponseRedirect(url)

        elif "rating" in request.POST:

            rating = request.POST["rating"]
            arg1 = "filter-by-rating"

            url = reverse('browse', args=[arg1, rating])
            return HttpResponseRedirect(url)
        
        elif any(field in request.POST for field in ["player", "host"]):
            
            quiz_id = request.POST["quiz_id"]

            try:
                quiz_data = Quiz.objects.get(id=quiz_id, private=False, hidden=False)

                # Read in initial question data
                question_data = Question.objects.filter(quiz=quiz_data).order_by('question_number').first()

                # Create quiz instance
                if "player" in request.POST:
                    quiz_instance = QuizInstance.objects.create(quiz=quiz_data, question_number=question_data.question_number, play_type=2)
                    Participant.objects.create(user=request.user, quiz=quiz_instance)
                    QuestionStep.objects.create(quiz_instance = quiz_instance, question = question_data)
                    
                    url = reverse('join_quiz', args=[quiz_instance.id])
                    return HttpResponseRedirect(url)
                else: 
                    quiz_instance = QuizInstance.objects.create(host=request.user, quiz=quiz_data, question_number=question_data.question_number, play_type=1)
                    Participant.objects.create(user=request.user, quiz=quiz_instance)
                    QuestionStep.objects.create(quiz_instance = quiz_instance, question = question_data)

                    url = reverse('quiz_host', args=[quiz_instance.id])
                    return HttpResponseRedirect(url)
                # Create question step
                QuestionStep.objects.create(quiz_instance = quiz_instance, question = question_data)

                

            except Quiz.DoesNotExist:
                messages.error(request, "Oops, something went wrong. Could not find the requested quiz. ")
                return redirect("browse")

        elif "host" in request.POST["quiz_id"]:
            pass

        else:
            return redirect(browse)

    else:

        if filter and category == None:

            if filter == "most-popular":

                # Order by quiz with most instances
                all_quizzes = Quiz.objects.filter(complete=True, private=False, hidden=False).annotate(num_instances=Count('quizinstance')).order_by('-num_instances')
                filter_text = "Sort by: Most Popular"
                 
            elif filter == "average-review":

                all_quizzes = Quiz.objects.filter(complete=True, private=False, hidden=False).annotate(avg_rating=Avg('quizreviews__rating')).order_by('-avg_rating')
                filter_text = "Sort by: Average Reviews"

            elif filter == "created-on-descending":

                # Order by most recent quizzes 
                all_quizzes = Quiz.objects.filter(complete=True, private=False, hidden=False).order_by('-created_on') 
                filter_text = "Sort by: Created On (New To Old)"

            elif filter == "created-on-ascending":
                
                # Order by oldest quizzes
                all_quizzes = Quiz.objects.filter(complete=True, private=False, hidden=False).order_by('created_on')
                filter_text = "Sort by: Created On (Old to New)"

            else:
                pass
            
        elif filter and category:

            if filter == "filter-by-category":

                query_string = category.title().replace('-', ' ')
                

                # Query all 4 categories
                query = Q(category1__icontains=query_string) | Q(category2__icontains=query_string) | \
                    Q(category3__icontains=query_string) | Q(category4__icontains=query_string)

                # Modify the existing query to include the new conditions
                all_quizzes = Quiz.objects.filter(complete=True, private=False, hidden=False).filter(query)
                
                filter_text = f"Category: { query_string }"

            elif filter == "filter-by-rating":

                try:
                    rating_initial = int(category)

                    if 0 <= rating_initial <= 5:  

                        if rating_initial == 0:
                            all_quizzes = Quiz.objects.filter(complete=True, private=False, hidden=False, quizreviews__isnull=True)
                            filter_text = "Filter by rating: Unrated"
                        
                        else:

                            if rating_initial == 5:
                                rating = float(4.8)
                                filter_text = f"Rating: 4.8 and above "

                            else:
                                rating = float(category)
                                filter_text = f"Rating: {rating_initial} and above "

                            all_quizzes = Quiz.objects.filter(complete=True, private=False, hidden=False).annotate(
                                avg_rating=Avg('quizreviews__rating')).filter(avg_rating__gte=rating).order_by('-avg_rating')
                                
                    else:
                        return redirect("browse")

                except Exception as e:
                
                    return redirect("browse")
            
            else:
                pass
            
        else:
            
            all_quizzes = Quiz.objects.filter(complete=True, private=False, hidden=False).order_by('-created_on') 
            filter_text = ""
            
        quiz_count = (len(all_quizzes))

        quizzes_with_avg_rating = all_quizzes.annotate(avg_rating=Avg('quizreviews__rating'))

        return render(request, "browse.html", {
            "filter_text": filter_text,
            "quizzes": quizzes_with_avg_rating,
            "quiz_count": quiz_count,
        })

@csrf_exempt
def change_quiz_parameter(request):

    data = json.loads(request.body)

    try:

        quiz_id = int(data.get('quiz_id'))
        parameter = data.get('parameter') 
        
        if data.get('radio_value') == "True":
            value = True
        else:
            value = False
        
        quiz_data = QuizInstance.objects.get(id = quiz_id, host=request.user)

        if parameter == "mode":
            
            quiz_data.local_mode = value
            quiz_data.save()

        else:
            
            quiz_data.multichoice_only = value
            quiz_data.save()

        
        response_data = {"success": True, "message": "PUT request was successful"}

    except Exception as e:
        print(e)
        response_data = {"success": False, "message": f"PUT request was not successful: {e}",} 

    return JsonResponse(response_data)


@login_required
def quiz_host(request, quiz_id = None):
    if request.method == "POST":

        if "change_password" in request.POST:

            try:
                quiz_id = int(request.POST["quiz_id"])
                password = request.POST["password"]

                if 0 < len(password) <= 50:

                    quiz_data = QuizInstance.objects.get(id = quiz_id, host=request.user)
                    quiz_data.password = password
                    quiz_data.save()

                    messages.success(request, "Password successfully changed.")
                    url = reverse('quiz_host', args=[quiz_id])
                    return HttpResponseRedirect(url)
                
                else:
                    messages.error(request, "Your password was  too long (> 50)")
                    return redirect("index")

            except Exception as e:
                messages.error(request, "Unexpected error. Error: {}".format(e))
                return redirect("index")
            
        elif "remove_password" in request.POST:

            try:
                quiz_id = int(request.POST["quiz_id"])
            
                quiz_data = QuizInstance.objects.get(id = quiz_id, host=request.user)
                quiz_data.password = ""
                quiz_data.save()

                url = reverse('quiz_host', args=[quiz_id])
                return HttpResponseRedirect(url)

            except Exception as e:
                messages.error(request, "Unexpected error. Error: {}".format(e))
                return redirect("index")

        elif "start_quiz" in request.POST:

            try:
                quiz_id = request.POST["quiz_id"]
                quiz_data = QuizInstance.objects.get(id = quiz_id)
                quiz_data.quiz_step = 1
                quiz_data.save()

                # Group play after host activation
                if quiz_data.play_type == 0 or quiz_data.play_type == 1:

                    # Create initial answers on quiz starting
                    participants = Participant.objects.filter(quiz=quiz_data)
                    question_data = Question.objects.get(quiz=quiz_data.quiz, question_number=quiz_data.question_number)
                    
                    for participant in participants:
                        Answers.objects.create(participant = participant, question = question_data)

                        # Create and store participant (team name and member data) for each started quiz instance
                        team_name_instance = TeamNames.objects.filter(user=participant.user).first()

                        if team_name_instance is not None:
                            team_data = QuizTeam.objects.create(participant = participant, team_name = team_name_instance.name)
                        else:
                            team_data = QuizTeam.objects.create(participant = participant, team_name = participant.user.username)

                        team_members = TeamMembers.objects.filter(user=participant.user)

                        for team_member in team_members:
                            QuizMember.objects.create(quiz_team=team_data, member_name=team_member.name, member_data=team_member)

                    # Group play after host activation
                    if quiz_data.play_type == 1:
                        url = reverse('quiz_redirection', args=[quiz_id])
                        return HttpResponseRedirect(url)
                
                    # Full hosting (no participation)
                    else:
                        url = reverse('quiz_host', args=[quiz_id])
                        return HttpResponseRedirect(url)
            
            except QuizInstance.DoesNotExist:
                messages.error(request, "Sorry, unable to find current quiz instance.")
                url = reverse('quiz_host', args=[quiz_id])
                return HttpResponseRedirect(url)

        elif "verify_answer" in request.POST:
            quiz_id = request.POST["quiz_id"]
            answer_id = int(request.POST["answer_id"])
            status = request.POST["status"]

            try:
                answer = Answers.objects.get(id = answer_id)

                if status == "True":
                    answer.points_awarded = 3
                    answer.verification = False
                    answer.save()
                else:
                    answer.points_awarded = 0
                    answer.verification = False
                    answer.save()

                url = reverse('quiz_host', args=[quiz_id])
                return HttpResponseRedirect(url)

            except Answers.DoesNotExist:
                messages.error(request, "Unable to find the requested answer.")
                url = reverse('quiz_host', args=[quiz_id])
                return HttpResponseRedirect(url)

        elif "next_step" in request.POST:
            try:
                # Read data and update question step 
                quiz_data = QuizInstance.objects.get(id = quiz_id)
                question = Question.objects.get(quiz = quiz_data.quiz, question_number = quiz_data.question_number)
                question_step = QuestionStep.objects.get(quiz_instance = quiz_data, question = question)
                
                question_step.step = True
                question_step.save()

                # Count total questions
                question_count = Question.objects.filter(quiz = quiz_data.quiz).count()
                if question_count == quiz_data.question_number:
                    # End quiz
                    quiz_data.quiz_step = 2
                    quiz_data.completed_on = timezone.now()
                    quiz_data.save()
                else:
                    # Update question number and create new question step
                    quiz_data.question_number += 1
                    quiz_data.save()

                    question = Question.objects.get(quiz = quiz_data.quiz, question_number = quiz_data.question_number)
                    QuestionStep.objects.create(quiz_instance = quiz_data, question = question)

                    # Create new answer objects
                    participants = Participant.objects.filter(quiz=quiz_data)
                    question_data = Question.objects.get(quiz=quiz_data.quiz, question_number=quiz_data.question_number)
                    
                    for participant in participants:
                        Answers.objects.create(participant = participant, question = question_data)

                url = reverse('quiz_host', args=[quiz_id])
                return HttpResponseRedirect(url)

            except Exception as e:
                messages.error(request, "Unexpected error: {}".format())
                url = reverse('quiz_host', args=[quiz_id])
                return HttpResponseRedirect(url)

        else:
            messages.error(request, "No valid POST submission.")
            url = reverse('quiz_host', args=[quiz_id])
            return HttpResponseRedirect(url)
                
    else:
            
        if quiz_id == None: 
            messages.error(request, "Unable to find the requested quiz.")
            return redirect("index")
        else:    
            try:
                
                quiz_data = QuizInstance.objects.get(id = quiz_id)
                quiz_data.participant_set.prefetch_related('quizteam_set', 'quizteam_set__quizmember_set')

                if quiz_data.host == request.user:

                    is_participant = Participant.objects.filter(quiz = quiz_data, user=request.user).exists()
                    
                    if quiz_data.local_mode:
                        quiz_participants = Participant.objects.filter(quiz = quiz_data).exclude(user=request.user)
                    else: 
                        quiz_participants = Participant.objects.filter(quiz = quiz_data)

                    question = Question.objects.get(quiz = quiz_data.quiz, question_number = quiz_data.question_number)
                    question_step = QuestionStep.objects.get(quiz_instance = quiz_data, question = question)
                    five_minutes_ago = timezone.now() - timedelta(minutes=5)
                    online_participant_ids = [participant.id for participant in quiz_participants if participant.user.last_activity >= five_minutes_ago]
                    answers = Answers.objects.filter(question = question, participant__in=quiz_participants)
                    answers_verify = Answers.objects.filter(question = question, participant__in=quiz_participants, question_step = 4, verification=False)
                    next_step = False

                    # Verify if all participants have answered 
                    if answers_verify.count() == quiz_participants.count():
                        next_step = True

                    # Identify correct answer text
                    correct_answer_number = question.correct_answer
                    answer_mapping = {
                        1: question.answer1,
                        2: question.answer2,
                        3: question.answer3,
                        4: question.answer4,
                    }
                    correct_answer = answer_mapping.get(correct_answer_number)

                    # Display results
                    sorted_participant_points = ()
                    
                    if quiz_data.quiz_step == 2:
                        
                        try:

                            # Total scores and ranking
                            participant_points = {}

                            if quiz_data.local_mode:
                                participants = Participant.objects.filter(quiz = quiz_data).exclude(user=request.user)
                            else: 
                                participants = Participant.objects.filter(quiz = quiz_data)

                            # Calculate total points for each participant
                            for participant in participants:
                                answers = Answers.objects.filter(participant=participant)
                                total_points = sum(answer.points_awarded for answer in answers)
                                participant_points[participant.user.username] = (participant, total_points)


                            # Sort participants by total points in descending order
                            sorted_participants = sorted(participant_points.items(), key=lambda x: x[1][1], reverse=True)

                            # Calculate ranks
                            rank = 1
                            prev_points = None
                            for index, (username, (participant, points)) in enumerate(sorted_participants):
                                if points != prev_points:
                                    rank = index + 1
                                participant_points[username] = (participant, points, rank)
                                prev_points = points

                            # Now, sorted_participant_points is a dictionary with ranks included
                            sorted_participant_points = dict(sorted(participant_points.items(), key=lambda x: x[1][1], reverse=True))

                        except Exception as e:
                            messages.error(request, "Error: {}".format(e))
                        
                    
                    return render(request, "quiz_host.html", {
                        "quiz_data": quiz_data,
                        "question_data": question,
                        "participants": quiz_participants,
                        "is_participant": is_participant,
                        "question_step": question_step,
                        "online_participant_ids": online_participant_ids,
                        "answers": answers,
                        "correct_answer": correct_answer,
                        "next_step": next_step,
                        "sorted_participant_points": sorted_participant_points,
                    })
                
                else:
                    messages.error(request, "You do not have permission to host this quiz.")
                    return HttpResponseRedirect(reverse("my_quizzes"))
            
            except Quiz.DoesNotExist:
                messages.error(request, "Unable to find the requested quiz.")
                return HttpResponseRedirect(reverse("index"))
            
            except Question.DoesNotExist:
                messages.error(request, "Unable to find the requested question.")
                return HttpResponseRedirect(reverse("index"))
            
            except Exception as e:
                messages.error(request, "Unexpected error. Error message: {}".format(e))
                return HttpResponseRedirect(reverse("index"))

@csrf_exempt
def update_host_view(request):

    data = json.loads(request.body.decode("utf-8"))
    quiz_id = data['quiz_id']

    try:

        # Querysets
        quiz_data = QuizInstance.objects.get(id = quiz_id)
        question = Question.objects.get(quiz = quiz_data.quiz, question_number = quiz_data.question_number)

        if quiz_data.local_mode:
            quiz_participants = Participant.objects.filter(quiz = quiz_data).exclude(user=request.user)
        else: 
            quiz_participants = Participant.objects.filter(quiz = quiz_data)

        answers_verify = Answers.objects.filter(question = question, participant__in=quiz_participants, question_step = 4, verification=False)
        answers = Answers.objects.filter(question = question, participant__in=quiz_participants)
        
        # Default variables
        next_step = False
        now = timezone.now()
        online_status = []
        answer_steps = []

        # Verify if participants are active
        for participant in quiz_participants:
            
            time_difference = now - participant.user.last_activity

            if time_difference < timedelta(minutes=5):
                online_status.append((participant.id, True))
            else:
                online_status.append((participant.id, False))
        
        # Check answer steps

        text1 = "At: Open question"
        text2 = "At: Multiple choice"
        text3 = "Answer submitted"
        text4 = "Answer requires verification:"

        for answer in answers:
            
            if answer.question_step == 0 or answer.question_step == 1:
                answer_steps.append((answer.participant.id, text1, False))
            elif answer.question_step == 2 and answer.answer_type == 2:
                answer_steps.append((answer.participant.id, text2, False))
            elif answer.question_step == 4 and answer.verification == False:
                answer_steps.append((answer.participant.id, text3, True))
            elif answer.question_step == 4 and answer.verification == True:
                answer_steps.append((answer.participant.id, text4, False, answer.given_answer))

        # Verify if all participants have answered 
        if answers_verify.count() == quiz_participants.count():
            next_step = True

        response_data = {
            'next_step': next_step,
            'online_status': online_status,
            'answer_steps': answer_steps,
        }

        return JsonResponse(response_data)

    except Exception as e:
        response_data = {"success": False, "message": f"PUT request was not successful: {e}",} 
        return JsonResponse(response_data)
    
@csrf_exempt
def question_started(request):
    data = json.loads(request.body.decode("utf-8"))
    answer_id = data['answer_id']

    try:
        answer_data = Answers.objects.get(id=answer_id)

        if answer_data.question_step == 1:
            answer_data.question_step = 2
            answer_data.save()

        response_data = {"success": True, "message": "PUT request was successful",} 

    except Exception as e:
        response_data = {"success": False, "message": f"PUT request was not successful: {e}",} 

    return JsonResponse(response_data)

@csrf_exempt
def forward_question(request):
    data = json.loads(request.body.decode("utf-8"))
    quiz_id = data['quiz_id']
    question_id = data['question_number']
    try:
        quiz_data = QuizInstance.objects.get(id = quiz_id)
        question_data = Question.objects.get(id = question_id)
        question_step = QuestionStep.objects.get(quiz_instance = quiz_data, question = question_data)

        if question_step.step == True:
            response_data = {
            'forward': True,
            'quiz_id': quiz_id,
            }
        else: 
            response_data = {
            'forward': False,
            'quiz_id': quiz_id,
            }

    except Exception as e:
        response_data = {"success": False, "message": "{e}"}
    
    return JsonResponse(response_data)
