# Favicon, robots.txt, and sitemap.xml

Repository: https://github.com/glitter-node/data-toolkit

Project root: the directory containing the checked-out Data Toolkit source.

Static assets live in `app/static/`: `favicon.ico`, `favicon-192.png`, `apple-touch-icon.png`, `robots.txt`, and `sitemap.xml`.

The FastAPI application exposes `/favicon.ico`, `/robots.txt`, and `/sitemap.xml` at the domain root. HTML includes favicon links, a canonical URL, and a short description. The sitemap intentionally lists only the public landing page. API endpoints and generated outputs are not listed. `robots.txt` excludes API and documentation endpoints from cooperative crawler discovery; it is not an access control mechanism. The public URL is a deployment target, not a guarantee of availability or indexing.

Verify after deployment:

```bash
curl -I https://data-toolkit.glitter.kr/favicon.ico
curl -I https://data-toolkit.glitter.kr/robots.txt
curl -I https://data-toolkit.glitter.kr/sitemap.xml
```

Note: Some servers may handle HEAD separately; if needed, verify with `curl -i` GET instead. Confirm that reverse-proxy rules do not intercept these paths. Search engines may choose not to index the page.
