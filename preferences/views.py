from django.shortcuts import render, redirect
from .models import UserPreference
from .forms import UserPreferenceForm
from django.contrib.auth.decorators import login_required

@login_required
def set_preferences(request):
    obj, created = UserPreference.objects.get_or_create(user=request.user)
    form = UserPreferenceForm(request.POST or None, instance=obj)
    if form.is_valid():
        form.save()
        return redirect('home')  # adjust as needed
    return render(request, 'preferences/set_preferences.html', {'form': form})
