import account.views
import qchain.forms
from django.shortcuts import render
from .models import Adspace, Website, WebsiteForm, AdspaceForm
from django.http import HttpResponse
from django.template import loader
from django.contrib.auth.decorators import login_required

def list(request):
	"""
	List of all adspaces.
	User should be able to filter/search.
	"""
	latest_ad_list = Adspace.objects.all()
	context = {'latest_ad_list': latest_ad_list}
	# TODO: FILTER BY PREFERENCES
	return render(request, 'list.html', context)


def ad_detail(request, ad_id):
	"""
	Adspace details.
	Static without actual functionality.
	"""
	try:
		ad = Adspace.objects.get(pk=ad_id)
	except Adspace.DoesNotExist:
		raise Http404("Adspace does not exist")
	return render(request, 'ad_detail.html', {'ad': ad})

def ad_list(request, web_id):
	"""
	List of adspaces on a website.
	"""
	try:
		site = Website.objects.get(pk=web_id)
		ad_list = Adspace.objects.filter(website=site)
	except Adspace.DoesNotExist:
		raise Http404("Website does not exist")
	return render(request, 'ad_list.html', {'ad_list': ad_list})


@login_required
def agent_details(request):
	"""
	Edit agent details/user profile.
	"""
	if request.method == 'POST':
		form = qchain.forms.DetailForm(request.POST)
		if form.is_valid():
			agent = request.user.agent # agent and user are one-to-one
			agent.birthdate = form.cleaned_data["birthdate"] # get form info (only birthdate for now)
			agent.save()
	else:
		form = qchain.forms.DetailForm()
	# TODO: display current details and confirm changes
	return render(request, 'details.html', {'form': form})


@login_required
def website_list(request):
	"""
	List of websites owned by user.
	User can add or delete websites.
	"""
	context = {}
	try:
		my_website_list = Website.objects.filter(user=request.user) # get websites owned by user
		context['my_website_list'] = my_website_list
	except Website.DoesNotExist:
		context['my_website_list'] = False
	try:
		my_ad_list = Adspace.objects.filter(user=request.user) # get adspaces owned by user
		views_ts = '' # NOTE: PSEUDO TIME SERIES
		for e in my_ad_list:
			views_ts += e.views
		context['views_ts'] = views_ts # TODO: D3 VISUALIZATION
	except Adspace.DoesNotExist:
		context['views_ts'] = False
	# add a new website
	if request.method == 'POST':
		web_form = WebsiteForm(request.POST) # NOTE: TWO FORMS DON'T WORK AT THE SAME TIME
		if form.is_valid():
			new_website = web_form.save(commit=False)
			new_website.user = request.user
			new_website.save()
	else:
		web_form = WebsiteForm()
		ad_form = AdspaceForm()
	context['web_form'] = web_form
	context['ad_form'] = ad_form
	# TODO: WEBSITE DELETION
	return render(request, 'website_list.html', context)


@login_required
def create_ad(request):
	"""
	Create a new adspace.
	"""
	if request.method == 'POST':
		form = AdspaceForm(request.POST) 
		if form.is_valid():
			new_ad = form.save(commit=False)
			new_ad.user = request.user
			new_ad.save()
			# increment website adcount
			current_website = form.cleaned_data["website"]
			current_website.adcount += 1
			current_website.save()
	else:
		form = AdspaceForm()
		form.fields['website'].queryset = Website.objects.filter(user=request.user)
	return render(request, 'create_ad.html', {'form': form})