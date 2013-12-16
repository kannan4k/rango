from django.template import RequestContext
from django.shortcuts import render_to_response
from rango.models import Category, Page
from rango.forms import CategoryForm, PageForm, UserForm, UserProfileForm
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth import logout

def index(request):
	context = RequestContext(request)
	#Get the top five categories
	category_list = Category.objects.order_by('-likes')[:5]
	context_dict = {'categories':category_list}
	for category in category_list:
		category.url = category.name.replace(' ','_')
	return render_to_response('rango/index.html',context_dict, context)

def about(request):
	context = RequestContext(request)
	context_dict = {'boldmessage':"kannan.jpg"}
	return render_to_response('rango/about.html',context_dict, context)

def category(request, category_name_url):
	# REquest our context from the request passed to us
	context = RequestContext(request)
	category_name = category_name_url.replace('_',' ')
	context_dict = {'category_name':category_name}
	try: 
		category = Category.objects.filter(name = category_name ) #Get the Category Object
		pages = Page.objects.filter(category=category) #Get the corresponding pages for the Category Object
		context_dict['pages'] = pages   #Adding the pages to the dict
		context_dict['category']= category   #Adding the category to dict to check the category in the template
		context_dict['category_name_url']= category_name_url
	except Category.DoesNotExist:
		pass
	return render_to_response('rango/category.html', context_dict, context)
		
	
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
	return render_to_response('rango/add_category.html', {'form':form}, context)

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
	return render_to_response('rango/add_page.html',{'category_name_url':category_name_url, 'category_name':category_name,'form':form},context)
		
			
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

    # Take the user back to the homepage.
    return HttpResponseRedirect('/rango/')




