"""
Lightweight email notification service for hazard assessments.
Designed to be non-blocking and efficient to avoid system slowdown.
"""

import threading
import logging
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.utils import timezone
from datetime import datetime

logger = logging.getLogger(__name__)

class HazardEmailNotificationService:
    """Lightweight email notification service for hazard assessments"""
    
    @staticmethod
    def send_assessment_completion_notification(hazard, inspector):
        """
        Send notification to manager when inspector completes assessment.
        This runs in a separate thread to avoid blocking the main request.
        """
        try:
            # Run email sending in background thread
            thread = threading.Thread(
                target=HazardEmailNotificationService._send_email_async,
                args=(hazard, inspector),
                daemon=True  # Dies when main thread dies
            )
            thread.start()
            
            # Log that notification was queued (non-blocking)
            logger.info(f"Hazard assessment notification queued for hazard {hazard.id}")
            
        except Exception as e:
            # Log error but don't fail the main request
            logger.error(f"Failed to queue hazard notification: {str(e)}")
    
    @staticmethod
    def _send_email_async(hazard, inspector):
        """
        Actually send the email in background thread.
        This is the heavy lifting that doesn't block the main request.
        """
        try:
            # Get manager email (the person who should be notified)
            manager_email = None
            manager_name = "Manager"
            
            if hazard.managed_by and hazard.managed_by.email:
                manager_email = hazard.managed_by.email
                manager_name = hazard.managed_by.username
            elif hazard.assigned_department and hazard.assigned_department.manager:
                if hasattr(hazard.assigned_department.manager, 'email'):
                    manager_email = hazard.assigned_department.manager.email
                    manager_name = hazard.assigned_department.manager.username
            
            if not manager_email:
                logger.warning(f"No manager email found for hazard {hazard.id}")
                return
            
            # Create email content
            subject = f"Hazard Assessment Completed - {hazard.serial_number}"
            
            # Simple text content
            text_content = f"""
Hazard Assessment Completed

Dear {manager_name},

Inspector {inspector.username} has completed the assessment for the following hazard:

Hazard ID: {hazard.serial_number}
Description: {hazard.hazard_description}
Location: {hazard.location}
Risk Level: {hazard.severity_level}
Status: {hazard.status}

The hazard is now ready for your review and approval.

Please log into the system to review the assessment details and take appropriate action.

Best regards,
Inspection Management System
            """.strip()
            
            # Extract assessment details from hazard
            assessment_notes = hazard.additional_notes or ""
            recommended_controls = hazard.recommended_controls or ""
            
            # Parse assessment data if available
            assessment_summary = ""
            if "=== INSPECTOR ASSESSMENT ===" in assessment_notes:
                assessment_parts = assessment_notes.split("=== INSPECTOR ASSESSMENT ===")
                if len(assessment_parts) > 1:
                    assessment_summary = assessment_parts[1].strip()
            
            # Parse recommendations if available
            recommendations_summary = ""
            if "=== INSPECTOR RECOMMENDATIONS ===" in recommended_controls:
                rec_parts = recommended_controls.split("=== INSPECTOR RECOMMENDATIONS ===")
                if len(rec_parts) > 1:
                    recommendations_summary = rec_parts[1].strip()

            # Compact Professional Hazard Assessment Email Template
            html_content = f"""
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Hazard Assessment Completed</title>
            </head>
            <body style="margin: 0; padding: 0; background-color: #f5f5f5; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;">
                <div style="max-width: 650px; margin: 0 auto; background-color: #ffffff; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
                    
                    <!-- Compact Header -->
                    <div style="background: linear-gradient(135deg, #dc2626 0%, #b91c1c 100%); color: white; padding: 20px; text-align: center;">
                        <div style="display: flex; align-items: center; justify-content: center; margin-bottom: 10px;">
                            <span style="font-size: 32px; margin-right: 10px;">⚠️</span>
                            <h1 style="margin: 0; font-size: 22px; font-weight: 700;">HAZARD ASSESSMENT COMPLETED</h1>
                        </div>
                        <p style="margin: 0; font-size: 14px; opacity: 0.9;">Ready for Manager Review</p>
                    </div>
                    
                    <!-- Urgent Alert -->
                    <div style="background: #fef3c7; border-left: 4px solid #f59e0b; padding: 12px 20px; margin: 0;">
                        <div style="display: flex; align-items: center;">
                            <span style="font-size: 16px; margin-right: 8px;">🚨</span>
                            <strong style="color: #92400e; font-size: 14px;">URGENT: Manager Review Required</strong>
                        </div>
                    </div>
                    
                    <!-- Main Content -->
                    <div style="padding: 20px;">
                        <p style="font-size: 15px; color: #374151; margin: 0 0 15px 0;">Dear <strong>{manager_name}</strong>,</p>
                        
                        <p style="font-size: 14px; color: #374151; line-height: 1.5; margin: 0 0 20px 0;">
                            Inspector <strong style="color: #dc2626;">{inspector.username}</strong> has completed the assessment for hazard <strong>{hazard.serial_number}</strong>.
                        </p>
                        
                        <!-- Compact Hazard Info -->
                        <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 15px; margin: 15px 0;">
                            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; font-size: 13px;">
                                <div>
                                    <span style="color: #6b7280; font-weight: 600;">Hazard ID:</span>
                                    <span style="color: #dc2626; font-weight: 700; margin-left: 5px;">{hazard.serial_number}</span>
                                </div>
                                <div>
                                    <span style="color: #6b7280; font-weight: 600;">Risk Level:</span>
                                    <span style="background: #dc2626; color: white; padding: 2px 8px; border-radius: 12px; font-size: 11px; font-weight: 600; margin-left: 5px;">{hazard.severity_level.upper()}</span>
                                </div>
                                <div>
                                    <span style="color: #6b7280; font-weight: 600;">Location:</span>
                                    <span style="color: #374151; margin-left: 5px;">{hazard.location}</span>
                                </div>
                                <div>
                                    <span style="color: #6b7280; font-weight: 600;">Assessed By:</span>
                                    <span style="color: #374151; margin-left: 5px;">{inspector.username}</span>
                                </div>
                            </div>
                            
                            <!-- Hazard Description -->
                            <div style="margin-top: 12px; padding-top: 12px; border-top: 1px solid #e2e8f0;">
                                <span style="color: #6b7280; font-weight: 600; font-size: 12px;">DESCRIPTION:</span>
                                <p style="margin: 5px 0 0 0; font-size: 13px; color: #374151; line-height: 1.4; background: white; padding: 8px; border-radius: 4px; border-left: 3px solid #dc2626;">
                                    {hazard.hazard_description}
                                </p>
                            </div>
                        </div>
                        
                        <!-- Assessment Summary -->
                        {f'''
                        <div style="background: #f0f9ff; border: 1px solid #0ea5e9; border-radius: 8px; padding: 15px; margin: 15px 0;">
                            <h4 style="margin: 0 0 10px 0; color: #0c4a6e; font-size: 14px; display: flex; align-items: center;">
                                <span style="margin-right: 8px;">📋</span> INSPECTOR ASSESSMENT
                            </h4>
                            <div style="font-size: 13px; color: #0c4a6e; line-height: 1.4; max-height: 120px; overflow-y: auto;">
                                {assessment_summary[:300]}{'...' if len(assessment_summary) > 300 else ''}
                            </div>
                        </div>
                        ''' if assessment_summary else ''}
                        
                        <!-- Recommendations Summary -->
                        {f'''
                        <div style="background: #f0fdf4; border: 1px solid #22c55e; border-radius: 8px; padding: 15px; margin: 15px 0;">
                            <h4 style="margin: 0 0 10px 0; color: #166534; font-size: 14px; display: flex; align-items: center;">
                                <span style="margin-right: 8px;">💡</span> INSPECTOR RECOMMENDATIONS
                            </h4>
                            <div style="font-size: 13px; color: #166534; line-height: 1.4; max-height: 100px; overflow-y: auto;">
                                {recommendations_summary[:250]}{'...' if len(recommendations_summary) > 250 else ''}
                            </div>
                        </div>
                        ''' if recommendations_summary else ''}
                        
                        <!-- Action Button -->
                        <div style="text-align: center; margin: 20px 0;">
                            <a href="{settings.FRONTEND_URL}/hazard_log/list" 
                               style="background: linear-gradient(135deg, #dc2626 0%, #b91c1c 100%); color: white; padding: 12px 25px; text-decoration: none; border-radius: 6px; display: inline-block; font-weight: 600; font-size: 14px; box-shadow: 0 2px 4px rgba(220, 38, 38, 0.3);">
                                🔍 REVIEW ASSESSMENT
                            </a>
                        </div>
                        
                        <!-- Quick Actions -->
                        <div style="background: #f9fafb; border-radius: 6px; padding: 12px; margin: 15px 0; font-size: 12px; color: #6b7280;">
                            <strong>Quick Actions:</strong> Approve • Reject • Reassign • Add Comments
                        </div>
                        
                        <!-- Footer -->
                        <div style="border-top: 1px solid #e2e8f0; padding-top: 15px; margin-top: 20px; text-align: center;">
                            <p style="margin: 0; color: #9ca3af; font-size: 11px;">
                                Inspection Management System • {timezone.now().strftime('%B %d, %Y at %I:%M %p')}
                            </p>
                        </div>
                    </div>
                </div>
            </body>
            </html>
            """
            
            # Send email
            from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'no-reply@example.com')
            
            email = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=from_email,
                to=[manager_email]
            )
            email.attach_alternative(html_content, "text/html")
            email.send()
            
            logger.info(f"Hazard assessment notification sent successfully to {manager_email}")
            
        except Exception as e:
            # Log error but don't crash the background thread
            logger.error(f"Failed to send hazard notification email: {str(e)}")
    
    @staticmethod
    def send_status_update_notification(hazard, old_status, new_status, updated_by):
        """
        Send notification when hazard status changes.
        Lightweight implementation for status updates.
        """
        try:
            # Only send notifications for important status changes
            important_statuses = ['Approved', 'Rejected', 'Reassigned', 'Done']
            
            if new_status not in important_statuses:
                return
            
            # Run in background thread
            thread = threading.Thread(
                target=HazardEmailNotificationService._send_status_email_async,
                args=(hazard, old_status, new_status, updated_by),
                daemon=True
            )
            thread.start()
            
            logger.info(f"Hazard status notification queued for hazard {hazard.id}")
            
        except Exception as e:
            logger.error(f"Failed to queue status notification: {str(e)}")
    
    @staticmethod
    def _send_status_email_async(hazard, old_status, new_status, updated_by):
        """Send status update email in background thread"""
        try:
            # Determine who should be notified
            recipient_email = None
            recipient_name = "User"
            
            if new_status == 'Approved' and hazard.assigned_to:
                # Notify inspector when approved
                if hasattr(hazard.assigned_to, 'email') and hazard.assigned_to.email:
                    recipient_email = hazard.assigned_to.email
                    recipient_name = hazard.assigned_to.username
            elif new_status == 'Reassigned' and hazard.assigned_to:
                # Notify new assignee
                if hasattr(hazard.assigned_to, 'email') and hazard.assigned_to.email:
                    recipient_email = hazard.assigned_to.email
                    recipient_name = hazard.assigned_to.username
            
            if not recipient_email:
                return
            
            subject = f"Hazard Status Updated - {hazard.serial_number}"
            
            text_content = f"""
Hazard Status Update

Dear {recipient_name},

The status of hazard {hazard.serial_number} has been updated:

Previous Status: {old_status}
New Status: {new_status}
Updated By: {updated_by.username}
Updated At: {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}

Please log into the system to view the updated details.

Best regards,
Inspection Management System
            """.strip()
            
            html_content = f"""
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Hazard Status Updated</title>
            </head>
            <body style="margin: 0; padding: 0; background-color: #f5f5f5; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;">
                <div style="max-width: 650px; margin: 0 auto; background-color: #ffffff; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
                    
                    <!-- Compact Header -->
                    <div style="background: linear-gradient(135deg, #059669 0%, #047857 100%); color: white; padding: 20px; text-align: center;">
                        <div style="display: flex; align-items: center; justify-content: center; margin-bottom: 10px;">
                            <span style="font-size: 32px; margin-right: 10px;">✅</span>
                            <h1 style="margin: 0; font-size: 22px; font-weight: 700;">HAZARD STATUS UPDATED</h1>
                        </div>
                        <p style="margin: 0; font-size: 14px; opacity: 0.9;">Action Taken on Assessment</p>
                    </div>
                    
                    <!-- Status Change Alert -->
                    <div style="background: #ecfdf5; border-left: 4px solid #059669; padding: 12px 20px; margin: 0;">
                        <div style="display: flex; align-items: center;">
                            <span style="font-size: 16px; margin-right: 8px;">📋</span>
                            <strong style="color: #047857; font-size: 14px;">Status Change Notification</strong>
                        </div>
                    </div>
                    
                    <!-- Main Content -->
                    <div style="padding: 20px;">
                        <p style="font-size: 15px; color: #374151; margin: 0 0 15px 0;">Dear <strong>{recipient_name}</strong>,</p>
                        
                        <p style="font-size: 14px; color: #374151; line-height: 1.5; margin: 0 0 20px 0;">
                            The status of hazard <strong style="color: #059669;">{hazard.serial_number}</strong> has been updated.
                        </p>
                        
                        <!-- Compact Status Change Info -->
                        <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 15px; margin: 15px 0;">
                            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; font-size: 13px;">
                                <div>
                                    <span style="color: #6b7280; font-weight: 600;">Hazard ID:</span>
                                    <span style="color: #059669; font-weight: 700; margin-left: 5px;">{hazard.serial_number}</span>
                                </div>
                                <div>
                                    <span style="color: #6b7280; font-weight: 600;">Location:</span>
                                    <span style="color: #374151; margin-left: 5px;">{hazard.location}</span>
                                </div>
                                <div>
                                    <span style="color: #6b7280; font-weight: 600;">Previous Status:</span>
                                    <span style="color: #6b7280; text-decoration: line-through; margin-left: 5px;">{old_status}</span>
                                </div>
                                <div>
                                    <span style="color: #6b7280; font-weight: 600;">Updated By:</span>
                                    <span style="color: #374151; margin-left: 5px;">{updated_by.username}</span>
                                </div>
                            </div>
                            
                            <!-- New Status Highlight -->
                            <div style="margin-top: 12px; padding-top: 12px; border-top: 1px solid #e2e8f0; text-align: center;">
                                <span style="color: #6b7280; font-weight: 600; font-size: 12px;">NEW STATUS:</span>
                                <div style="margin-top: 5px;">
                                    <span style="background: #059669; color: white; padding: 6px 15px; border-radius: 20px; font-size: 14px; font-weight: 600;">
                                        {new_status.upper()}
                                    </span>
                                </div>
                            </div>
                        </div>
                        
                        <!-- Action Button -->
                        <div style="text-align: center; margin: 20px 0;">
                            <a href="{settings.FRONTEND_URL}/hazard_log/list" 
                               style="background: linear-gradient(135deg, #059669 0%, #047857 100%); color: white; padding: 12px 25px; text-decoration: none; border-radius: 6px; display: inline-block; font-weight: 600; font-size: 14px; box-shadow: 0 2px 4px rgba(5, 150, 105, 0.3);">
                                📋 VIEW HAZARD DETAILS
                            </a>
                        </div>
                        
                        <!-- Footer -->
                        <div style="border-top: 1px solid #e2e8f0; padding-top: 15px; margin-top: 20px; text-align: center;">
                            <p style="margin: 0; color: #9ca3af; font-size: 11px;">
                                Inspection Management System • {timezone.now().strftime('%B %d, %Y at %I:%M %p')}
                            </p>
                        </div>
                    </div>
                </div>
            </body>
            </html>
            """
            
            from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'no-reply@example.com')
            
            email = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=from_email,
                to=[recipient_email]
            )
            email.attach_alternative(html_content, "text/html")
            email.send()
            
            logger.info(f"Hazard status notification sent successfully to {recipient_email}")
            
        except Exception as e:
            logger.error(f"Failed to send status notification email: {str(e)}")
