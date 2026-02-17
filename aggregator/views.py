from django.shortcuts import render
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.utils.feedgenerator import Rss201rev2Feed, Enclosure
from .models import Post, Source

class ExtendedRSSFeed(Rss201rev2Feed):
    """
    RSS Feed with content:encoded and other standard extensions for better compatibility.
    """
    def root_attributes(self):
        attrs = super().root_attributes()
        attrs['xmlns:content'] = 'http://purl.org/rss/1.0/modules/content/'
        attrs['xmlns:dc'] = 'http://purl.org/dc/elements/1.1/'
        return attrs

    def add_item_elements(self, handler, item):
        super().add_item_elements(handler, item)
        
        # content:encoded
        if item.get('content_encoded'):
            handler.addQuickElement(u'content:encoded', item['content_encoded'])
            
        # dc:creator
        if item.get('author_name'):
            handler.addQuickElement(u'dc:creator', item['author_name'])

def index(request):
    source_id = request.GET.get('source')
    source_type = request.GET.get('type')
    posts_list = Post.objects.all()
    
    if source_id:
        posts_list = posts_list.filter(source__id=source_id)
    
    if source_type:
        posts_list = posts_list.filter(source__source_type=source_type)
        
    paginator = Paginator(posts_list, 20) # Show 20 contacts per page.
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Calculate elided page range for better navigation
    custom_range = paginator.get_elided_page_range(page_obj.number, on_each_side=2, on_ends=1)
    
    sources = Source.objects.filter(is_active=True)
    
    return render(request, 'aggregator/index.html', {
        'page_obj': page_obj,
        'custom_range': custom_range,
        'sources': sources,
        'current_source_type': source_type
    })

def feed_rss(request):
    source_id = request.GET.get('source')
    title = "Burma News Aggregator"
    link = "/feed/rss"
    description = "Latest news from Burma News Aggregator"
    
    posts = Post.objects.all()[:50] # Limit to last 50
    if source_id:
        posts = posts.filter(source__id=source_id)
        
    feed = ExtendedRSSFeed(
        title=title,
        link=link,
        description=description,
        language="my",
    )
    
    for post in posts:
        # Prepare full content for content:encoded
        # We wrap it in CDATA implicitly by addQuickElement usually, but Django handles it.
        # We create a simple HTML string for the full view.
        full_content = f"""
        <p><strong>{post.title}</strong></p>
        <p>{post.translated_content or post.original_content}</p>
        <p><a href="{post.url}">Read original at {post.source.name}</a></p>
        """
        
        if post.image_url:
            # Add image at top of content
            full_content = f'<img src="{post.image_url}" style="max-width:100%;" /><br/>' + full_content

        item_kwargs = {
            'title': post.title,
            'link': post.url,
            'description': post.translated_content or post.original_content,
            'pubdate': post.published_date,
            'unique_id': post.url,
            'author_name': post.source.name,
            'content_encoded': full_content,
        }
        
        # Add enclosure if image exists
        if post.image_url:
             # Heuristic for mime type
             mime = "image/jpeg"
             if ".png" in post.image_url.lower(): mime = "image/png"
             elif ".gif" in post.image_url.lower(): mime = "image/gif"
             
             item_kwargs['enclosure'] = Enclosure(
                 url=post.image_url, 
                 length="0", 
                 mime_type=mime
             )

        feed.add_item(**item_kwargs)
        
    xml_data = feed.writeString('utf-8')
    # Inject XSLT instruction
    xslt_instruction = '<?xml-stylesheet type="text/xsl" href="/static/aggregator/rss_style.xsl"?>\n'
    # Insert after XML declaration
    xml_data = xml_data.replace('<?xml version="1.0" encoding="utf-8"?>', '<?xml version="1.0" encoding="utf-8"?>\n' + xslt_instruction)
    
    return HttpResponse(xml_data, content_type="application/xml")
