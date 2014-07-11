import base64
import json

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.core import serializers
from django.core.urlresolvers import resolve, reverse
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET

from functools import wraps

from .models import Bathroom
from .forms import BathroomForm


def auth_login(func):
	@wraps(func)
	def inner(request, *args, **kwargs):
		if request.META.get('HTTP_AUTHORIZATION', None):
			auth = request.META.get('HTTP_AUTHORIZATION', None).split()
			if len(auth) == 2:
				if auth[0].lower() == 'basic':
					# Currently, only basic http auth is used.
					uname, passwd = base64.b64decode(auth[1]).split(':')
					user = authenticate(username=uname, password=passwd)
					if user:
						login(request, user)
		return func(request, *args, **kwargs)
	return inner


@require_GET
def bathrooms(request):
	if request.META.get('HTTP_ACCEPT', False) and 'application/json' in request.META.get('HTTP_ACCEPT'):
		data = []
		for b in Bathroom.objects.all():
			data.append({
				'id':b.pk,
				'name':b.name,
				'description':b.description,
				'stalls':b.stalls,
				'lon':b.lon,
				'lat':b.lat,
				'locked':b.is_occupied()
				})
		return HttpResponse(json.dumps(data), mimetype='application/json')
	d = {'bathrooms':Bathroom.objects.all()}
	return render(request, "potty/bathrooms.html", d)


@require_GET
def bathroom(request, bathroom_id):
	d = {'bathroom':get_object_or_404(Bathroom, pk=bathroom_id)}
	return render(request, "potty/bathroom.html", d)


@auth_login
@login_required
def create(request):
	if request.method == 'POST':
		form = BathroomForm(request.POST)
		if form.is_valid():
			br = form.save()
			messages.success(request, "Way to go.. you made a bathroom")
			return redirect('bathroom', bathroom_id=br.pk)
	else:
		form = BathroomForm(initial={'createdBy':request.user})
	return render(request, 'potty/bathroom_form.html', {'form':form})


@csrf_exempt
@require_POST
@auth_login
@login_required
def lock(request, bathroom_id):
	try:
		br = get_object_or_404(Bathroom, pk=bathroom_id)
		ok = br.lock(get_object_or_404(User, pk=request.POST['userid']))
		if not ok:
			messages.error(request, "OH NO!! could not lock %s - now you gotta hold it!" % br.name)
		else:
			messages.success(request, "SUCCESS! %s locked - go do your thing" % br.name)
	except Exception, e:
		messages.error(request, e.message)
		ok = False

	if request.META.get('HTTP_ACCEPT', False) and 'application/json' in request.META.get('HTTP_ACCEPT'):
		# this was from a client... clear messages and logout user
		storage = messages.get_messages(request)
		logout(request)
		for m in storage:
			pass
		if ok:
			return HttpResponse(status=200)
		else:
			return HttpResponse(status=400)

	path = request.POST.get('redirect', None)
	if path:
		return redirect(resolve(path).url_name)	
	return redirect('bathroom', bathroom_id=bathroom_id)

@csrf_exempt
@require_POST
@auth_login
@login_required
def unlock(request, bathroom_id):
	try:
		br = get_object_or_404(Bathroom, pk=bathroom_id)
		ok = br.unlock(get_object_or_404(User, pk=request.POST['userid']))
		if not ok:
			messages.error(request, "ERROR: could not unlock %s - contact tim" % br.name)
		else:
			messages.success(request, "SUCCESS: %s unlocked - now others can go sully the potty" % br.name)
	except Exception, e:
		messages.error(request, e.message)
		ok = False

	if request.META.get('HTTP_ACCEPT', False) and 'application/json' in request.META.get('HTTP_ACCEPT'):
		# this was from a client... clear messages and logout user
		storage = messages.get_messages(request)
		logout(request)
		for m in storage:
			pass
		if ok:
			return HttpResponse(status=200)
		else:
			return HttpResponse(status=400)

	path = request.POST.get('redirect', None)
	if path:
		return redirect(resolve(path).url_name)
	return redirect('bathroom', bathroom_id=bathroom_id)

@require_GET
def status(request, bathroom_id):
	br = get_object_or_404(Bathroom, pk=bathroom_id)
	d = {"locked":br.is_occupied(), "bathroom_id":br.pk}
	d['locked_by'] = None
	if br.who_is_bogging_you_down():
		d['locked_by'] = br.who_is_bogging_you_down().username
	return HttpResponse(json.dumps(d), mimetype="application/json")
