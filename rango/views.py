from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login
from rango.models import Category, Page
from rango.forms import CategoryForm, PageForm, UserForm, UserProfileForm

def index( request ):
	context_dict = {}
	
	# Query the database for a list of ALL categories currently stored.
	# Order the categories by no. likes in descending order.
	# Retrieve the top 5 only - or all if less than 5.
	# Place the list in our context_dict dictionary which will be passed to the template.
	category_list = Category.objects.order_by('-likes')[:5]
	context_dict['categories'] = category_list

	# Retrieve top 5 viewed pages from the Page table.
	# Place them in the context dictionary to be used by the template.
	top_pages = Page.objects.order_by('-views')[:5]
	context_dict['top_pages'] = top_pages
	
	# Return a rendered response to send to the client.
	# We make use of the shortcut function to make our lives easier.
	# Note that the second parameter is the template we wish to use.
	return render( request, 'rango/index.html', context_dict )

def category( request, category_name_slug ):
	# Create a context dictionary which we can pass to the template rendering page.
	context_dict = {}

	try:
		# The .get() method returns one model instance or raises an exception.
		category = Category.objects.get(slug=category_name_slug)
		context_dict['category_name'] = category.name
		context_dict['category_name_slug'] = category.slug

		# Retrieve all of the associated pages.
		pages = Page.objects.filter(category=category)
		
		# Adds our results list to the template context dictionary.
		context_dict['pages'] = pages
	except Category.DoesNotExist:
		# context_dict will remain empty. We will let the template display a "no category" message
		pass
	return render( request, 'rango/category.html', context_dict )

def add_category(request):
	# An HTTP POST?
	if request.method == 'POST':
		form = CategoryForm(request.POST)

		# Have we been provided with a valid form?
		if form.is_valid():
			# Save the new category to the database.
			form.save(commit=True)
		
			# Now call the index() view.
			# The user will be shown the homepage.
			return index(request)
		else:
			# The supplied form contained errors - just print them to the terminal.
			#return HttpResponse( form.errors )
			#return index(request)
			print form.errors
	else:
		# If the request was not a POST, display the form to enter details.
		form = CategoryForm()

	# Bad form (or form details), no form supplied...
	# Render the form with error messages (if any).
	return render(request, 'rango/add_category.html', {'form': form})

def add_page( request, category_name_slug ):
	try:
		cat = Category.objects.get(slug=category_name_slug)
	except Category.DoesNotExist:
		cat = None
	
	if request.method == 'POST':
		form = PageForm( request.POST )
		if form.is_valid():
			if cat:
				page = form.save(commit=False)
				page.category = cat
				page.views = 0
				page.save()
				return category(request, category_name_slug)
		else:
			print form.errors
	else:
		form = PageForm()

	context_dict = {'form':form, 'category':cat ,'category_name_slug':category_name_slug}
	return render(request, 'rango/add_page.html', context_dict)	

def register( request ):
    # A boolean value for telling the template whether the registration
    # was successful. Set to False initially. Code changes value to True
    # when registration succeeds.
    registered = False

    # If it's a HTTP POST, we're interested in processing form data.
    if request.method == 'POST':
        # Attempt to grab information from the raw form information.
        # Note that we make use of both UserForm and UserProfileForm. 
        user_form = UserForm( data=request.POST ) 
        profile_form = UserProfileForm( data=request.POST ) 

        # If the two forms are valid...
        if user_form.is_valid() and profile_form.is_valid():
            # Save the user's form data to the database
            user = user_form.save()

            # Now we hash the password with the set_password method.
            # Once hashed, we can update the user object.
            user.set_password( user.password )
            user.save()

            # Now sort out the UserProfile instance.
            # Since we need to set the user attribute ourselves, we
            # set commit=False. This delays saving the model until 
            # we are ready to avoid integrity problems.
            profile = profile_form.save( commit=False )
            profile.user = user

            # Did the user provide a profile picture?
            # If so, we need to get it from the input form and put it
            # in the UserProfile model.
            if 'picture' in request.FILES:
                profile.picture = request.FILES[ 'picture' ]

            # Now we save the UserProfile model instance.
            profile.save()

            # Update our variable to tell the template registration
            # was successful.
            registered = True
            
        # Invalid form or forms - mistakes or something else?
        # Print problems to the terminal.
        # They'll also be shown to the user.
        else:
            print user_form.errors, profile_form.errors

    # Not a HTTP POST, so we render our form using two ModelForm instances.
    # These forms will be blank, ready for user input.
    else:
        user_form = UserForm()
        profile_form = UserProfileForm()

    # Render the template depending on the context.
    return render( request,
            'rango/register.html', 
            { 'user_form': user_form, 'profile_form': profile_form, 'registered': registered } )

def user_login( request ):
    # If the request is a HTTP POST, try to pull out the relevant information.
    if request.method == 'POST':
        # Gather the username and password provided by the user.
        # This information is obtained from the login form.
        username = request.POST['username']
        password = request.POST['password']

        # Use Django's machinery to attempt to see if the username/password
        # is valid - a User object is returned if it is.
        user = authenticate( username=username, password=password )

        # If we have a User object, the details are correct.
        # If None, no user with matching credentials was found.
        if user:
            # Is the account active? It could have been disabled.
            if user.is_active:
                # If the account is valid and active, we can log the user in.
                # We'll send the user back to the homepage.
                login( request, user )
                return HttpResponseRedirect( '/rango/' )
            else:
                # An inactive account was used - no logging in!
                return HttpResponse("Your Rango account is disabled.")
        else:
            # Bad login details were provided. We can't log the user in.
            print "Invalid login details: %s, %s" % ( username, password )
            return HttpResponse("Invalid login details supplied.")
    
    # The request is not a HTTP POST, so display the login form.
    # This scenario would most likely be a HTTP GET.
    else:
        # No context variables to pass to the template system, hence the
        # blank dictionary object.
        return render( request, 'rango/login.html', {} )

def about( request ):
	return render( request, 'rango/about.html', {} ) 
