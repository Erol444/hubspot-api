from typing import List, Union
from hubspot_api.private_api.api_client import ApiClient
from .crm_base import CrmBase
from .converter import markdown_to_html

class Meeting(CrmBase):
    object_name = 'meetings'
    default_properties = ["hs_activity_type","hs_all_assigned_business_unit_ids","hs_at_mentioned_owner_ids","hs_attachment_ids","hs_attendee_owner_ids","hs_body_preview","hs_body_preview_html","hs_body_preview_is_truncated","hs_contact_first_outreach_date","hs_created_by","hs_created_by_user_id","hs_createdate","hs_engagement_source","hs_engagement_source_id","hs_follow_up_action","hs_gdpr_deleted","hs_guest_emails","hs_i_cal_uid","hs_include_description_in_reminder","hs_internal_meeting_notes","hs_lastmodifieddate","hs_meeting_body","hs_meeting_calendar_event_hash","hs_meeting_change_id","hs_meeting_created_from_link_id","hs_meeting_end_time","hs_meeting_external_url","hs_meeting_location","hs_meeting_location_type","hs_meeting_ms_teams_payload","hs_meeting_outcome","hs_meeting_payments_session_id","hs_meeting_pre_meeting_prospect_reminders","hs_meeting_source","hs_meeting_source_id","hs_meeting_start_time","hs_meeting_title","hs_meeting_web_conference_meeting_id","hs_merged_object_ids","hs_modified_by","hs_object_id","hs_object_source","hs_object_source_detail_1","hs_object_source_detail_2","hs_object_source_detail_3","hs_object_source_id","hs_object_source_label","hs_object_source_user_id","hs_outcome_canceled_count","hs_outcome_completed_count","hs_outcome_no_show_count","hs_outcome_rescheduled_count","hs_outcome_scheduled_count","hs_product_name","hs_queue_membership_ids","hs_read_only","hs_roster_object_coordinates","hs_scheduled_tasks","hs_time_to_book_meeting_from_first_contact","hs_timestamp","hs_timezone","hs_unique_creation_key","hs_unique_id","hs_updated_by_user_id","hs_user_ids_of_all_notification_followers","hs_user_ids_of_all_notification_unfollowers","hs_user_ids_of_all_owners","hs_was_imported","hubspot_owner_assigneddate","hubspot_owner_id","hubspot_team_id","hs_all_owner_ids","hs_all_team_ids","hs_all_accessible_team_ids"]
    default_associations = []

    def add_internal_note(self, meeting_id, note: str):
        """
        Set the internal note of a meeting
        """
        return self.update(meeting_id, { "hs_internal_meeting_notes": markdown_to_html(note) })