<?xml version="1.0" encoding="utf-8"?>
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
        <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;700&amp;display=swap" rel="stylesheet"/>
        <link rel="stylesheet" type="text/css" href="/static/aggregator/rss.css"/>
      </head>
      <body>
        <header>
            <h1><xsl:value-of select="/rss/channel/title"/></h1>
            <p class="desc"><xsl:value-of select="/rss/channel/description"/></p>
            
            <div class="rss-box">
                <div class="rss-link" id="rssUrl">
                    <!-- Current URL will be injected here via JS or just user copies from browser bar -->
                    <xsl:value-of select="/rss/channel/link"/>
                </div>
                <button class="copy-btn" onclick="copyUrl()">Copy URL</button>
            </div>
        </header>
        
        <main>
            <xsl:for-each select="/rss/channel/item">
                <article class="item" style="animation-delay: {position() * 0.1}s">
                    <div class="meta">
                        <xsl:value-of select="pubDate"/>
                    </div>
                    <h2>
                        <a href="{link}" target="_blank">
                            <xsl:value-of select="title"/>
                        </a>
                    </h2>
                    <div class="desc">
                        <xsl:value-of select="description" disable-output-escaping="yes"/>
                    </div>
                </article>
            </xsl:for-each>
        </main>
        
        <script>
            function copyUrl() {
                navigator.clipboard.writeText(window.location.href).then(function() {
                    alert('RSS Feed URL copied to clipboard!');
                }, function(err) {
                    console.error('Could not copy text: ', err);
                });
            }
        </script>
      </body>
    </html>
  </xsl:template>
</xsl:stylesheet>
