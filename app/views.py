import json
from typing import Dict, List

from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.core import serializers
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import redirect, render

from training import face_extraction
from utils import get_next_image_url, process_selected_name

from .models import Person, FacePicture


def signup(request: HttpRequest) -> HttpResponse:
    """
    Sign up a new user.

    Args:
        request: HttpRequest object containing user details.

    Returns:
        HttpResponse object after creating a new user.
    """
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('index')
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})


@login_required
def register_people(request: HttpRequest) -> HttpResponse:
    """
    Register a new person.

    Args:
        request: HttpRequest object containing person details.

    Returns:
        HttpResponse object after registering a new person.
    """
    if request.method == "POST":
        data = json.loads(request.body)
        name = data.get('name')
        if name:
            person = Person(name=name, user=request.user)
            person.save()
            return JsonResponse({"status": "success", "person_id": person.id})
        else:
            return JsonResponse({"status": "error", "message": "Missing name"}, status=400)
    else:
        existing_persons = Person.objects.filter(user=request.user)
        existing_persons_json = serializers.serialize('json', existing_persons)
        clickable_step_numbers = [2]
        return render(request, "app/register_people.html", {'existing_persons': existing_persons_json, 'clickable_step_numbers': clickable_step_numbers})

@login_required
def upload(request: HttpRequest) -> HttpResponse:
    """
    Upload images for face recognition.

    Args:
        request: HttpRequest object containing the uploaded images.

    Returns:
        HttpResponse object after uploading the images.
    """
    if request.method == "POST":
        full_images = request.FILES.getlist("folder")
        user = request.user

        if full_images:
            extracted_faces_paths = face_extraction.save_faces_from_images(full_images, user)
            request.session["extracted_faces_paths"] = extracted_faces_paths
            request.session["total_faces"] = len(extracted_faces_paths)
            request.session["name_list"] = request.POST.getlist('names')

            return redirect('faces')
        else:
            return render(request, "app/test.html")
    else:
        clickable_step_numbers = [1]
        return render(request, "app/upload.html", {'clickable_step_numbers': clickable_step_numbers})


@login_required
def delete_person(request: HttpRequest, person_id: int) -> JsonResponse:
    """
    Delete a person.

    Args:
        request: HttpRequest object.
        person_id: Integer ID of the person to be deleted.

    Returns:
        JsonResponse object after deleting the person.
    """
    if request.method == "DELETE":
        try:
            person = Person.objects.get(pk=person_id, user=request.user)
            person.delete()
            return JsonResponse({"status": "success"})
        except Person.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Person not found"}, status=404)
    else:
        return JsonResponse({"status": "error", "message": "Invalid request method"}, status=405)


@login_required
def index(request: HttpRequest) -> HttpResponse:
    """
    Render the index page.

    Args:
        request: HttpRequest object.

    Returns:
        HttpResponse object for rendering the index page.
    """
    return render(request, "app/index.html")

@login_required
def faces(request: HttpRequest) -> HttpResponse:
    """
    Display and process faces for face recognition.

    Args:
        request: HttpRequest object.

    Returns:
        HttpResponse object for displaying and processing faces.
    """
    user = request.user
    face_pictures = FacePicture.objects.filter(user=user, person=None)
    if request.method == "POST":
        data = json.loads(request.body)
        person_id = data.get("selected_person_id")
        face_picture_id = data.get("current_face_picture_id")

        person = Person.objects.get(id=person_id)
        face_picture = FacePicture.objects.get(id=face_picture_id)
        face_picture.person = person
        face_picture.save()

        face_pictures = FacePicture.objects.filter(user=request.user, person=None)
        next_face_picture = face_pictures.first()
        next_image_url = next_face_picture.image.url if next_face_picture else None

        if next_image_url:
            return JsonResponse({"status": "continue", "next_image_url": next_image_url, "next_face_picture_id": next_face_picture.id})
        else:
            return JsonResponse({"status": "success", "message": "All faces processed"})
    else:
        context = {
            'face_pictures': face_pictures,
            'total_faces': len(face_pictures),
            'name_list': list(Person.objects.filter(user=user)),
            'current_face_picture': face_pictures.first(),
        }
        return render(request, "app/faces.html", context)