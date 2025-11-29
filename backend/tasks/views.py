from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import TaskInputSerializer, TaskSerializer
from .scoring import calculate_priority_score
from .models import Task

class AnalyzeTasksView(APIView):
    def post(self, request):
        serializer = TaskInputSerializer(data=request.data, many=True)
        if serializer.is_valid():
            tasks_data = serializer.validated_data
            
            # Build Dependency Graph to count how many tasks depend on a specific task
            # Map ID -> Count of tasks that list this ID in their 'dependencies'
            # Note: The input tasks might have 'id' or might be transient. 
            # If transient, we assume they are referenced by index or some temporary ID provided in input.
            # The prompt example shows "dependencies": [] // list of task IDs.
            # We'll assume the input includes IDs if dependencies are used.
            
            # Build Dependency Graph for Cycle Detection
            # Map: Task ID -> List of Dependency IDs
            graph = {}
            task_map = {} # ID -> Task Data
            
            for task in tasks_data:
                t_id = task.get('id')
                if t_id is not None:
                    graph[t_id] = task.get('dependencies', [])
                    task_map[t_id] = task
            
            # Detect Cycles using DFS
            visited = set()
            recursion_stack = set()
            circular_tasks = set()
            
            def detect_cycle(node_id, path):
                visited.add(node_id)
                recursion_stack.add(node_id)
                path.append(node_id)
                
                for neighbor in graph.get(node_id, []):
                    if neighbor not in visited:
                        if detect_cycle(neighbor, path):
                            return True
                    elif neighbor in recursion_stack:
                        # Cycle detected!
                        # Mark all nodes in the current path that are part of the cycle
                        # (Simple approach: mark all in recursion stack)
                        # Better: Mark from neighbor to end of path
                        try:
                            start_index = path.index(neighbor)
                            for cycle_node in path[start_index:]:
                                circular_tasks.add(cycle_node)
                        except ValueError:
                            pass
                        return True
                
                recursion_stack.remove(node_id)
                path.pop()
                return False

            for t_id in graph:
                if t_id not in visited:
                    detect_cycle(t_id, [])

            dependency_counts = {}
            for task in tasks_data:
                deps = task.get('dependencies', [])
                for dep_id in deps:
                    dependency_counts[dep_id] = dependency_counts.get(dep_id, 0) + 1
            
            strategy = request.query_params.get('strategy', 'smart')
            
            analyzed_tasks = []
            for task in tasks_data:
                task_id = task.get('id')
                dep_count = dependency_counts.get(task_id, 0) if task_id else 0
                
                score, explanation = calculate_priority_score(task, dep_count, strategy)
                
                # Check for circular dependency
                is_circular = task_id in circular_tasks
                if is_circular:
                    explanation.append("⚠️ Circular Dependency Detected!")
                    # Optional: Penalize score? Or just flag it.
                    # Let's penalize to push it down or keep it same but warn.
                    # The prompt says "visually flag", so warning is key.
                
                task_result = task.copy()
                task_result['score'] = score
                task_result['explanation'] = explanation
                task_result['has_circular_dependency'] = is_circular
                analyzed_tasks.append(task_result)
            
            # Sort by score descending
            analyzed_tasks.sort(key=lambda x: x['score'], reverse=True)
            
            return Response(analyzed_tasks)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SuggestTasksView(APIView):
    def get(self, request):
        tasks = Task.objects.all()
        # Convert model instances to dicts for scoring
        tasks_data = []
        
        # We need to build the dependency graph for DB tasks too
        # Task model has 'dependencies' (blocking). 
        # 'dependencies' field in model means "This task depends on X".
        # So if A depends on B, A.dependencies.add(B).
        # We want to know how many tasks depend on B.
        # This is B.blocking.count() (using related_name='blocking')
        
        for task in tasks:
            # For model, we can use the reverse relationship directly
            # 'blocking' is the related_name for tasks that depend on this task
            # Wait, in model: dependencies = ManyToMany('self', symmetrical=False, related_name='blocking')
            # If A.dependencies.add(B) -> A depends on B.
            # B.blocking.all() -> Returns A.
            # So dependency_count (tasks blocked by this) is task.blocking.count()
            
            dep_count = task.blocking.count()
            
            # Serialize to dict for scoring function
            # We can use serializer or manual dict
            task_dict = {
                'id': task.id,
                'title': task.title,
                'due_date': task.due_date,
                'estimated_hours': task.estimated_hours,
                'importance': task.importance,
            }
            
            score, explanation = calculate_priority_score(task_dict, dep_count)
            
            task_result = task_dict.copy()
            task_result['score'] = score
            task_result['explanation'] = explanation
            tasks_data.append(task_result)
            
        # Sort
        tasks_data.sort(key=lambda x: x['score'], reverse=True)
        
        # Return top 3
        return Response(tasks_data[:3])
