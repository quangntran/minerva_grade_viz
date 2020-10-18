from django import forms

class GradeForm(forms.Form):
    
    file = forms.FileField(label='Upload file', label_suffix="")
    lo_list = forms.CharField(label='LO list', max_length=500,label_suffix="" , widget=forms.Textarea(attrs={'rows':4, 'cols':15}))
    co_list = forms.CharField(label='CO list', max_length=500, label_suffix="", widget=forms.Textarea(attrs={'rows':4, 'cols':15}))
    assignment_title = forms.CharField(label='Assignment titles', max_length=500, label_suffix="", widget=forms.Textarea(attrs={'rows':4, 'cols':15}))
    assignment_weight = forms.CharField(label='Assignment weights', max_length=500, label_suffix="")
    default_lo = forms.CharField(label='LO to highlight in LO evolution graph', max_length=500, label_suffix="",  required=False, widget=forms.Textarea(attrs={'rows':4, 'cols':15}))
    
    
    
#    
#    
#    <input type="file" name="document">
#    <label for="lo_list">LO in order</label><br>
#    <input type="text" id="lo_list" name="lo_list"><br>
#    <label for="co_list">CO in order</label><br>
#    <input type="text" id="co_list" name="co_list"><br>
#    <label for="assignment_title">Assignment Titles</label><br>
#    <input type="text" id="assignment_title" name="assignment_title"><br>
#    <label for="assignment_weight">Assignment Weights</label><br>
#    <input type="text" id="assignment_weight" name="assignment_weight"><br>
#    <label for="default_lo">LOs to highlight in LO evolution graph</label><br>
#    <input type="text" id="default_lo" name="default_lo"><br>

#widget=forms.Textarea(attrs={'rows':4, 'cols':15})