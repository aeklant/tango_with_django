from django.shortcuts import render
from django.http import HttpResponse
from rango.models import Category, Page
from rango.forms import CategoryForm, PageForm

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

def about( request ):
	return render( request, 'rango/about.html', {} ) 
