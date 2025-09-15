import pyodbc
from django.conf import settings
import json
from datetime import datetime
from typing import List, Dict, Any


class SQLServerConnection:
    """Utility class for connecting to SQL Server (LW8Process) database"""
    
    def __init__(self):
        self.connection_string = self._get_connection_string()
    
    def _get_connection_string(self):
        """Build connection string from Django settings"""
        lw8_config = settings.DATABASES['LW8Process']
        
        # For Windows Authentication (if using Windows Auth)
        if lw8_config.get('USER') and lw8_config.get('PASSWORD'):
            connection_string = (
                f"DRIVER={{ODBC Driver 17 for SQL Server}};"
                f"SERVER={lw8_config['HOST']};"
                f"DATABASE={lw8_config['NAME']};"
                f"UID={lw8_config['USER']};"
                f"PWD={lw8_config['PASSWORD']};"
                f"Trusted_Connection=no;"
            )
        else:
            # For Windows Authentication (Trusted Connection)
            connection_string = (
                f"DRIVER={{ODBC Driver 17 for SQL Server}};"
                f"SERVER={lw8_config['HOST']};"
                f"DATABASE={lw8_config['NAME']};"
                f"Trusted_Connection=yes;"
            )
        
        return connection_string
    
    def get_connection(self):
        """Get database connection"""
        try:
            connection = pyodbc.connect(self.connection_string)
            return connection
        except Exception as e:
            print(f"Error connecting to SQL Server: {str(e)}")
            raise
    
    def fetch_external_departments(self) -> List[Dict[str, Any]]:
        """Fetch all external departments from LW8Process database"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                query = """
                SELECT 
                    id, name, department_type, description, external_system_url, 
                    external_system_id, contact_person, contact_email, contact_phone,
                    capabilities, specializations, status, is_available, 
                    max_concurrent_assignments, location, cost_per_hour, 
                    estimated_completion_days, created_at, updated_at, created_by_user_id
                FROM ExternalDepartments 
                WHERE status = 'ACTIVE'
                ORDER BY name
                """
                
                cursor.execute(query)
                columns = [column[0] for column in cursor.description]
                results = []
                
                for row in cursor.fetchall():
                    row_dict = dict(zip(columns, row))
                    
                    # Parse JSON fields
                    if row_dict['capabilities']:
                        try:
                            row_dict['capabilities'] = json.loads(row_dict['capabilities'])
                        except:
                            row_dict['capabilities'] = []
                    
                    if row_dict['specializations']:
                        try:
                            row_dict['specializations'] = json.loads(row_dict['specializations'])
                        except:
                            row_dict['specializations'] = []
                    
                    # Convert datetime objects to ISO format
                    if row_dict['created_at']:
                        row_dict['created_at'] = row_dict['created_at'].isoformat()
                    if row_dict['updated_at']:
                        row_dict['updated_at'] = row_dict['updated_at'].isoformat()
                    
                    results.append(row_dict)
                
                return results
                
        except Exception as e:
            print(f"Error fetching external departments: {str(e)}")
            raise
    
    def create_ims_assignment(self, assignment_data: Dict[str, Any]) -> int:
        """Create assignment in LW8Process IMSAssignments table"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # First, get the external department ID from SQL Server using external_system_id
                external_system_id = assignment_data['external_department_id']
                cursor.execute(
                    "SELECT id FROM ExternalDepartments WHERE external_system_id = ?", 
                    (external_system_id,)
                )
                result = cursor.fetchone()
                
                if not result:
                    raise ValueError(f"External department with external_system_id '{external_system_id}' not found in SQL Server")
                
                external_dept_id = result[0]
                
                query = """
                INSERT INTO IMSAssignments (
                    ims_evince_id, external_department_id, assignment_type,
                    assigned_by_ims_user_id, target_completion_date, priority,
                    assignment_data, risk_level, risk_category, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """
                
                cursor.execute(query, (
                    assignment_data['ims_evince_id'],
                    external_dept_id,  # Use the integer ID from SQL Server
                    assignment_data['assignment_type'],
                    assignment_data['assigned_by_ims_user_id'],
                    assignment_data['target_completion_date'],
                    assignment_data['priority'],
                    json.dumps(assignment_data['assignment_data']),
                    assignment_data['risk_level'],
                    assignment_data['risk_category'],
                    'ASSIGNED'
                ))
                
                conn.commit()
                
                # Get the inserted ID
                cursor.execute("SELECT @@IDENTITY")
                assignment_id = cursor.fetchone()[0]
                
                return assignment_id
                
        except Exception as e:
            print(f"Error creating IMS assignment: {str(e)}")
            raise
    
    def fetch_assignment_updates(self) -> List[Dict[str, Any]]:
        """Fetch assignment updates from LW8Process database"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                query = """
                SELECT 
                    id, ims_evince_id, external_department_id, assignment_type,
                    assigned_by_ims_user_id, assigned_at, target_completion_date,
                    priority, assignment_data, risk_level, risk_category,
                    status, external_task_id, external_status, completed_at,
                    completion_notes, mitigation_actions, evidence_data, cost_incurred,
                    created_at, updated_at
                FROM IMSAssignments 
                WHERE status IN ('IN_PROGRESS', 'COMPLETED')
                AND updated_at > DATEADD(hour, -24, GETDATE())
                ORDER BY updated_at DESC
                """
                
                cursor.execute(query)
                columns = [column[0] for column in cursor.description]
                results = []
                
                for row in cursor.fetchall():
                    row_dict = dict(zip(columns, row))
                    
                    # Parse JSON fields
                    if row_dict['assignment_data']:
                        try:
                            row_dict['assignment_data'] = json.loads(row_dict['assignment_data'])
                        except:
                            row_dict['assignment_data'] = {}
                    
                    # Convert datetime objects to ISO format
                    for date_field in ['assigned_at', 'target_completion_date', 'completed_at', 'created_at', 'updated_at']:
                        if row_dict[date_field]:
                            row_dict[date_field] = row_dict[date_field].isoformat()
                    
                    results.append(row_dict)
                
                return results
                
        except Exception as e:
            print(f"Error fetching assignment updates: {str(e)}")
            raise
    
    def update_assignment_status(self, assignment_id: int, status: str, 
                               completion_notes: str = None, 
                               mitigation_actions: str = None,
                               evidence_data: str = None,
                               cost_incurred: float = None) -> bool:
        """Update assignment status in LW8Process database"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                query = """
                UPDATE IMSAssignments 
                SET status = ?, completion_notes = ?, mitigation_actions = ?, 
                    evidence_data = ?, cost_incurred = ?, completed_at = ?
                WHERE id = ?
                """
                
                completed_at = datetime.now() if status == 'COMPLETED' else None
                
                cursor.execute(query, (
                    status, completion_notes, mitigation_actions,
                    evidence_data, cost_incurred, completed_at, assignment_id
                ))
                
                conn.commit()
                return True
                
        except Exception as e:
            print(f"Error updating assignment status: {str(e)}")
            raise
