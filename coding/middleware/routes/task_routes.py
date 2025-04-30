from flask import Blueprint, jsonify, request, g, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from middleware_data_classes import Task, Group, Membership, User, InvitationStatus
from database import Database
from datetime import datetime
from sqlalchemy import and_

task_bp = Blueprint('tasks', __name__)

# Convert Task SQLAlchemy object to JSON serializable dict
def task_to_dict(task):
    return {
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "due_date": task.due_date.isoformat() if task.due_date else None,
        "status": "completed" if task.status else "pending",
        "group_id": task.group_id,
        "assigned_to": []  # This would need to be populated from a task_assignments table if implemented
    }

@task_bp.route('/', methods=['GET'])
@jwt_required()
def get_tasks():
    """Get all tasks for the current user"""
    try:
        current_user_email = get_jwt_identity()
        db = Database().get_session()

        # Get all groups where the user is a member with ACCEPTED status
        user_memberships = db.query(Membership).filter(
            and_(
                Membership.user_id == current_user_email,
                Membership.status == InvitationStatus.ACCEPTED
            )
        ).all()

        # Get the group IDs
        user_group_ids = [membership.group_id for membership in user_memberships]

        # Get tasks for these groups
        tasks_list = []
        if user_group_ids:
            tasks = db.query(Task).filter(Task.group_id.in_(user_group_ids)).all()
            tasks_list = [task_to_dict(task) for task in tasks]

        return jsonify({"tasks": tasks_list})
    except Exception as e:
        current_app.logger.error(f"Error fetching tasks: {str(e)}")
        return jsonify({"error": "Failed to fetch tasks"}), 500
    finally:
        db.close()

@task_bp.route('/<int:task_id>', methods=['GET'])
@jwt_required()
def get_task(task_id):
    """Get a specific task by ID"""
    try:
        current_user_email = get_jwt_identity()
        db = Database().get_session()

        # Get the task
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            return jsonify({"error": "Task not found"}), 404

        # Verify the user has access to this group
        membership = db.query(Membership).filter(
            and_(
                Membership.user_id == current_user_email,
                Membership.group_id == task.group_id,
                Membership.status == InvitationStatus.ACCEPTED
            )
        ).first()

        if not membership:
            return jsonify({"error": "Access denied"}), 403

        return jsonify({"task": task_to_dict(task)})
    except Exception as e:
        current_app.logger.error(f"Error fetching task: {str(e)}")
        return jsonify({"error": "Failed to fetch task"}), 500
    finally:
        db.close()

