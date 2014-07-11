from django.db import models
from django.contrib.auth.models import User
from datetime import datetime
from django.utils.timezone import utc

# Create your models here.
# heroku pg:reset postgres
# heroku run python manage.py syncdb

class TheDeed(models.Model):
	start = models.DateTimeField(auto_now_add=True)
	stop = models.DateTimeField(blank=True, null=True)
	user = models.ForeignKey(User)
	bathroom = models.ForeignKey('Bathroom')

	def __str__(self):
		return "Deed at %s by %s in %s" % (self.start, self.user, self.bathroom)


class Bathroom(models.Model):
	name = models.CharField(max_length=200)
	description = models.TextField(blank=True, null=True)
	stalls = models.IntegerField(blank=True, null=True)
	lat = models.FloatField('Latitude', blank=True, null=True)
	lon = models.FloatField('Longitude', blank=True, null=True)
	createdBy = models.ForeignKey(User)

	def __str__(self):
		return "Bathroom: %s by %s" % (self.name, self.createdBy)

	def is_occupied(self):
		return len(self.thedeed_set.filter(stop__isnull=True)) > 0

	def current_deed(self):
		if (self.is_occupied()):
			return self.thedeed_set.filter(stop__isnull=True)[0]
		return None

	def current_deed_start(self):
		deed = self.current_deed()
		if deed:
			return deed.start
		return None

	def who_is_bogging_you_down(self):
		deed = self.current_deed()
		if (deed):
			return deed.user
		return None

	def lock(self, user):
		if self.is_occupied():
			if user == self.who_is_bogging_you_down():
				return True
			else:
				raise Unauthorized("%s has already locked it" % self.who_is_bogging_you_down().username)
		
		TheDeed(user=user, bathroom=self).save()
		return True

	def unlock(self, user):
		if not self.is_occupied():
			return True
		if user != self.who_is_bogging_you_down():
			raise Unauthorized("You can't unlock it. It was locked by %s at %s" % 
				(self.who_is_bogging_you_down, self.current_deed().start))

		deed = self.current_deed()
		if not deed:
			return True
		deed.stop = datetime.utcnow().replace(tzinfo=utc)
		deed.save()
		return True


class Unauthorized(Exception):
    pass