from django.template import RequestContext
from django.shortcuts import render_to_response
from rango.models import Category, Page, UserProfile
from rango.forms import CategoryForm, PageForm, UserForm, UserProfileForm
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth import logout
from django.contrib.auth.models import User
from datetime import datetime
from rango.bing_search import run_query

def get_category_list(max_results=0, starts_with=''):
	
	if starts_with:
		cat_list = Category.objects.filter(name__startswith = starts_with)
	else:
		cat_list = Category.objects.all()
		
	if max_results > 0:
		if len(cat_list) > max_results:
			cat_list = cat_list[:max_results]
			
	for cat in cat_list:
		cat.url = cat.name.replace(' ','_')
	return cat_list


def index(request):
	context = RequestContext(request)
	#Get the top five categories		
	category_list = Category.objects.order_by('-likes')[:5]
	context_dict = {'categories':category_list}
	for category in category_list:
		category.url = category.name.replace(' ','_')
	
	page_list = Page.objects.order_by('-views')[:5]
	context_dict['pages'] = page_list
	context_dict['cats'] = get_category_list()
	#### NEW CODE ####
	if request.session.get('last_visit'):
		# The session has a value for the last visit
		last_visit_time = request.session.get('last_visit')
		visits = request.session.get('visits', 0)

		if (datetime.now() - datetime.strptime(last_visit_time[:-7], "%Y-%m-%d %H:%M:%S")).days > 0:
			request.session['visits'] = visits + 1
			request.session['last_visit'] = str(datetime.now())
	else:
		# The get returns None, and the session does not have a value for the last visit.
		request.session['last_visit'] = str(datetime.now())
		request.session['visits'] = 1
	#### END NEW CODE ####
	return render_to_response('rango/index.html', context_dict, context)

def about(request):
	context = RequestContext(request)
	if request.session.get('visits'):
		count = request.session.get('visits')
	else:
		count = 0
	context_dict = {'boldmessage':"kannan.jpg",'visits': count}
	context_dict['cats'] = get_category_list()
	# remember to include the visit data
	return render_to_response('rango/about.html', context_dict, context)

def category(request, category_name_url):
	# REquest our context from the request passed to us
	context = RequestContext(request)
	category_name = category_name_url.replace('_',' ')
	context_dict = {'category_name':category_name}
	context_dict['cats'] = get_category_list()
	try: 
		category = Category.objects.get(name=category_name)
		pages = Page.objects.filter(category=category) #Get the corresponding pages for the Category Object)\
		context_dict['pages'] = pages   #Adding the pages to the dict
		context_dict['category']= category   #Adding the category to dict to check the category in the template
		context_dict['category_name_url']= category_name_url
	except Category.DoesNotExist:
		pass
	
	#Search Functionality
	result_list = []
	if request.method == 'POST':
		query = request.POST['query'].strip()
		if query:
			result_list = run_query(query)
	context_dict['cats']=get_category_list()
	context_dict['result_list'] = result_list
	
	return render_to_response('rango/category.html', context_dict, context)
		
@login_required	
def add_category(request):
	# Get the context
	context = RequestContext(request)
	#A HTTP Request?
	if request.method == 'POST':
		form = CategoryForm(request.POST)
		if form.is_valid():
			form.save(commit=True)
			return index(request)
		else:
			print form.errors
	else:
		form= CategoryForm()
	cat_list = get_category_list()
	return render_to_response('rango/add_category.html', {'form':form,'cats':cat_list}, context)

@login_required
def add_page(request, category_name_url):
	context = RequestContext(request)
	category_name = category_name_url.replace('_',' ')
	if request.method == 'POST':
		form = PageForm(request.POST)
		if form.is_valid():
			page = form.save(commit=False)
			cat = Category.objects.get(name=category_name)
			page.category = cat
			page.views= 0
			page.save()
			return category(request, category_name_url)
		else:
			print form.errors
	else:
		form = PageForm()
	cat_list = get_category_list()
	for cat in cat_list:
		print cat.url
	return render_to_response('rango/add_page.html',{'category_name_url':category_name_url,'cats':cat_list, 'category_name':category_name,'form':form},context)
		
			
