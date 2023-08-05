from django.db import models

class Creator(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]

    name = models.CharField(unique=True, max_length=200)
    description = models.TextField(blank=True, null=True)
    birthday = models.DateField(blank=True, null=True)
    image = models.ImageField(upload_to='creators/', blank=True, null=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, default='O')
    created = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Tag(models.Model):
	genre = models.CharField(unique=True, max_length=100)
	created = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	def __str__(self):
		return self.genre

class CreatorOfTheMonth(models.Model):
    creator = models.ForeignKey(Creator, on_delete=models.CASCADE)
    month = models.IntegerField()
    year = models.IntegerField()

    def __str__(self):
        return f"Creator of the Month: {self.creator.name}"
     

class Show(models.Model):
	title = models.CharField(max_length=200)
	count = models.IntegerField()
	script = models.FileField(blank=True, null=True, upload_to="screenplays")
	poster = models.ImageField(blank=True, null=True, upload_to="posters")
	description = models.TextField(blank=True, null=True)
	creators = models.ManyToManyField(Creator, related_name='shows')
	tags = models.ManyToManyField(Tag, related_name='shows')
	favorites = models.ManyToManyField('StaffFavorite', related_name='shows', blank=True)
	created = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	def __str__(self):
		return self.title

class Comment(models.Model):
	name = models.CharField(max_length=100)
	email = models.EmailField(max_length=100)
	message = models.TextField()
	created = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	def __str__(self):
		return self.message
	
class StaffFavorite(models.Model):
    show = models.ForeignKey(Show, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Staff Favorite: {self.show.title}"

class InfluentialShow(models.Model):
    show = models.ForeignKey(Show, on_delete=models.CASCADE)
    month = models.IntegerField()
    year = models.IntegerField()

    def __str__(self):
        return f"Show of the Month: {self.show.title}"

	

#  Models that point to the cassandra db

# Import necessary modules
# from django_cassandra_engine.models import DjangoCassandraModel
# from cassandra.cqlengine import columns

# # Define User model
# class User(DjangoCassandraModel):
#     # User fields
#     username = columns.Text(primary_key=True)
#     password = columns.Text()
#     email = columns.Text()
#     first_name = columns.Text()
#     last_name = columns.Text()
#     date_of_birth = columns.Date()
#     created_at = columns.DateTime()

#     class Meta:
#         using = 'cassandra'  # Specify the database alias for Cassandra
#         get_pk_field = 'username'  # Specify the primary key field


# # Define Watchlist model
# class Watchlist(DjangoCassandraModel):
#     # Watchlist fields
#     user = columns.Text(primary_key=True)
#     movie_ids = columns.List(columns.Text)

# # Define Readlist model
# class Readlist(DjangoCassandraModel):
#     # Readlist fields
#     user = columns.Text(primary_key=True)
#     book_ids = columns.List(columns.Text)

# # Define Activity model
# class Activity(DjangoCassandraModel):
#     # Activity fields
#     user = columns.Text(primary_key=True)
#     watched_movies = columns.Set(columns.Text)
#     watching_movies = columns.Set(columns.Text)
#     read_books = columns.Set(columns.Text)
#     reading_books = columns.Set(columns.Text)

# # Define UserFollowing model
# class UserFollowing(DjangoCassandraModel):
#     # UserFollowing fields
#     follower = columns.Text(primary_key=True)
#     following = columns.Text(primary_key=True)

# # Define UserLikes model
# class UserLikes(DjangoCassandraModel):
#     # UserLikes fields
#     user = columns.Text(primary_key=True)
#     liked_lists = columns.Set(columns.Text)

# # Define ListLikes model
# class ListLikes(DjangoCassandraModel):
#     # ListLikes fields
#     list_id = columns.Text(primary_key=True)
#     liked_by_users = columns.Set(columns.Text)

