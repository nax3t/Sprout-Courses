from django import forms

class VideoUploadForm(forms.Form):
    title = forms.CharField(max_length=100)
    video_file = forms.FileField()