def register(request):
	context = RequestContext(request)
	registered=False
	if request.method == 'POST': # Checks POST Request
		user_form = UserForm(data=request.POST) 
		profile_form = UserProfileForm(data=request.POST)
		if user_form.is_valid() and profile_form.is_valid():
			user = user_form.save()
			user.set_password(user.password) # TO set the Hashed Password
			user.save()
			profile = profile_form.save(commit=False) #To set the picture and website 
			profile.user = user
			if 'picture' in request.FILES:
				profile.picture = request.FILES['picture']
			profile.save()
			registered= True
		else: 
			print user_form.errors, profile_form.errors
	else:
		user_form = UserForm()
		profile_form = UserProfileForm()
	context_dict = {'user_form':user_form, 'profile_form': profile_form, 'registered': registered}
	return render_to_response('rango/register.html', context_dict, context)

def user_login(request):
	context = RequestContext(request)
	
	if request.method == 'POST':
		username = request.POST['username']
		password = request.POST['password']
		user = authenticate(username=username, password=password)
		
		if user is not None:
			if user.is_active:
				login(request,user)
				return HttpResponseRedirect('/rango/')
			else:
				return HttpResponse("Your Rango account is disabled")
		else:
			print "Invalid login Details:{0}, {1} ".format(username,password)
			return HttpResponse("Invalid Login Details Supplied ")
		
	else: 
		return render_to_response('rango/login.html', {}, context)
			
			
			
@login_required
def restricted(request):
	return HttpResponse("Since you're logged in, you can see this text!")
		
	
# Use the login_required() decorator to ensure only those logged in can access the view.
@login_required
def user_logout(request):
	# Since we know the user is logged in, we can now just log them out.
	logout(request)
	# Take the user back to the homepage
	return HttpResponseRedirect('/rango/')

def search(request):
	context = RequestContext(request)
	result_list = []
	
	if request.method == 'POST':
		query = request.POST['query'].strip()
		
		if query:
			result_list = run_query(query)
		
	return render_to_response('rango/search.html', {'result_list':result_list,'cats': get_category_list()}, context )

@login_required			
def profile(request):
	context = RequestContext(request)
	u = User.objects.get(username = request.user)
	try:
		up = UserProfile.objects.get(user = u)
	except:
		up = None
	return render_to_response('rango/profile.html',{'cats': get_category_list(),'up':up}, context )
	
def track_url(request):
	if request.method =='GET':
		if 'page_id' in request.GET:
			page_id = request.GET['page_id']
			try:
				page = Page.objects.get(id=page_id)
				page.views = page.views+1
				page.save()
				url = page.url
			except:
				pass
	return HttpResponseRedirect(url)
			
@login_required
def like_category(request):
	cat_id = None
	if request.method == 'GET':
		cat_id = request.GET['category_id']
	likes = 0
	if cat_id:
		category = Category.objects.get(id = int(cat_id))
		if category:
			likes = category.likes +1
			category.likes = likes
			category.save()
		
	return HttpResponse(likes)

@login_required
def auto_add_page(request):
	context = RequestContext(request)
	context_dict ={}
	if request.method == 'GET':
		title = request.GET['title']
		url = request.GET['url']
		cat_id = request.GET['category_id']
		if cat_id:
			category = Category.objects.get(id = int(cat_id))
			Page.objects.get_or_create(category=category, title=title, url=url)
			pages = Page.objects.filter(category=category).order_by('-views')
			context_dict['pages'] = pages
	return render_to_response('rango/page_list.html', context_dict, context)

def suggest_category(request):
	context = RequestContext(request)
	starts_with = ''
	if request.method == 'GET':
		starts_with = request.GET['suggestion']
	else:
		starts_with = request.POST['suggestion']

	cats = get_category_list(8, starts_with)
	return render_to_response('rango/category_list.html', {'cats': cats }, context)
