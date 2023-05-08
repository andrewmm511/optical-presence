import json
import socket
from ipaddress import ip_address

from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.core import serializers
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import redirect, render

from training import face_extraction

from .models import FacePicture, IPCamera, Person

def is_valid_rtsp_stream(ip: str, port: int) -> bool:
    # Create a socket object
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        # Connect to the IP address and port number
        s.connect((ip, port))

        # Send a basic RTSP request to check if the stream is valid
        s.send(b"OPTIONS rtsp://"+ip.encode()+b":%d RTSP/1.0\r\n\r\n" % port)

        # Wait for a response from the server
        response = s.recv(1024)

        # Check if the response contains "RTSP" (indicating a valid stream)
        if b"RTSP" in response:
            return True
        else:
            return False

    except:
        return False

    finally:
        # Close the socket connection
        s.close()

def home(request: HttpRequest) -> HttpResponse:
    return render(request, 'app/home.html')

def dashboard(request: HttpRequest) -> HttpResponse:
    return render(request, 'app/dashboard.html')

@login_required
def cameras(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST':
        body = json.loads(request.body.decode('utf-8'))
        ip = body.get("domain")
        port = int(body.get("port"))

        if not request.user.is_authenticated:
            return JsonResponse({'status': 'error', 'message': 'User not authenticated'})

        # Check IP validity
        try:
            ip_address(ip)
        except ValueError:
            return JsonResponse({'status': 'error', 'message': f"Invalid IP address: {ip}"})

        # Check if the port is valid
        if not 0 < port <= 65535:
            return JsonResponse({'status': 'error', 'message': f"Invalid port: {port}"})

        # Check the RTSP stream
        if not is_valid_rtsp_stream(ip, port):
            return JsonResponse({'status': 'error', 'message': f"Unable to connect to the RTSP stream: {ip}:{port}"})

        # Add the camera to the model
        new_camera = IPCamera(user=request.user, ip=ip, port=port, connected=True)
        new_camera.save()

        return JsonResponse({'status': 'success'})
    else:
        clickable_step_numbers = [1]
        return render(request, 'app/add_cameras.html', {'clickable_step_numbers': clickable_step_numbers})


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
    classified_faces = FacePicture.objects.filter(user=user).exclude(person=None)
    if request.method == "POST":
        body = json.loads(request.body.decode('utf-8'))
        person_id = body.get("selected_person_id")
        face_picture_id = body.get("current_face_picture_id")

        face_picture = FacePicture.objects.get(id=face_picture_id)
        if person_id is not None:
            person = Person.objects.get(id=person_id)
            face_picture.person = person
            face_picture.save()
        else:
            person = None
            face_picture.delete()
            face_picture = None

        face_pictures = FacePicture.objects.filter(user=request.user, person=None)
        next_face_picture = face_pictures.first()
        next_image_url = next_face_picture.image.url if next_face_picture else None

        if next_image_url:
            return JsonResponse({"status": "continue",
                                 "next_image_url": next_image_url,
                                 "next_face_picture_id": next_face_picture.id,
                                 "person_name": person.name if person else None,
                                 "person_id": person_id,
                                 "processed_faces_count": len(face_pictures),
                                 "face_image_url": face_picture.image.url if face_picture else None,})
        else:
            return JsonResponse({"status": "success", "message": "All faces processed"})
    else:
        context = {
            'face_pictures': face_pictures,
            'total_faces': len(face_pictures),
            'name_list': list(Person.objects.filter(user=user)),
            'current_face_picture': face_pictures.first(),
            'classified_faces': classified_faces,
        }
        return render(request, "app/faces.html", context)