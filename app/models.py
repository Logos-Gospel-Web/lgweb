from django.db import models
from django.utils import timezone
import ulid
from app.services.convert_search_text import convert_search_text

# Create your models here.

LANGUAGES = (
    ('tc', '繁體'),
    ('sc', '简体'),
)

_TO_LOCALE = {
    'tc': 'zh_TW',
    'sc': 'zh_CN',
}

_FROM_LOCALE = {
    'zh_TW': 'tc',
    'zh-tw': 'tc',
    'zh_CN': 'sc',
    'zh-cn': 'sc',
}

_TO_LANG_TAG = {
    'tc': 'zh-hant',
    'sc': 'zh-hans',
}

def to_locale(lang: str) -> str:
    return _TO_LOCALE[lang]

def to_lang_tag(lang: str) -> str:
    return _TO_LANG_TAG[lang]

def to_lang(locale: str) -> str:
    return _FROM_LOCALE[locale]

def make_id():
    return ulid.new().str

def make_id_field():
    return models.CharField(max_length=26, primary_key=True, default=make_id, editable=False)

def with_lang(field: str, lang: str):
    return f'{field}_{lang}'

def print_multilingual(self, field: str):
    return ' / '.join((getattr(self, with_lang(field, lang)) or f'<empty>' for (lang, _) in LANGUAGES))

def model(*, multilingual: list[str] = [], base: type[models.Model] = models.Model):
    def make_multilingual(Cls, field):
        def getter(self):
            return { lang: getattr(self, with_lang(field, lang)) for (lang, _) in LANGUAGES }

        definition = getattr(Cls, field)
        if not callable(definition):
            raise Exception('multilingual field must be callable')
        for (lang, _) in LANGUAGES:
            name = with_lang(field, lang)
            setattr(Cls, name, definition(lang))
        setattr(Cls, field, property(getter))

    def decorator(Cls):
        for field in multilingual:
            make_multilingual(Cls, field)
        dt = dict(Cls.__dict__)
        dt.pop('__dict__')
        Copied = type(Cls.__name__, (base,), dt)
        return Copied

    return decorator

def WithPageManager(page_field):
    class Manager(models.Manager):
        def with_page_url(self):
            return self\
                .select_related(f'{page_field}__message__parent')\
                .select_related(f'{page_field}__topic')\

    return Manager()

@model()
class HomePage:
    class Meta:
        db_table = 'home_page'
    language = models.TextField(primary_key=True, choices=LANGUAGES)

    def __str__(self):
        return next(name for lang, name in LANGUAGES if lang == self.language)

@model()
class Banner:
    class Meta:
        db_table = 'banner'

    id = make_id_field()
    title = models.TextField()
    image = models.ImageField(upload_to='banner/image/')
    # break points when screen width smaller than the specified number
    image_480 = models.ImageField(upload_to='banner/image/', blank=True)
    image_720 = models.ImageField(upload_to='banner/image/', blank=True)
    hide_title = models.BooleanField('Hide Title', default=False)
    font = models.FileField(upload_to='banner/font/', blank=True)
    subfont = models.FileField(upload_to='banner/subfont/', blank=True)
    font_size = models.IntegerField(default=28)
    letter_spacing = models.IntegerField(default=30)
    font_weight = models.IntegerField(default=700, choices=[(400, 'Normal'), (700, 'Bold')])
    font_color = models.CharField(max_length=7, default='#ffffff')
    shadow_x = models.IntegerField(default=10)
    shadow_y = models.IntegerField(default=10)
    shadow_blur = models.IntegerField(default=20)
    shadow_color = models.CharField(max_length=7, default='#000000')
    offset_x = models.IntegerField(default=0)
    offset_y = models.IntegerField(default=0)

    def __str__(self):
        return self.title

