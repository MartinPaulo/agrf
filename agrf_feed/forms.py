from django import forms

from agrf_feed.apps import AgrfFeedConfig


class GenomeSpaceLoginForm(forms.Form):
    _server_locations = tuple((location, location) for location in
                              AgrfFeedConfig.get_server_locations())
    xrd_provider = forms.ChoiceField(
        label='Choose the:',
        widget=forms.RadioSelect,
        choices=_server_locations
    )

    def __init__(self, *args, **kwargs):
        super(GenomeSpaceLoginForm, self).__init__(*args, **kwargs)
        self.fields['xrd_provider'].initial = self._server_locations[0][0]


class FileUploadForm(forms.Form):
    file_listing = forms.MultipleChoiceField(
        label='Select the files to copy to the GenomeSpace',
        widget=forms.CheckboxSelectMultiple,
        choices=()
    )

    def __init__(self, file_listing, *args, **kwargs):
        super(FileUploadForm, self).__init__(*args, **kwargs)
        self.fields['file_listing'].choices = file_listing


class TargetChooserForm(forms.Form):
    target_directories = forms.ChoiceField(
        label='Select the GenomeSpace target directory',
        widget=forms.RadioSelect,
        choices=()
    )

    def __init__(self, target_choices, *args, **kwargs):
        super(TargetChooserForm, self).__init__(*args, **kwargs)
        self.fields['target_directories'].choices = target_choices
        # now select the first entry in the list of choices
        if len(target_choices):
            self.fields['target_directories'].initial = target_choices[0][0]
