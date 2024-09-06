from django.contrib import admin
from .models import Author, Category, Book, Comment, LendingTransaction


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    fields = ('first_name', 'last_name', 'brith_date', 'biography', 'nationality', 'website')
    search_fields = ('first_name', 'last_name', 'nationality')

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    fields = ('name',)

class CommentAdmin(admin.StackedInline):
    model = Comment
    fields = ('user', 'content', 'rating', 'created_at')

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    fields = ('title', 'author', 'category', 'published_date', 'isbn', 'num_exist')
    search_fields = ('title', 'author', 'category')
    inlines = [CommentAdmin]


@admin.register(LendingTransaction)
class LendingTransactionAdmin(admin.ModelAdmin):
    fields = ('book', 'borrower', 'borrowed_at','returned_at','status',)
    search_fields = ('book', 'borrower')