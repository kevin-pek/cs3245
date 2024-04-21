component_weights = {
    'title': 0.3,
    'content': 0.5,
    'citation': 0.1,
    'date': 0.05,
    'court': 0.05
}

def calculate_score(scores, component_weights= component_weights):
    total_score = 0
    for component, weight in component_weights.items():
        total_score += scores.get(component, 0) * weight
    return total_score

