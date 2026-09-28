# Figures: pull images out of a PDF

Give a PDF (a local file, a URL, or a paper id to resolve), and extract its embedded raster images.

Open the PDF (e.g. PyMuPDF/`fitz`), walk pages, and for each image on a page save it. Save as JPG for compactness — but convert first: **JPEG cannot hold alpha or CMYK**, so any pixmap with alpha or 4+ channels must be converted to RGB, and a pixmap with no colorspace is a mask/stencil and should be skipped. Name files by page and index (`page-003-figure-01.jpg`).

## The honest limitation

This extracts **embedded raster images only**. Vector figures, and figures composed of many drawn elements, will be missed or come out as fragments. For real understanding, download the whole PDF (`fulltext.md`) and view it — the figures in context, the captions, and the text around them are what carry the meaning. Use this task for quick thumbnails, not for evidence.
