from django.shortcuts import render
from django.http import HttpResponse
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from django.views.decorators.http import require_http_methods
from .forms import VideoUploadForm
# from django.shortcuts import get_object_or_404
# from .models import Video
import ffmpeg
import os
import sys
import cloudinary
import cloudinary.uploader
import cloudinary.api
if not os.getenv('CLOUDINARY_API_SECRET'):
    raise Exception('CLOUDINARY_API_SECRET environment variable is not set.')

cloudinary.config(
  cloud_name = 'devsprout2023',
  api_key = '524769167723622',
  api_secret = os.getenv('CLOUDINARY_API_SECRET'),
  secure = True,
)



def index(request):
    return render(request, 'videos/index.html')

@require_http_methods(["GET", "POST"])
def create(request):
    if request.method == "GET":
        form = VideoUploadForm()
        return render(request, "videos/create.html", {"form": form})
    elif request.method == "POST":
        form = VideoUploadForm(request.POST, request.FILES)
        if form.is_valid():
            video_file = form.cleaned_data['video_file']
            video_title = form.cleaned_data['title']

            fs = FileSystemStorage()
            filename = fs.save(video_file.name, video_file)
            input_path = fs.path(filename)
            name, ext = os.path.splitext(filename)
            output_path = fs.path(name + "_preview" + ext)

            try:
                trimmed_duration = get_trimmed_video_duration(input_path)
                trim_video(input_path, output_path, trimmed_duration)
                full_video_url = upload_to_cloudinary(video_file, video_title)
                preview_video_url = upload_to_cloudinary(output_path, f"{video_title}_preview", is_file_path=True)
                print_debug_info(full_video_url)
                print_debug_info(preview_video_url)
            except Exception as e:
                print(e, file=sys.stderr)
                fs.delete(filename)
                return HttpResponse("An error occurred while processing the video.", status=500)
            finally:
                cleanup_files(fs, filename, output_path)

            return HttpResponse("Video uploaded successfully!")

def get_trimmed_video_duration(input_path):
    video_info = ffmpeg.probe(input_path)
    duration = float(video_info['streams'][0]['duration'])
    return duration / 3

def trim_video(input_path, output_path, trimmed_duration):
    ffmpeg.input(input_path).output(output_path, t=trimmed_duration).run(overwrite_output=True)

def upload_to_cloudinary(file, public_id, is_file_path=False):
    if is_file_path:
        with open(file, 'rb') as video_file:
            res = cloudinary.uploader.upload_large(video_file, 
                resource_type="video",
                public_id=public_id)
    else:
        res = cloudinary.uploader.upload_large(file, 
            resource_type="video",
            public_id=public_id)
    return res['secure_url']

def print_debug_info(url):
    print("*" * 20)
    print(url)
    print("*" * 20)

def cleanup_files(fs, *file_paths):
    for path in file_paths:
        fs.delete(path)
    
# def detail(request, video_id):
#     video = get_object_or_404(Video, pk=video_id)
#     return render(request, 'videos/index.html', {'video': video})


