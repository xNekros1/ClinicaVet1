# Formulario para agregar historial clínico
class HistorialClinicoForm(forms.ModelForm):
    class Meta:
        model = HistorialClinico
        fields = ['motivo', 'diagnostico', 'tratamiento', 'notas']
        widgets = {
            'motivo': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'diagnostico': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'tratamiento': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'notas': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }
        labels = {
            'motivo': 'Motivo de Consulta',
            'diagnostico': 'Diagnóstico',
            'tratamiento': 'Tratamiento Prescrito',
            'notas': 'Notas Adicionales'
        }
