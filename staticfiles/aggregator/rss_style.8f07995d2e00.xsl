<xsl:stylesheet version="3.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns:atom="http://www.w3.org/2005/Atom"
                xmlns:dc="http://purl.org/dc/elements/1.1/"
                xmlns:itunes="http://www.itunes.com/dtds/podcast-1.0.dtd">
  <xsl:output method="html" version="1.0" encoding="UTF-8" indent="yes"/>
  <xsl:template match="/">
    <html xmlns="http://www.w3.org/1999/xhtml" lang="en">
      <head>
        <title><xsl:value-of select="/rss/channel/title"/> - Web Feed</title>
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>
        <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1"/>
        <link rel="preconnect" href="https://fonts.googleapis.com"/>
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin="anonymous"/>
        <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&amp;display=swap" rel="stylesheet"/>
        <link rel="stylesheet" type="text/css" href="/static/aggregator/rss.css?v=2"/>
      </head>
      <body>
        <div class="container">
            <header class="fade-in">
                <div class="header-content">
                    <h1><xsl:value-of select="/rss/channel/title"/></h1>
                    <p class="desc"><xsl:value-of select="/rss/channel/description"/></p>
                    
                    <div class="controls">
                        <div class="rss-box">
                            <span class="rss-icon">
                                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 11a9 9 0 0 1 9 9"></path><path d="M4 4a16 16 0 0 1 16 16"></path><circle cx="5" cy="19" r="1"></circle></svg>
                            </span>
                            <div class="rss-link" id="rssUrl">
                                <xsl:value-of select="/rss/channel/link"/>
                            </div>
                            <button class="copy-btn" onclick="copyUrl()" aria-label="Copy RSS URL">
                                <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>
                                <span>Copy</span>
                            </button>
                        </div>
                        <div class="search-box">
                            <svg class="search-icon" xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>
                            <input type="text" id="searchInput" placeholder="Search articles..." onkeyup="filterItems()"/>
                        </div>
                    </div>
                </div>
            </header>
            
            <main id="feedGrid">
                <xsl:for-each select="/rss/channel/item">
                    <article class="item fade-in-up">
                        <div class="item-content">
                            <div class="meta">
                                <span class="date"><xsl:value-of select="pubDate"/></span>
                                <xsl:if test="dc:creator">
                                     <span class="author">by <xsl:value-of select="dc:creator"/></span>
                                </xsl:if>
                            </div>
                            
                            <h2>
                                <a href="{link}" target="_blank">
                                    <xsl:value-of select="title"/>
                                </a>
                            </h2>
                            
                            <div class="desc">
                                <!-- Show image if available via enclosure -->
                                <xsl:if test="enclosure">
                                    <img src="{enclosure/@url}" alt="{title}" style="width: 100%; height: 200px; object-fit: cover; border-radius: 0.5rem; margin-bottom: 1rem;"/>
                                </xsl:if>
                                
                                <!-- We trust the content:encoded or description, but for the grid card we might want to limit it purely via CSS or just show it. 
                                     The description usually contains a summary. -->
                                <xsl:choose>
                                    <xsl:when test="description">
                                        <xsl:value-of select="description" disable-output-escaping="yes"/>
                                    </xsl:when>
                                </xsl:choose>
                            </div>
                            
                            <a href="{link}" target="_blank" class="read-more">
                                Read Article 
                                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="5" y1="12" x2="19" y2="12"></line><polyline points="12 5 19 12 12 19"></polyline></svg>
                            </a>
                        </div>
                    </article>
                </xsl:for-each>
            </main>
            
            <footer>
                <p>Generated by Burma News Aggregator</p>
            </footer>
        </div>
        
        <script>
            function copyUrl() {
                const url = window.location.href;
                navigator.clipboard.writeText(url).then(function() {
                    const btn = document.querySelector('.copy-btn');
                    const originalText = btn.innerHTML;
                    btn.innerHTML = '<span>Copied!</span>';
                    btn.classList.add('copied');
                    
                    setTimeout(() => {
                        btn.innerHTML = originalText;
                        btn.classList.remove('copied');
                    }, 2000);
                }, function(err) {
                    console.error('Could not copy text: ', err);
                });
            }
            
            function filterItems() {
                const input = document.getElementById('searchInput');
                const filter = input.value.toLowerCase();
                const grid = document.getElementById('feedGrid');
                const items = grid.getElementsByTagName('article');
                
                for (let i = 0; i < items.length; i++) {
                    const title = items[i].getElementsByTagName('h2')[0];
                    const desc = items[i].querySelector('.desc');
                    const txtValue = (title.textContent || title.innerText) + " " + (desc.textContent || desc.innerText);
                    
                    if (txtValue.toLowerCase().indexOf(filter) > -1) {
                        items[i].style.display = "";
                    } else {
                        items[i].style.display = "none";
                    }
                }
            }
            
            // Set animation delays for items
            document.addEventListener('DOMContentLoaded', () => {
                const items = document.querySelectorAll('.item');
                items.forEach((item, index) => {
                    item.style.animationDelay = (index * 0.05) + 's';
                });
            });
        </script>
      </body>
    </html>
  </xsl:template>
</xsl:stylesheet>
