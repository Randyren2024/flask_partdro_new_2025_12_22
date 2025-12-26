
def generate_lp_html(product_name, hero_media, features):
    """
    Generates a full HTML string for a landing page.
    In a real scenario, this could use AI (like Gemini/DeepSeek) or a Jinja2 template.
    For now, we'll use a high-quality template string.
    """
    
    feature_items_html = ""
    for feat in features:
        icon = feat.get('icon') or 'fas fa-check-circle'
        title = feat.get('title') or 'Feature'
        desc = feat.get('desc') or 'Description'
        feature_items_html += f"""
            <div class="col-md-4 text-center mb-5">
                <div class="mb-4">
                    <i class="{icon} fa-3x text-primary"></i>
                </div>
                <h4 class="text-white font-orbitron">{title}</h4>
                <p class="text-muted">{desc}</p>
            </div>
        """

    media_tag = ""
    if hero_media.endswith(('.mp4', '.webm', '.ogg')):
        media_tag = f'<video class="hero-video" autoplay muted loop playsinline><source src="{hero_media}" type="video/mp4"></video>'
    else:
        media_tag = f'<img class="hero-video" src="{hero_media}" style="object-fit: cover;">'

    html = f"""{{% extends "base.html" %}}

{{% block title %}}{product_name} - Partdro{{% endblock %}}

{{% block extra_css %}}
<style>
    :root {{
        --lp-primary: #00f2ff;
        --lp-bg: #050505;
    }}

    .hero-wrapper {{
        position: relative;
        height: 80vh;
        width: 100%;
        overflow: hidden;
        display: flex;
        align-items: center;
        justify-content: center;
        background: #000;
    }}

    .hero-video {{
        position: absolute;
        top: 0; left: 0; width: 100%; height: 100%;
        object-fit: cover;
        z-index: 0;
        opacity: 0.5;
    }}

    .hero-overlay {{
        position: absolute;
        top: 0; left: 0; width: 100%; height: 100%;
        background: linear-gradient(to bottom, rgba(0,0,0,0.2), rgba(0,0,0,0.8));
        z-index: 1;
    }}

    .hero-content {{
        position: relative;
        z-index: 2;
        text-align: center;
        max-width: 800px;
    }}

    .glitch-title {{
        font-family: 'Orbitron', sans-serif;
        font-size: 4rem;
        font-weight: 900;
        color: #fff;
        text-transform: uppercase;
        text-shadow: 2px 2px var(--lp-primary);
    }}

    .section-title {{
        font-family: 'Orbitron', sans-serif;
        color: #fff;
        text-align: center;
        margin-bottom: 50px;
        text-transform: uppercase;
        letter-spacing: 2px;
    }}
</style>
{{% endblock %}}

{{% block content %}}
<div class="hero-wrapper">
    {media_tag}
    <div class="hero-overlay"></div>
    <div class="hero-content">
        <h1 class="glitch-title">{product_name}</h1>
        <div class="mt-5">
            <a href="#contact" class="btn btn-primary btn-lg px-5 py-3 font-orbitron">GET STARTED</a>
        </div>
    </div>
</div>

<section class="py-5 bg-black">
    <div class="container py-5">
        <h2 class="section-title">Core Features</h2>
        <div class="row">
            {feature_items_html}
        </div>
    </div>
</section>

<section id="contact" class="py-5 bg-dark">
    <div class="container py-5 text-center">
        <h2 class="section-title">Inquiry</h2>
        <p class="text-muted mb-5">Contact us to learn more about {product_name}.</p>
        <a href="mailto:sales@partdro.com" class="btn btn-outline-primary btn-lg px-5 py-3">CONTACT US</a>
    </div>
</section>
{{% endblock %}}
"""
    return html