@task_bp.route('/', methods=['POST'])
@jwt_required()
def create_task():
    """Create a new task"""
    if not request.json:
        return jsonify({"error": "Invalid request data"}), 400

    required_fields = ['title', 'group_id']
    for field in required_fields:
        if field not in request.json:
            return jsonify({"error": f"Missing required field: {field}"}), 400

    try:
        current_user_email = get_jwt_identity()
        current_app.logger.info(f"Creating task for user: {current_user_email}")
        db = Database().get_session()

        # Verify the user has access to this group
        group_id = request.json.get('group_id')
        current_app.logger.info(f"Checking membership for group_id: {group_id}")
        
        # Debug: List all memberships for this user
        all_memberships = db.query(Membership).filter(Membership.user_id == current_user_email).all()
        current_app.logger.info(f"User has {len(all_memberships)} memberships")
        for membership in all_memberships:
            current_app.logger.info(f"Membership - Group: {membership.group_id}, Status: {membership.status}")
        
        # Now check for specific membership with ACCEPTED status
        membership = db.query(Membership).filter(
            and_(
                Membership.user_id == current_user_email,
                Membership.group_id == group_id,
                Membership.status == InvitationStatus.ACCEPTED
            )
        ).first()

        if not membership:
            current_app.logger.warning(f"Access denied: User {current_user_email} does not have ACCEPTED membership in group {group_id}")
            
            # Try to find any membership record for diagnostics
            any_membership = db.query(Membership).filter(
                and_(
                    Membership.user_id == current_user_email,
                    Membership.group_id == group_id
                )
            ).first()
            
            if any_membership:
                current_app.logger.info(f"User has non-ACCEPTED membership with status: {any_membership.status}")
            else:
                current_app.logger.info(f"No membership record exists for this user and group")
                
            return jsonify({
                "error": "Access denied to this group", 
                "details": "You must be an accepted member of this group to create tasks"
            }), 403

        current_app.logger.info(f"Membership verified for group {group_id}")

        # Parse the due date
        due_date = None
        if 'due_date' in request.json and request.json['due_date']:
            try:
                due_date = datetime.fromisoformat(request.json['due_date'].replace('Z', '+00:00'))
            except ValueError:
                return jsonify({"error": "Invalid date format for due_date"}), 400

        # Create a new task
        new_task = Task(
            title=request.json.get('title'),
            description=request.json.get('description', ''),
            group_id=group_id,
            created_at=datetime.utcnow(),
            due_date=due_date,
            status=False  # Default to pending
        )

        db.add(new_task)
        db.commit()
        db.refresh(new_task)

        return jsonify({"task": task_to_dict(new_task)}), 201
    except Exception as e:
        db.rollback()
        current_app.logger.error(f"Error creating task: {str(e)}")
        return jsonify({"error": "Failed to create task"}), 500
    finally:
        db.close()

@task_bp.route('/<int:task_id>', methods=['PUT'])
@jwt_required()
def update_task(task_id):
    """Update a task"""
    if not request.json:
        return jsonify({"error": "Invalid request data"}), 400

    try:
        current_user_email = get_jwt_identity()
        db = Database().get_session()

        # Get the task
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            return jsonify({"error": "Task not found"}), 404

        # Verify the user has access to this group
        membership = db.query(Membership).filter(
            and_(
                Membership.user_id == current_user_email,
                Membership.group_id == task.group_id,
                Membership.status == InvitationStatus.ACCEPTED
            )
        ).first()

        if not membership:
            return jsonify({"error": "Access denied"}), 403

        # Update the task fields
        if 'title' in request.json:
            task.title = request.json['title']
        
        if 'description' in request.json:
            task.description = request.json['description']
        
        if 'due_date' in request.json:
            try:
                if request.json['due_date']:
                    task.due_date = datetime.fromisoformat(request.json['due_date'].replace('Z', '+00:00'))
                else:
                    task.due_date = None
            except ValueError:
                return jsonify({"error": "Invalid date format for due_date"}), 400
        
        if 'status' in request.json:
            status_str = request.json['status'].lower()
            task.status = status_str == 'completed'

        db.commit()

        return jsonify({"task": task_to_dict(task)})
    except Exception as e:
        db.rollback()
        current_app.logger.error(f"Error updating task: {str(e)}")
        return jsonify({"error": "Failed to update task"}), 500
    finally:
        db.close()

@task_bp.route('/<int:task_id>', methods=['DELETE'])
@jwt_required()
def delete_task(task_id):
    """Delete a task"""
    try:
        current_user_email = get_jwt_identity()
        db = Database().get_session()

        # Get the task
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            return jsonify({"error": "Task not found"}), 404

        # Verify the user has access to this group
        membership = db.query(Membership).filter(
            and_(
                Membership.user_id == current_user_email,
                Membership.group_id == task.group_id,
                Membership.status == InvitationStatus.ACCEPTED
            )
        ).first()

        if not membership:
            return jsonify({"error": "Access denied"}), 403

        # Delete the task
        db.delete(task)
        db.commit()

        return jsonify({"message": "Task deleted successfully"})
    except Exception as e:
        db.rollback()
        current_app.logger.error(f"Error deleting task: {str(e)}")
        return jsonify({"error": "Failed to delete task"}), 500
    finally:
        db.close()