# PDF.js local runtime

Mozilla PDF.js (`pdfjs-dist` 5.4.624), Apache-2.0. See LICENSE and VERSION.json for upstream source and verified npm archive integrity. Runtime modules, CMaps, standard fonts, WebAssembly decoders, viewer CSS and image resources are distributed locally, so PDF preview needs no third-party network requests.

`viewer.html`, `viewer.css`, and `viewer.mjs` are the site integration. The viewer only loads same-origin PDF URLs. PDF scripting and annotation editing are disabled. Document links, text selection, continuous scrolling, page navigation and zoom are handled by the PDF.js viewer. The outer article keeps direct-open and download links as fallback.
