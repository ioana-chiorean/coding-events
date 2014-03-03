from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core import serializers
from django.core.urlresolvers import reverse
from django.conf import settings


from api.models import Event
from web.forms.event_form import AddEvent
from web.processors.event import get_event
from web.processors.event import create_or_update_event
from web.processors.event import get_lat_lon_from_user_ip
from web.processors.event import get_country_from_user_ip
from api.processors import get_approved_events
from api.processors import get_approved_events
from api.processors import get_pending_events

from web.decorators.access_right import can_edit_event

"""
Do not Query the database directly from te view.
Use a processors file within the api app, put all of your queries there and
then call your newly created function in view!!! .-Erika
"""


def index(request):
	events = get_approved_events()
	map_events = serializers.serialize('json', events, fields=('geoposition', 'title', 'pk', 'slug'))

	try:
		user_ip = get_client_ip(request)
		lan_lon = get_lat_lon_from_user_ip(user_ip)
		country = get_country_from_user_ip(user_ip)
	except:
		lan_lon = (46.0608144,14.497165600000017)
		country = None

	if country:
		latest_events = get_approved_events(limit=5, order='pub_date', country_code=country['country_code'])
	else:
		latest_events = get_approved_events(limit=5, order='pub_date')

	return render_to_response(
		'pages/index.html', {
			'latest_events': latest_events,
		    'map_events': map_events,
		    'lan_lon': lan_lon,
		    'country': country,
		},
		context_instance=RequestContext(request))


@login_required
def add_event(request):
	event_form = AddEvent()
	if request.method =="POST":
		event_form = AddEvent(data=request.POST, files=request.FILES)
		if event_form.is_valid():
			event_data = {}
			event_data.update(event_form.cleaned_data)
			event = create_or_update_event(**event_data)
			return render_to_response(
					'pages/thankyou.html',
					{'title': event.title, 'event_id': event.id, 'slug': event.slug},
					context_instance=RequestContext(request))
	context = {"form": event_form}
	return render_to_response("pages/add_event.html", context, context_instance=RequestContext(request))


def view_event(request, event_id, slug):
	event = get_object_or_404(Event, pk=event_id, slug=slug)
	context = {'event': event}
	return render_to_response("pages/view_event.html", context, context_instance=RequestContext(request))


def search_event(request):
	pass


def thankyou(request):
	return render_to_response('pages/thankyou.html')

@login_required
@can_edit_event
def edit_event(request,event_id):
	event = get_event(event_id)
	# Create a dictionary out of db data to populate the edit form
	event_data = event.__dict__
	tags = []
	for tag in event.tags.all():
		tags.append(tag.name)
	event_data['tags'] = ",".join(tags)
	event_form = AddEvent(data=event_data)
	if request.method =="POST":
		event_form = AddEvent(data=request.POST, files=request.FILES)
		if event_form.is_valid():
			event_data = event_form.cleaned_data
			event = create_or_update_event(event_id,**event_data)
			url = reverse('web.view_event', kwargs={'event_id': event.id, 'slug': event.slug})
			return HttpResponseRedirect(url)
	# Passing event address separately to be used in map JS
	context= {"form" : event_form, "address" : event_data['location']}
	return render_to_response("pages/add_event.html", context, context_instance=RequestContext(request))


@login_required
def list_pending_events(request, country_code):

	"""
	Display a list of pending events.
	"""

	event_list = get_pending_events(country_code=country_code)
	user = request.user
	if not user.profile.is_ambassador():
		messages.error(request, "You don't have permissions to see this page")
		return HttpResponseRedirect(reverse("web.index"))
	else:
		return render_to_response("pages/list_events.html", {
									'event_list': event_list,
									'status': 'pending',
									'country_code': country_code,
									},
									context_instance=RequestContext(request))


@login_required
def list_approved_events(request,country_code):
	"""
	Display a list of approved events.
	"""

	event_list = get_approved_events(country_code = country_code)
	context = {'event_list': event_list, 'status': 'approved','country_code': country_code}

	return render_to_response("pages/list_events.html", context, context_instance=RequestContext(request))


def guide(request):
	return render_to_response('pages/guide.html')


def get_client_ip(request):
	if settings.DEBUG:
		return '93.103.53.11'

	x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
	if x_forwarded_for:
		ip = x_forwarded_for.split(',')[0]
	else:
		ip = request.META.get('REMOTE_ADDR')
	return ip

#@login_required
#@can_edit_event


def approve_event(request,event_id):
	if request.method == 'GET':
		#event_id=request.GET["event_id"]
		event_data= {"status": "APPROVED"}
		event=create_or_update_event(event_id=event_id,**event_data)
		status=event.status
		return HttpResponse(status)
