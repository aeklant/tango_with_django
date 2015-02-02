"""
'views.py' is to serve as the controller for any and all rango actions
requested by the rango html templates.
"""
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from rango.models import Category, Page
from rango.forms import CategoryForm, PageForm
from datetime import datetime

def index(request):
    """
    Fetches the top five most liked categories and top five most viewed pages.
    Sends them to be handled by 'rango/index.html'
    """

    context_dict = {}

	# Query the database for a list of ALL categories currently stored.
	# Order the categories by no. likes in descending order.
	# Retrieve the top 5 only - or all if less than 5.
	# Place the list in our context_dict dictionary which will be passed to
    # the template.
    # pylint: disable=E1103
    category_list = Category.objects.order_by('-likes')[:5]
    context_dict['categories'] = category_list

	# Retrieve top 5 viewed pages from the Page table.
	# Place them in the context dictionary to be used by the template.
    top_pages = Page.objects.order_by('-views')[:5]
    context_dict['top_pages'] = top_pages
    # pylint: enable=E1103

    # Get the number of visits to the site.
    visits = request.session.get('visits')
    if not visits:
        visits = 1
    reset_last_visit_time = False

    last_visit = request.session.get('last_visit')
    if last_visit:
        last_visit_time = datetime.strptime(last_visit[:-7],
                                            "%Y-%m-%d %H:%M:%S")

        # has it been more than a day since the last visit?
        if (datetime.now() - last_visit_time).seconds > 10:
            visits += 1
            reset_last_visit_time = True
    else:
        # Cookie 'last_visit' doesn't exist, so flag that it should be set.
        reset_last_visit_time = True
        context_dict['visits'] = visits

    if reset_last_visit_time:
        request.session['visits'] = visits
        request.session['last_visit'] = str(datetime.now())

    # Return response back to the user, updating cookies.
    response = render(request, 'rango/index.html', context_dict)
    return response

def category(request, category_name_slug):
    """
    Fetches all of the pages whose category corresponds to 'category_name_slug'
    Sends them to be handled by 'rango/category.html'
    """

	# Create a context dictionary which we can pass to the template rendering page.
    context_dict = {}

    # pylint: disable=E1103
    try:
		# The .get() method returns one model instance or raises an exception.
        cat = Category.objects.get(slug=category_name_slug)
        context_dict['category_name'] = cat.name
        context_dict['category_name_slug'] = cat.slug

		# Retrieve all of the associated pages.
        pages = Page.objects.filter(category=cat)

		# Adds our results list to the template context dictionary.
        context_dict['pages'] = pages
    except Category.DoesNotExist:
		# context_dict will remain empty. We will let the template display a "no category" message
        pass
    # pylint: enable=E1103
    return render(request, 'rango/category.html', context_dict)

@login_required
def add_category(request):
    """
    User must be logged in to use this functionality.
    Adds a new category corresponding to the information in the form filled
    by the user. If form empty, display form. If form filled and valid, create
    a new category. If form filled and not valid, display form errors.
    """

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
			#return HttpResponse(form.errors)
			#return index(request)
            print form.errors
    else:
		# If the request was not a POST, display the form to enter details.
        form = CategoryForm()

	# Bad form (or form details), no form supplied...
	# Render the form with error messages (if any).
    return render(request, 'rango/add_category.html', {'form': form})

@login_required
def add_page(request, category_name_slug):
    """
    User must be logged in to use this functionality.
    Adds a new page corresponding to the information in the form filled
    by the user with 'category_name_slug' as its category.
    If form empty, display form. If form filled and valid, create
    a new page. If form filled and not valid, display form errors.
    """

    # pylint: disable=E1103
    try:
        cat = Category.objects.get(slug=category_name_slug)
    except Category.DoesNotExist:
        cat = None
    # pylint: enable=E1103

    if request.method == 'POST':
        form = PageForm(request.POST)
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

    context_dict = {'form':form, 'category':cat,
                    'category_name_slug':category_name_slug}

    return render(request, 'rango/add_page.html', context_dict)

# Use the login_required decorator to ensure only those logged in can access the view.
@login_required
def restricted(request):
    """
    User must be logged in to use this functionality.
    Renders a restricted page. Does nothing else.
    """

    return render(request, 'rango/restricted.html', {})

def about(request):
    """
    Renders a page with information about the web application.
    """
    context_dict = {}

    visits = request.session.get('visits')
    if not visits:
        visits = 1
    context_dict['visits'] = visits

    return render(request, 'rango/about.html', context_dict)
