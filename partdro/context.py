def register_context(app):
    @app.context_processor
    def inject_vars():
        return {"site_name": "PartDro"}

