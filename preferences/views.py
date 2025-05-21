from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from .models import UserPreference
from .forms import UserPreferenceForm

@login_required
def set_preferences(request):
    obj, created = UserPreference.objects.get_or_create(user=request.user)
    form = UserPreferenceForm(request.POST or None,
                              instance=obj, user=request.user)
    if form.is_valid():
        form.save()
        return redirect('home')  # or wherever makes sense
    return render(request, 'preferences/set_preferences.html', {'form': form})
