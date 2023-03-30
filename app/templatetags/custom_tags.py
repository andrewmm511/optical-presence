from django import template

register = template.Library()

@register.inclusion_tag('common/components/progress_indicator.html')
def progress_indicator(active_step, clickable_steps):
    steps = [
        {"title": "Register Members", "tooltip": "Register household members with their names.", "tooltip_message": "Please complete the current step first.", "url": "/register_people"},
        {"title": "Upload Images", "tooltip": "Upload multiple images of each member for better recognition.", "tooltip_message": "Please complete the current step first.", "url": "/upload"},
        {"title": "Train Model", "tooltip": "Train the facial recognition model using the uploaded images.", "tooltip_message": "Please complete the current step first.", "url": "/train"},
        {"title": "Complete Setup", "tooltip": "Complete the setup process and start using Optical Presence.", "tooltip_message": "Please complete the current step first.", "url": "/complete"},
    ]

    for i, step in enumerate(steps):
        step['clickable'] = i + 1 in clickable_steps

    return {'steps': steps, 'active_step': active_step}