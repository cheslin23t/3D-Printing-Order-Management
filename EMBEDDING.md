# Portfolio embed

The ches.dev portfolio loads this published project's `index.html?embed=1` directly. There is no second storefront implementation in the portfolio.

The query parameter skips the initial archive dialog, hides admin navigation, disables the particle loop, and keeps the original customer form inside the iframe. `static/portfolio-embed.css` handles narrow frame sizing. The standalone page retains its original presentation and opening dialog. Bootstrap 5.3.3 is hosted locally to keep form behavior independent of the CDN.

This deployment is a static archive. Submitting the original form displays inline status and does not send an order or payment. The Python/Flask and MySQL implementation remains in the source tree.
