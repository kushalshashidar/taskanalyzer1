from django.test import TestCase
from datetime import date, timedelta
from .scoring import calculate_priority_score

class ScoringAlgorithmTests(TestCase):
    def setUp(self):
        self.today = date.today()
        
    def test_standard_task_scoring(self):
        """Test a standard task due in the future"""
        task = {
            'title': 'Test Task',
            'due_date': self.today + timedelta(days=5),
            'estimated_hours': 2,
            'importance': 5
        }
        score, explanation = calculate_priority_score(task)
        # Urgency: 100 - (5*2) = 90 * 0.4 = 36
        # Importance: 50 * 0.3 = 15
        # Effort: (100/2) = 50 * 0.1 = 5
        # Deps: 0
        # Total: 56
        self.assertEqual(score, 56.0)
        
    def test_overdue_task_scoring(self):
        """Test that overdue tasks get a higher score"""
        task = {
            'title': 'Overdue Task',
            'due_date': self.today - timedelta(days=2),
            'estimated_hours': 2,
            'importance': 5
        }
        score, explanation = calculate_priority_score(task)
        # Urgency: 100 + (2*5) = 110 * 0.4 = 44
        # Total should be higher than standard task (56)
        self.assertTrue(score > 56.0)
        self.assertIn("Overdue by 2 days", explanation)

    def test_high_importance_strategy(self):
        """Test that 'important' strategy boosts importance weight"""
        task = {
            'title': 'Important Task',
            'due_date': self.today + timedelta(days=5),
            'estimated_hours': 2,
            'importance': 10
        }
        
        # Smart Strategy (Default)
        # Imp: 100 * 0.3 = 30
        score_smart, _ = calculate_priority_score(task, strategy='smart')
        
        # Important Strategy
        # Imp: 100 * 0.7 = 70
        score_important, _ = calculate_priority_score(task, strategy='important')
        
        self.assertTrue(score_important > score_smart)

    def test_dependency_boost(self):
        """Test that having dependencies increases score"""
        task = {
            'title': 'Blocker Task',
            'due_date': self.today + timedelta(days=5),
            'estimated_hours': 2,
            'importance': 5
        }
        score_no_deps, _ = calculate_priority_score(task, dependency_count=0)
        score_with_deps, _ = calculate_priority_score(task, dependency_count=3)
        
        self.assertTrue(score_with_deps > score_no_deps)
