from django import forms

from admin_panel.models import SubtitleUpload


class SubtitleUploadForm(forms.ModelForm):
    class Meta:
        model = SubtitleUpload
        fields = ['file']
