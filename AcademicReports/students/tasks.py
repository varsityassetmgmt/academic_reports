from celery import shared_task
import requests
from branches.models import *
 
from django.db.models import Q
from functools import reduce
from operator import or_
from students.models import *


@shared_task
def sync_branch_wise_orientations():
    academic_year_id = AcademicYear.objects.filter(is_current_academic_year = True, is_active=True).values_list('academic_year_id', flat=True).first()

    if not academic_year_id:
        return "No active current academic year found."

    url = "http://192.168.0.6/varna_api/branchorientations.php"
    params = {"token": "chaitanya", "academic_year_id": academic_year_id}

    try:
        response = requests.get(url, params=params,timeout=15)
        response.raise_for_status()
        data = response.json()

        if not data:
            return "No data found from external API."

        created_or_updated = 0

        for item in data:
            branch_id = item.get('branch_id')
            varna_orientation_id = item.get('orientation_id')
            is_active = item.get('active_status') == "1"

            try:
                branch = Branch.objects.get(branch_id = branch_id,)
                orientation = Orientation.objects.get(varna_orientation_id = varna_orientation_id,)
            except (Branch.DoesNotExist, Orientation.DoesNotExist):
                continue

            branch_orientation, _ = BranchOrientations.objects.get_or_create(branch=branch)

            if is_active:
                branch_orientation.orientations.add(orientation)
                created_or_updated += 1
                
            else:
                branch_orientation.orientations.remove(orientation)
                created_or_updated += 1


        return f"Task completed. Updated or added {created_or_updated} records."

    except requests.exceptions.RequestException as e:
        return f"Request error: {str(e)}"