@model()
class HomeBanner:
    objects = WithPageManager('target_page')
    class Meta:
        db_table = 'home_banner'
        ordering = ['position']

    id = make_id_field()
    language = models.ForeignKey('HomePage', on_delete=models.CASCADE)
    position = models.PositiveSmallIntegerField()
    banner = models.ForeignKey('Banner', on_delete=models.CASCADE)
    target_page = models.ForeignKey('Page', blank=True, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f'Home Banner {self.position + 1}'

@model()
class Promotion:
    objects = WithPageManager('page')
    class Meta:
        db_table = 'promotion'
        ordering = ['position']
    id = make_id_field()
    position = models.PositiveSmallIntegerField()
    language = models.ForeignKey('HomePage', on_delete=models.CASCADE)
    image = models.ImageField('Image', upload_to='promotion/image/')
    alt = models.TextField('Image Hint', blank=True)
    title = models.TextField('Title')
    description = models.TextField('Description')
    page = models.ForeignKey('Page', on_delete=models.CASCADE)

    def __str__(self):
        return self.title

@model(multilingual=['title'])
class MenuItem:
    objects = WithPageManager('page')
    class Meta:
        db_table = 'menu_item'
        ordering = ['position']
    id = make_id_field()
    position = models.PositiveSmallIntegerField()
    enabled = models.BooleanField('Enabled', default=True)
    page = models.ForeignKey('Page', blank=True, null=True, on_delete=models.SET_NULL)
    title = lambda _: models.TextField('Title')

    def __str__(self):
        return print_multilingual(self, 'title')

@model(base=MenuItem)
class ParentMenuItem:
    class Meta:
        verbose_name = 'Menu Item'
        db_table = 'parent_menu_item'
        ordering = ['position']
    pass

@model(base=MenuItem)
class ChildMenuItem:
    class Meta:
        verbose_name = 'Submenu Item'
        db_table = 'child_menu_item'
        ordering = ['position']
    parent = models.ForeignKey('ParentMenuItem', on_delete=models.CASCADE, related_name='children')

@model(multilingual=['title', 'author', 'banner'])
class Page:
    class Meta:
        db_table = 'page'
    id = make_id_field()
    type = models.TextField('Type', choices=[(x, x.title()) for x in ('message', 'topic')])
    enabled = models.BooleanField('Enabled', default=True)
    publish = models.DateField('Publish at', blank=True, null=True)
    title = lambda _: models.TextField('Title', blank=True)
    author = lambda _: models.TextField('Author', blank=True)
    banner = lambda lang: models.ForeignKey('Banner', verbose_name='Banner', related_name=f'page_{lang}_set', blank=True, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f'({self.type.title()}) {print_multilingual(self, "title")}'

@model(multilingual=['prefix', 'document', 'audio', 'preview', 'content', 'search'], base=Page)
class Message:
    class Meta:
        db_table = 'message'
        ordering = ['parent', 'position']
    position = models.PositiveSmallIntegerField()
    parent = models.ForeignKey('Topic', on_delete=models.CASCADE, related_name='children')
    prefix = lambda _: models.TextField('Prefix', blank=True)
    document = lambda _: models.FileField('Document', upload_to='message/document/', blank=True)
    audio = lambda _: models.FileField('Audio', upload_to='message/audio/', blank=True)
    preview = lambda _: models.TextField('Preview', blank=True)
    content = lambda _: models.TextField('Content', blank=True)
    search = lambda _: models.TextField(blank=True)

    def __str__(self):
        return print_multilingual(self, 'title')

    def full_title(self, lang):
        prefix = self.prefix[lang]
        title = ' ' + self.title[lang]
        if prefix:
            return prefix + title
        else:
            return str(self.position + 1).zfill(2) + title

    def is_new(self, now):
        return self.publish is not None and now.year == self.publish.year and now.month == self.publish.month

    def save(self, *args, **kwargs):
        self.search_tc = convert_search_text(self.title_tc, self.content_tc)
        self.search_sc = convert_search_text(self.title_sc, self.content_sc)
        super(Message, self).save(*args, **kwargs)

@model(multilingual=['end_msg', 'description'], base=Page)
class Topic:
    class Meta:
        db_table = 'topic'
    is_blog = models.BooleanField('Blog layout')
    slug = models.SlugField('Slug')
    end_msg = lambda _: models.TextField('"End" message', blank=True)
    description = lambda _: models.TextField('Description', blank=True)

    def __str__(self):
        return print_multilingual(self, 'title')

@model()
class Contact:
    class Meta:
        db_table = 'contact'
    id = make_id_field()
    submitted_at = models.DateTimeField(auto_now_add=True)
    ip = models.CharField('IP', max_length=45)
    fingerprint = models.CharField(max_length=64)
    language = models.TextField(choices=LANGUAGES)
    name = models.TextField()
    email = models.EmailField()
    comment = models.TextField()

    def __str__(self):
        return f'{self.name} ({timezone.localtime(self.submitted_at).strftime(r"%Y-%m-%d %H:%M:%S")})'

@model()
class AnalyticsTemp:
    class Meta:
        db_table = 'analytics_temp'
    id = make_id_field()
    created_at = models.DateTimeField(auto_now_add=True)
    ip = models.CharField('IP', max_length=45)
    fingerprint = models.CharField(max_length=64)
    language = models.TextField(choices=LANGUAGES)
    url = models.TextField()
    user_agent = models.TextField()
    referrer = models.TextField()

    def __str__(self):
        return f'{self.ip} ({self.created_at.strftime(r"%Y-%m-%d %H:%M:%S")})'

@model()
class Analytics:
    class Meta:
        db_table = 'analytics'
        indexes = [
            models.Index(fields=['isbot', 'created_at'], name='analytics_query_idx'),
        ]
    id = make_id_field()
    created_at = models.DateTimeField()
    ip = models.CharField('IP', max_length=45)
    fingerprint = models.CharField(max_length=64)
    language = models.TextField(choices=LANGUAGES)
    url = models.TextField()
    user_agent = models.TextField()
    referrer = models.TextField()
    isbot = models.BooleanField(null=True, default=None)
    country = models.TextField(blank=True)

    def __str__(self):
        return f'{self.ip} ({self.created_at.strftime(r"%Y-%m-%d %H:%M:%S")})'
