# templates.py

def render_template(template_name, context={}):
    with open(f"templates/{template_name}", "r") as file:
        template = file.read()

    for key, value in context.items():
        if isinstance(value, list) or isinstance(value, tuple):
            value_str = ', '.join(map(str, value))  # Liste veya tuple varsa bir dizeye dönüştür
        else:
            value_str = str(value)  # Liste veya tuple değilse doğrudan kullan
        template = template.replace("{{" + key + "}}", value_str)

    return template
