from os import environ
import json
from django import forms
from django.contrib import admin
from django.forms.utils import flatatt
from django.forms.widgets import Input, TextInput, HiddenInput
from django.templatetags.static import static
from django.utils.html import format_html, html_safe
from django.utils.safestring import mark_safe
from .models import LANGUAGES, with_lang, Banner, HomePage, HomeBanner, Promotion, Message, Topic, ChildMenuItem, ParentMenuItem, Contact

def make_multilingual_fields(*fields: str, collapsed: bool = False):
    return tuple(((name, {
        'classes': ('grp-collapse', 'grp-closed' if collapsed else 'grp-open'),
        'fields': tuple((with_lang(field, lang) for field in fields)),
    }) for (lang, name) in LANGUAGES))

class RichTextInput(Input):
    input_type = 'text'
    template_name = 'forms/widgets/richtext.html'
    class Media:
        css = {
            'all': (
                'admin/richtext/tinymce/skins/ui/oxide/skin.min.css',
            )
        }
        js = (
            'https://cdn.jsdelivr.net/npm/js-base64@3.7.5/base64.min.js',
            'admin/richtext/tinymce/tinymce.min.js',
            'admin/richtext/richtext.js',
        )

class JS:
    def __init__(self, js, attrs=None):
        self.js = js
        self.attrs = attrs or {}

    def startswith(self, _):
        return True

    def __repr__(self):
        return f"JS({self.js}, {json.dumps(self.attrs, sort_keys=True)})"

    def __str__(self):
        return format_html(
            '<script src="{}"{}></script>',
            self.js
                if self.js.startswith(("http://", "https://", "/"))
                else static(self.js),
            mark_safe(flatatt(self.attrs)),
        )

    def __eq__(self, other):
        if isinstance(other, JS):
            return self.js == other.js and self.attrs == other.attrs
        return self.js == other and not self.attrs

    def __hash__(self):
        return hash((self.js, json.dumps(self.attrs, sort_keys=True)))


JS = html_safe(JS)

class DropboxInput(Input):
    input_type = 'url'
    template_name = 'forms/widgets/dropbox.html'
    class Media:
        css = {
            'all': (
                'admin/dropbox/dropbox.css',
            )
        }
        js = (
            JS('https://www.dropbox.com/static/api/2/dropins.js', { 'id': 'dropboxjs', 'data-app-key': environ.get('DROPBOX_APP_KEY', '')}),
            'admin/dropbox/dropbox.js',
        )

class ColorInput(TextInput):
    input_type = 'color'

class BannerForm(forms.ModelForm):
    class Meta:
        model = Banner
        exclude = ['subfont']
        widgets = {
            'title': TextInput(),
            'font_color': ColorInput(),
            'shadow_color': ColorInput(),
        }

@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    form = BannerForm

class MessageForm(forms.ModelForm):
    class Meta:
        exclude = []
        model = Message
        widgets = {
            'type': HiddenInput(attrs={'value': 'message'}),
            'title_tc': TextInput(),
            'title_sc': TextInput(),
            'author_tc': TextInput(),
            'author_sc': TextInput(),
            'prefix_tc': TextInput(),
            'prefix_sc': TextInput(),
            'audio_tc': DropboxInput(),
            'audio_sc': DropboxInput(),
            'preview_tc': RichTextInput(),
            'preview_sc': RichTextInput(),
            'content_tc': RichTextInput(),
            'content_sc': RichTextInput(),
        }

class MessageInline(admin.StackedInline):
    model = Message
    sortable_field_name = 'position'
    fk_name = 'parent'
    extra = 0
    form = MessageForm
    fieldsets = (
        (None, {
            'fields': ('type', 'position', 'enabled', 'publish'),
        }),
    ) + make_multilingual_fields(
        'title', 'author', 'banner', 'prefix',
        'document', 'audio', 'content', 'preview',
        collapsed=True
    )

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.name == self.sortable_field_name:
            kwargs["widget"] = HiddenInput()
        return super(MessageInline, self).formfield_for_dbfield(db_field, request, **kwargs)

class TopicForm(forms.ModelForm):
    class Meta:
        exclude = []
        model = Topic
        widgets = {
            'type': HiddenInput(attrs={'value': 'topic'}),
            'title_tc': TextInput(),
            'title_sc': TextInput(),
            'author_tc': TextInput(),
            'author_sc': TextInput(),
            'end_msg_tc': TextInput(),
            'end_msg_sc': TextInput(),
            'description_tc': RichTextInput(),
            'description_sc': RichTextInput(),
        }

@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    form = TopicForm
    inlines = [MessageInline]
    fieldsets = (
        (None, {
            'fields': ('type', 'enabled', 'publish', 'is_blog', 'slug'),
        }),
    ) + make_multilingual_fields(
        'banner', 'title', 'author', 'end_msg', 'description',
        collapsed=True,
    )

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    form = MessageForm
    fieldsets = (
        (None, {
            'fields': ('type', 'parent', 'position', 'enabled', 'publish'),
        }),
    ) + make_multilingual_fields(
        'title', 'author', 'banner', 'prefix',
        'document', 'audio', 'content', 'preview',
    )

class ChildMenuItemForm(forms.ModelForm):
    class Meta:
        exclude = []
        model = ChildMenuItem
        widgets = {
            'position': HiddenInput(),
            'title_tc': TextInput(),
            'title_sc': TextInput(),
        }

class ChildMenuItemInline(admin.StackedInline):
    model = ChildMenuItem
    sortable_field_name = 'position'
    fk_name = 'parent'
    extra = 0
    form = ChildMenuItemForm
    fieldsets = (
        (None, {
            'fields': ('position', 'enabled', 'page'),
        }),
    ) + make_multilingual_fields('title')

class ParentMenuItemForm(forms.ModelForm):
    class Meta:
        exclude = []
        model = ParentMenuItem
        widgets = {
            'title_tc': TextInput(),
            'title_sc': TextInput(),
        }

@admin.register(ParentMenuItem)
class ParentMenuItemAdmin(admin.ModelAdmin):
    form = ParentMenuItemForm
    inlines = [ChildMenuItemInline]
    fieldsets = (
        (None, {
            'fields': ('position', 'enabled', 'page'),
        }),
    ) + make_multilingual_fields('title')

class HomeBannerForm(forms.ModelForm):
    class Meta:
        exclude = []
        model = HomeBanner
        widgets = {
            'position': HiddenInput(),
        }

class HomeBannerInline(admin.StackedInline):
    model = HomeBanner
    sortable_field_name = 'position'
    fk_name = 'language'
    extra = 0
    form = HomeBannerForm
    fieldsets = (
        (None, {
            'fields': ('position', 'banner', 'target_page'),
        }),
    )

class PromotionForm(forms.ModelForm):
    class Meta:
        exclude = []
        model = Promotion
        widgets = {
            'position': HiddenInput(),
            'alt': TextInput(),
            'title': TextInput(),
        }

class PromotionInline(admin.StackedInline):
    model = Promotion
    sortable_field_name = 'position'
    fk_name = 'language'
    extra = 0
    form = PromotionForm
    fieldsets = (
        (None, {
            'fields': ('position', 'title', 'description', 'image', 'alt', 'page'),
        }),
    )

@admin.register(HomePage)
class HomePageAdmin(admin.ModelAdmin):
    inlines = [HomeBannerInline, PromotionInline]
    exclude = ['language']

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    fields = ['name', 'email', 'comment', 'submitted_at', 'language', 'ip', 'fingerprint']
    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
