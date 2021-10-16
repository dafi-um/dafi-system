from typing import Any

from django.db.models import QuerySet
from django.forms import (
    ModelChoiceField,
    ModelForm,
    ValidationError,
)
from django.forms.widgets import Select

from .models import (
    PollDesign,
    PollVote,
)


class CustomSelect(Select):

    template_name = 'sanalberto/widgets/select.html'


class PollVoteForm(ModelForm):

    first = ModelChoiceField(
        None, widget=CustomSelect,
        label='Primera opción',
    )

    second = ModelChoiceField(
        None, required=False, widget=CustomSelect,
        label='Segunda opción (opcional)',
    )

    third = ModelChoiceField(
        None, required=False, widget=CustomSelect,
        label='Tercera opción (opcional)',
    )

    def __init__(self, *args, designs: 'QuerySet[PollDesign]', **kwargs) -> None:
        super().__init__(*args, **kwargs)

        # Save the choices now to avoid the field implementation to make
        # additional queries
        choices: list[tuple['int | str', str]] = [
            (obj.id, obj.title) for obj in designs
        ]

        blank: list[tuple['int | str', str]] = [('', '---')]

        self.fields['first'].queryset = designs
        self.fields['first'].choices = choices
        self.fields['second'].queryset = designs
        self.fields['second'].choices = blank + choices
        self.fields['third'].queryset = designs
        self.fields['third'].choices = blank + choices

    class Meta:
        model = PollVote
        fields = ('first', 'second', 'third')

    def clean(self) -> dict[str, Any]:
        data = super().clean()

        if data['third'] and not data['second']:
            data['third'], data['second'] = data['second'], data['third']

        if data['first'] == data['second']:
            raise ValidationError({
                'second': 'No puede ser el mismo que la primera opción',
            })
        if data['third']:
            if data['first'] == data['third']:
                raise ValidationError({
                    'third': 'No puede ser el mismo que la primera opción',
                })
            if data['second'] == data['third']:
                raise ValidationError({
                    'third': 'No puede ser el mismo que la segunda opción',
                })

        return data
