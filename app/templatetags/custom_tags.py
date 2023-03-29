from django import template

register = template.Library()

@register.inclusion_tag('common/components/progress_indicator.html')
def progress_indicator(active_step):
    steps = [
        {"title": "Register Members", "tooltip": "Register household members with their names.", "tooltip_message": "Please complete the current step first."},
        {"title": "Upload Images", "tooltip": "Upload multiple images of each member for better recognition.", "tooltip_message": "Please complete the current step first."},
        {"title": "Train Model", "tooltip": "Train the facial recognition model using the uploaded images.", "tooltip_message": "Please complete the current step first."},
        {"title": "Complete Setup", "tooltip": "Complete the setup process and start using Optical Presence.", "tooltip_message": "Please complete the current step first."},
    ]

    return {'steps': steps, 'active_step': active_step}