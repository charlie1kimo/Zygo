from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Submit, HTML, Button, Row, Field
from crispy_forms.bootstrap import AppendedText, PrependedText, FormActions


class TravelerSetupForm(forms.Form):
    num_rows = forms.IntegerField(
        label = "Number of Rows:",
        required = True)

    def __init__(self, *args, **kwargs):
        super(TravelerSetupForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'id-travelerSetupForm'
        self.helper.form_class = 'blueForms'
        self.helper.form_method = 'post'
        self.helper.form_action = '/track/travelerform/'

        self.helper.add_input(Submit('submit', 'Submit'))

class TravelerForm(forms.Form):
    op_num = forms.IntegerField(
        label = "OP NO",
        required = True)
    work_center = forms.ChoiceField(
        label = "WORK CENTER",
        choices = ((1,"ROQA"), 
                    (2, "ROLP"), 
                    (3, "ROCC"), 
                    (4, "ROAS"), 
                    (5, "ROSH"), 
                    (6, "ROMT"), 
                    (7, "ROPS"),
                    (8, "ROIB"), 
                    (9, "ROCM"),
                    (10, "ROPC"),
                    (11, "ROEN"),
                    (12, "ROHS"),
                    (13, "ROMS"),
                    (14, "ROPT"),
                    (15, "RO_SHIP"),
                    (16, "ROVN"),
                    (17, "ROEV"),
                    ("VNDR", "VNDR")),
        required = True)
    routing_steps = forms.CharField(
        label = "Routing Steps",
        required = True)
    machine_resource_requirements = forms.CharField(
        widget = forms.Textarea(attrs={'rows': 1}),
        label = "Machine Resource Requirements",
        required = False)
    labor_resource_requirements = forms.CharField(
        widget = forms.Textarea(attrs={'rows': 1}),
        label = "Labor Resource Requirements",
        required = False)
    machine_resource_utilization_time = forms.CharField(
        widget = forms.Textarea(attrs={'rows': 1}),
        label = "Machine Resource Utilization Time (hrs)",
        required = False)
    labor_resource_utilization_time = forms.CharField(
        widget = forms.Textarea(attrs={'rows': 1}),
        label = "Labor Resource Utilization Time (hrs)",
        required = False)
    engineering_cycle_time_estimate = forms.IntegerField(
        label = "Engineering Cycle Time Estimate (days)",
        required = True)

# example form using the crispy forms
class ExampleForm(forms.Form):
    like_website = forms.TypedChoiceField(
        label = "Do you like this website?",
        choices = ((1, "Yes"), (0, "No")),
        coerce = lambda x: bool(int(x)),
        widget = forms.RadioSelect,
        initial = '1',
        required = True,
    )

    favorite_food = forms.CharField(
        label = "What is your favorite food?",
        max_length = 80,
        required = True,
    )

    favorite_color = forms.CharField(
        label = "What is your favorite color?",
        max_length = 80,
        required = True,
    )

    favorite_number = forms.IntegerField(
        label = "Favorite number",
        required = False,
    )

    notes = forms.CharField(
        label = "Additional notes or feedback",
        required = False,
    )

    def __init__(self, *args, **kwargs):
        super(TravelerForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'id-travelerForm'
        self.helper.form_class = 'blueForms'
        self.helper.form_method = 'post'
        self.helper.form_action = 'submit_survey'

        self.helper.add_input(Submit('submit', 'Submit'))

# example using crispy form and layout helper
class MessageForm(forms.Form):
    text_input = forms.CharField()
 
    textarea = forms.CharField(
        widget = forms.Textarea(),
    )
 
    radio_buttons = forms.ChoiceField(
        choices = (
            ('option_one', "Option one is this and that be sure to include why it's great"), 
            ('option_two', "Option two can is something else and selecting it will deselect option one")
        ),
        widget = forms.RadioSelect,
        initial = 'option_two',
    )
 
    checkboxes = forms.MultipleChoiceField(
        choices = (
            ('option_one', "Option one is this and that be sure to include why it's great"), 
            ('option_two', 'Option two can also be checked and included in form results'),
            ('option_three', 'Option three can yes, you guessed it also be checked and included in form results')
        ),
        initial = 'option_one',
        widget = forms.CheckboxSelectMultiple,
        help_text = "<strong>Note:</strong> Labels surround all the options for much larger click areas and a more usable form.",
    )
 
    appended_text = forms.CharField(
        help_text = "Here's more help text"
    )
 
    prepended_text = forms.CharField()
 
    prepended_text_two = forms.CharField()
 
    multicolon_select = forms.MultipleChoiceField(
        choices = (('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5')),
    )
 
    # Uni-form
    helper = FormHelper()
    helper.form_class = 'form-horizontal'
    helper.layout = Layout(
        Field('text_input', css_class='input-xlarge'),
        Field('textarea', rows="3", css_class='input-xlarge'),
        'radio_buttons',
        Field('checkboxes', style="background: #FAFAFA; padding: 10px;"),
        AppendedText('appended_text', '.00'),
        PrependedText('prepended_text', '<input type="checkbox" checked="checked" value="" id="" name="">', active=True),
        PrependedText('prepended_text_two', '@'),
        'multicolon_select',
        FormActions(
            Submit('save_changes', 'Save changes', css_class="btn-primary"),
            Submit('cancel', 'Cancel'),
        )
    )