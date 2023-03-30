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

from .models import Person


def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('index')
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})

def test(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        # User has submitted the form, now process the data
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
        return render(request, "app/test.html")
    
@login_required
def register_people(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        data = json.loads(request.body)
        name = data.get('name')
        person = Person(name=name, user=request.user)
        person.save()
        return JsonResponse({"status": "success", "person_id": person.id})
    else:
        existing_persons = Person.objects.filter(user=request.user)
        existing_persons_json = serializers.serialize('json', existing_persons)
        clickable_step_numbers = [2]
        return render(request, "app/register_people.html", {'existing_persons': existing_persons_json, 'clickable_step_numbers': clickable_step_numbers})

@login_required
def upload(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        # User has submitted the form, now process the data
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
    return render(request, "app/index.html")

@login_required
def faces(request: HttpRequest):
    if request.method == "POST":
        data = json.loads(request.body)
        extracted_faces: List[str] = request.session.get("extracted_faces_paths", [])
        name_list: List[str] = request.session.get("name_list", [])

        if request.method == "POST":
            
            data: Dict[str, str] = json.loads(request.body)

            process_selected_name(data.get("selected_name"), data.get("current_image"))

            extracted_faces.pop(0)
            request.session["extracted_faces"] = extracted_faces

            next_image_url: str = "/" + extracted_faces[0]

        if next_image_url:
            return JsonResponse({"status": "continue", "next_image_url": next_image_url, "extracted_faces_paths": extracted_faces})
        else:
            return JsonResponse({"status": "success", "message": "All faces processed"})
    else:
        context = {
            'extracted_faces_paths': request.session.get("extracted_faces_paths", []),
            'total_faces': request.session.get("total_faces", 0),
            'name_list': request.session.get("name_list", []),
            'current_image': request.session.get("extracted_faces_paths", [])[0],
        }
        return render(request, "app/faces.html", context)