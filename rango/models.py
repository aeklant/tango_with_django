from django.db import models
from django.template.defaultfilters import slugify

class Category( models.Model ):
	name = models.CharField(max_length=128, unique=True)
	views = models.IntegerField(default=0)
	likes = models.IntegerField(default=0)
	slug = models.SlugField(unique=True)
	
	def save(self, *args, **kwargs): 
		self.slug = slugify(self.name)

		# Calling super has implications that make it not very safe, it's not like java.		# We will call the parent constructor directly.
		models.Model.save(self, *args, **kwargs)
		
	def __unicode__(self):
		return self.name

class Page( models.Model ):
	category = models.ForeignKey(Category)
	title = models.CharField(max_length=128)
	url = models.URLField()
	views = models.IntegerField(default=0)

	def __unicode__(self):
		return self.title
