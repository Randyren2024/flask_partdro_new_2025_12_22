import os
import re
from flask import render_template, url_for
from partdro import create_app
from partdro.services.db import list_products

def export_pages():
    app = create_app()
    
    # Ensure output directory exists
    output_dir = 'standalone_html'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Context for rendering
    with app.app_context():
        # Mock request context for url_for and get_locale
        with app.test_request_context('/?locale=en'):
            
            # 1. Export Index (Home)
            print("Exporting index.html...")
            try:
                # Fetch products for dynamic sections
                # We fetch a few for each category to populate the page
                infrared = list_products(category="Infrared Drones", page=1, page_size=3)
                cargo = list_products(category="Cargo Drones", page=1, page_size=3)
                spray = list_products(category="Spray Drones", page=1, page_size=3)
                products = infrared + cargo + spray
                
                html = render_template('index.html', products=products, locale='en')
                save_html(html, 'index.html')
            except Exception as e:
                print(f"Error exporting index.html: {e}")

            # 2. Export About Us
            print("Exporting about.html...")
            try:
                html = render_template('about.html')
                save_html(html, 'about.html')
            except Exception as e:
                print(f"Error exporting about.html: {e}")

            # 3. Export Contact Us
            print("Exporting contact.html...")
            try:
                html = render_template('contact.html')
                save_html(html, 'contact.html')
            except Exception as e:
                print(f"Error exporting contact.html: {e}")

def save_html(html_content, filename):
    # Post-process links to make them standalone relative links
    # Replace /about with about.html, etc.
    # Note: This is a simple regex replacement and might not cover all edge cases
    
    # Fix url_for generated links
    html_content = html_content.replace('href="/about"', 'href="about.html"')
    html_content = html_content.replace('href="/contact"', 'href="contact.html"')
    html_content = html_content.replace('href="/terms-and-services"', 'href="terms.html"') # Assuming terms.html exists or will be created
    html_content = html_content.replace('href="/privacy-policy"', 'href="privacy.html"')   # Assuming privacy.html exists
    html_content = html_content.replace('href="/"', 'href="index.html"')
    html_content = html_content.replace('href="/products"', 'href="index.html#products"') # Map products page to index for now or leave as is
    
    # Fix static asset links if necessary (e.g. /static/...)
    # For now, we assume /static/ is accessible or relative. 
    # To make it truly standalone, one might need to copy static assets too.
    # We'll just change /static/ to ./static/ for better local viewing chance
    html_content = html_content.replace('src="/static/', 'src="./static/')
    html_content = html_content.replace('href="/static/', 'href="./static/')
    
    path = os.path.join('standalone_html', filename)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f"Saved {path}")

if __name__ == '__main__':
    export_pages()
