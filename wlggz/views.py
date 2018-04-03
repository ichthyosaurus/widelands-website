# Create your views here.


from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import HttpResponseRedirect

from forms import EditGGZForm


@login_required
def change_password(request):
    """empty text."""
    instance = request.user.wlggz

    if request.method == 'POST':
        form = EditGGZForm(request.POST,
                           instance=instance, files=request.FILES)
        if form.is_valid():
            form.save()

            return HttpResponseRedirect(reverse('profile_edit'))
    else:
        form = EditGGZForm(instance=instance)

    template_params = {
        'wlggz': instance,
        'ggz_form': form,
    }

    return render(request, 'wlggz/edit_ggz.html',
                              template_params)
