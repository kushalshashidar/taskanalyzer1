from datetime import date, datetime

def calculate_priority_score(task_data, dependency_count=0, strategy='smart'):
    """
    Calculate priority score for a task.
    
    Factors:
    1. Urgency: (Due Date - Today)
    2. Importance: 1-10
    3. Effort: Estimated Hours
    4. Dependencies: Number of tasks depending on this one
    
    Strategies:
    - 'smart': Balanced (default)
    - 'urgent': Prioritize deadlines
    - 'important': Prioritize importance
    - 'quick': Prioritize low effort
    """
    
    # Parse due_date if string
    due_date = task_data.get('due_date')
    if isinstance(due_date, str):
        try:
            due_date = datetime.strptime(due_date, '%Y-%m-%d').date()
        except ValueError:
            due_date = date.today()
    
    today = date.today()
    days_until_due = (due_date - today).days
    
    # 1. Urgency Score
    if days_until_due < 0:
        urgency_score = 100 + (abs(days_until_due) * 5)
    elif days_until_due == 0:
        urgency_score = 100
    else:
        urgency_score = max(0, 100 - (days_until_due * 2))
        
    # 2. Importance Score
    importance = task_data.get('importance', 5)
    importance_score = importance * 10
    
    # 3. Effort Score (Quick Wins)
    effort = task_data.get('estimated_hours', 1)
    effort_score = 100 / max(0.5, effort)
    
    # 4. Dependency Score
    dependency_score = dependency_count * 15
    
    # Define Weights based on Strategy
    weights = {
        'smart': {'urgency': 0.4, 'importance': 0.3, 'effort': 0.1, 'deps': 0.2},
        'urgent': {'urgency': 0.7, 'importance': 0.1, 'effort': 0.1, 'deps': 0.1},
        'important': {'urgency': 0.2, 'importance': 0.7, 'effort': 0.05, 'deps': 0.05},
        'quick': {'urgency': 0.2, 'importance': 0.1, 'effort': 0.6, 'deps': 0.1},
    }
    
    w = weights.get(strategy, weights['smart'])
    
    total_score = (
        (urgency_score * w['urgency']) +
        (importance_score * w['importance']) +
        (dependency_score * w['deps']) +
        (effort_score * w['effort'])
    )
    
    explanation = []
    if days_until_due < 0:
        explanation.append(f"Overdue by {abs(days_until_due)} days")
    elif days_until_due <= 2:
        explanation.append("Due very soon")
        
    if importance >= 8:
        explanation.append("High importance")
        
    if effort <= 2:
        explanation.append("Quick win")
        
    if dependency_count > 0:
        explanation.append(f"Blocks {dependency_count} other tasks")
        
    if strategy != 'smart':
        explanation.append(f"Strategy: {strategy.capitalize()}")
        
    return round(total_score, 1), explanation
