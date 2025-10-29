from __future__ import absolute_import, unicode_literals
import os

from celery import Celery
from django.conf import settings
from celery import schedules


os.environ.setdefault('DJANGO_SETTINGS_MODULE','AcademicReports.settings')

app = Celery('AcademicReports')

app.conf.enable_utc = False

app.conf.update(timezone = 'Asia/Kolkata')

app.config_from_object('django.conf:settings',namespace = 'CELERY')

# Load task modules from all registered Django app configs.
 
# Auto-discover tasks in your apps
app.autodiscover_tasks()


@app.task(bind = True)
def debug_task(self):
    print(f'Request: {self.request!r}')


app.conf.beat_schedule = {

    # Wizklub tasks
    # 'fetch_wizklub_sales_final_day_sync': {
    #     'task': 'wizklub.tasks.fetch_wizklub_sales',
    #     'schedule': schedules.crontab(hour=23, minute=45),  # # Daily at 11:45 PM
    # },

    # 'process_unprocessed_wizklub_sales_every_10_minutes': {
    #     'task': 'wizklub.tasks.fetch_wizklub_sales_is_processed_false',  
    #     'schedule': schedules.crontab(minute='*/10'),  #  Every 10 minutes
    # },

    
    # API sync tasks (Varna bridge)

#========================================================= start  Uncoment again   ===================================================================
    
    # 'sync_designations_from_varna_daily': {
    #     'task': 'apibridge.tasks.sync_designations_from_varna',
    #     'schedule': schedules.crontab(hour=1, minute=6),  # Daily at 1:06 AM
    # },
    # 'sync_departments_from_varna_daily': {
    #     'task': 'apibridge.tasks.sync_departments_from_varna',
    #     'schedule': schedules.crontab(hour=1, minute=1),  # Daily at 1:01 AM
    # },
    # 'sync_teachers_from_varna_daily': {
    #     'task': 'apibridge.tasks.sync_teachers_for_all_branches',
    #     'schedule': schedules.crontab(hour=1, minute=15),  # Daily at 1:15 AM
    # },
    # 'sync_states_daily_from_varna': {
    #     'task': 'apibridge.tasks.sync_states_from_varna',
    #     'schedule': schedules.crontab(hour=2, minute=0),  # Daily at 2:00 AM
    # },
    # 'sync_zones_daily_from_varna': {
    #     'task': 'apibridge.tasks.sync_zones_from_varna',
    #     'schedule': schedules.crontab(hour=2, minute=5),  # Daily at 2:05 AM
    # },
    # 'sync_branches_daily_from_varna': {
    #     'task': 'apibridge.tasks.sync_branches_from_varna',
    #     'schedule': schedules.crontab(hour=2, minute=15),  # Daily at 2:15 AM
    # },

    
    
#========================================================= End Uncoment again   ===================================================================



    # 'sync_orientations_daily_from_varna': {
    #     'task': 'apibridge.tasks.sync_orientations_from_varna',
    #    'schedule': schedules.crontab(hour=2, minute=20),  # Daily at 2:20 AM
    # },
    # 'sync_sections_daily_from_varna': {
    #     'task': 'apibridge.tasks.process_all_branches_sections',
    #    'schedule': schedules.crontab(hour=2, minute=30),  # Daily at 2:30 AM
    # },
    #  'sync_students_daily_from_varna': {
    #     'task': 'apibridge.tasks.process_all_branches_students',
    #    'schedule': schedules.crontab(hour=3, minute=00),  # Daily at 3:00 AM
    # },
    # 'sync_branch_orientations_daily_from_varna': {
    #     'task': 'branches.tasks.sync_branch_wise_orientations',
    #    'schedule': schedules.crontab(hour=6, minute=00),  # Daily at 6:00 AM
    # },
    # 'update_sales_rank_groups_fixed_ids': {
    #     'task': 'teammgmt.tasks.update_sales_rank_groups_fixed_ids',
    #    'schedule': schedules.crontab(minute='*/30'),
    # },
    # 'update_strength_wizklub_branch_sales': {
    #     'task': 'branches.tasks.update_strength_wizklub_branch_sales_ranking_process',
    #     'schedule': schedules.crontab(hour=7, minute=00),  # Daily at 7:00 AM
    # },
    
    # 'create_weekly_sales_task': {
    #     'task': 'wizklub.tasks.create_weekly_sales_task',
    #     'schedule': schedules.crontab(hour=2, minute=10, day_of_week=1),  # Every Monday at 3:10 AM 
    # },

    # 'send_agent_weekly_performence_email_task': {
    #     'task': 'mailhub.tasks.send_agent_weekly_performence_email_task',
    #     'schedule': schedules.crontab(hour=23, minute=30, day_of_week=0),  # Every SUNDAY at 11:30 PM 
    # },

    # 'create_daily_call_conversion_task': {
    #     'task': 'wizklub.tasks.create_daily_call_conversion_task',
    #     'schedule': schedules.crontab(hour=0, minute=30,),  # Daily at 12:30 AM
    # },

    # 'send_daily_call_conversion_report_email_task': {
    #     'task': 'mailhub.tasks.send_daily_call_conversion_report_email_task',
    #     'schedule': schedules.crontab(hour=9, minute=30,),  # Daily at 9:30 AM
    # },

    # 'update_wizklub_missing_sales_amount': {
    #     'task': 'wizklub.tasks.update_wizklub_missing_sales_amount_task',
    #     'schedule': schedules.crontab(hour=23, minute=30,),  # Daily at 11:30 PM
    # },

    # 'update_wizklub_missing_sales_amount': {
    #     'task': 'userhub.tasks.create_agent_daily_attendace_celery_task',
    #     'schedule': schedules.crontab(hour=0, minute=30,),  # Daily at 12:30 PM
    # },


    # 'sync_scts_all_branches_score_attendance': {
    #     'task': 'score.tasks.sync_scts_all_branches_score_attendance',
    #     'schedule': schedules.crontab(minute='*/30'),  # every 15 minutes
    # },
    # 'sync_telangana_all_branches_score_attendance': {
    #     'task': 'score.tasks.sync_telangana_all_branches_score_attendance',
    #     'schedule': schedules.crontab(minute='*/30'),  # every 15 minutes
    # },

 


    # Optional commented tasks for later

    # 'fetch_website_students_data_every_2_minute': {
    #     'task': 'outdoor_summercamp.tasks.fetch_and_process_website_students_data',  
    #     'schedule': schedules.crontab(minute='*/2'),  #  Every 2 minutes
    # },
    # 'fetch_summercamp_sales_data_every_2_minutes': {
    #     'task': 'summercamp.tasks.fetch_and_process_summercamp_sales_data',
    #     'schedule': schedules.crontab(minute='*/2'),  #  Every 2 minutes
    # },
    # 'fetch_summercamp_telangana_schools_sales_data_every_2_minutes': {
    #     'task': 'summercamp.tasks.fetch_and_process_summercamp_telangana_schools_sales_data',
    #     'schedule': schedules.crontab(minute='*/2'),  #  Every 2 minutes
    # },

    # 'fetch_wizklub_sales_every_2_minutes': {
    #     'task': 'wizklub.tasks.fetch_wizklub_sales',
    #     'schedule': schedules.crontab(minute='*/20'),  # Every 2 minutes
    # },
 
    
}



 