from celery import shared_task
from celery.utils.log import get_task_logger
logger = get_task_logger(__name__)

# from apibridge.views import *
from branches.models import *
from apibridge import views
import requests
from django.db import transaction
from branches.models import *
from students.models import *
# from branches import tasks


# @shared_task(bind = True)

@shared_task
def process_all_branches_sections():
    branches = Branch.objects.filter(is_active = True)
    results = []
    for branch in branches:
        result = views.process_sections_for_branch(branch.branch_id)
        logger.info(f'Processed branch: {branch.branch_id}')
        results.append(result)
    
    return results  # Optionally return the results or handle as necessary



@shared_task
def process_all_branches_students():
    branches = Branch.objects.filter(is_active = True)
    results = []
    for branch in branches:
        result = views.process_students_for_branch(branch.branch_id)
        logger.info(f'Processed branch: {branch.branch_id}')
        results.append(result)    
    return results  # Optionally return the results or handle as necessary



# @shared_task
# def process_wizklub_sales_from_varna():



# @shared_task
# def sync_designations_from_varna():
#     url = "http://192.168.0.6/varna_api/staff_designations.php?token=chaitanya"

#     try:
#         response = requests.get(url, timeout=20)
#         response.raise_for_status()
#         data = response.json()

#         if not data:
#             return "No data found"
#         for item in data:    
#             designation_id = item.get('id')
#             short_code = item.get('short_code')
#             name = item.get('designation')
#             division_id = item.get('division_id')
#             departments_id = item.get('departments_id')            
#             active_status = item.get('active_status')

#             if not designation_id or not name:
#                 continue   
#             department = Department.objects.filter(department_id=departments_id).first()
#             existing_designation = Designation.objects.filter(designation_id=designation_id).first()
#             if existing_designation:
#                 existing_designation.name = name
#                 existing_designation.department = department
#                 existing_designation.short_code = short_code
#                 existing_designation.division_id = division_id
#                 existing_designation.is_active = True if active_status == "1" else False
#                 existing_designation.save()
#             else:
#                 try:
#                     Designation.objects.create(
#                         designation_id=designation_id,
#                         name=name,
#                         department=department,
#                         division_id=division_id,
#                         short_code=short_code,
#                         is_active=True if active_status == "1" else False
#                     )
#                 except:
#                     continue       # pass or continue      
#         return "Sync completed successfully"

#     except requests.exceptions.RequestException as e:
#         return f"API Error: {str(e)}"
     
                

# # from celery import shared_task
# # import requests
# # from .models import Department
# # from django.db import transaction
# # import logging

# # logger = logging.getLogger(__name__)

# def convert_active_status(active_status):
#     return True if active_status == "1" else False

# @shared_task
# def sync_departments_from_varna():
#     url = "http://192.168.0.6/varna_api/staff_department.php?token=chaitanya"

#     try:
#         response = requests.get(url, timeout=30)
#         response.raise_for_status()
#         data = response.json()

#         if not data:
#             logger.warning("No data found in department API")
#             return "No data found"

#         with transaction.atomic():
#             for item in data:
#                 department_id = item.get('id')
#                 name = item.get('name')
#                 division_id = item.get('division_id')
#                 active_status = item.get('active_status')

#                 if department_id and name:
#                     department, created = Department.objects.update_or_create(
#                         department_id=department_id,
#                         defaults={
#                             'name': name,
#                             'division_id': division_id,
#                             'is_active': convert_active_status(active_status),
#                         }
#                     )

#                     if created:
#                         logger.info(f"Created Department: {name} ({department_id})")
#                     else:
#                         logger.info(f"Updated Department: {name} ({department_id})")

#         return "Department sync completed successfully"

#     except requests.exceptions.RequestException as e:
#         logger.error(f"Request error: {e}")
#         return f"Request error: {str(e)}"
#     except Exception as e:
#         logger.error(f"Unexpected error: {e}")
#         return "Unexpected error occurred"
    

#============================================= Sync Employees ====================================================================

# from celery import shared_task
# import requests
# from .models import Teacher, Branch, Department, Designation, Gender

# @shared_task
# def sync_scts_teachers_from_api(branch_id):
#     try:
#         branch = Branch.objects.get(branch_id=branch_id)
#         url = f"http://192.168.0.6/varna_api/employee_master.php?token=chaitanya&branch_id={branch_id}"
#         response = requests.get(url,timeout=20)
#         response.raise_for_status()
#         data = response.json()

#         if not data:
#             return "No data found"

#         for item in data:
#             try:
#                 teacher_id = item.get('id')
#                 full_name = item.get('employee_name')
#                 employee_id = item.get('employee_id')
#                 employee_code = item.get('employee_code')
#                 designation_id = item.get('designation_id')
#                 departments_id = item.get('departments_id')
#                 qualification = item.get('qualification')
#                 joining_date = item.get('joining_date')
#                 gender_str = item.get('gender', '').lower()
#                 employee_status_id = item.get('employee_status_id')

#                 if not (teacher_id and full_name):
#                     continue

#                 gender_id = 1 if gender_str == 'male' else 2 if gender_str == 'female' else 3
#                 gender = Gender.objects.filter(gender_id=gender_id).first()
#                 department = Department.objects.filter(department_id=departments_id).first()
#                 designation = Designation.objects.filter(designation_id=designation_id).first()

#                 teacher = Teacher.objects.filter(teacher_id=teacher_id).first()

#                 if teacher:
#                     teacher.branch = branch
#                     teacher.employee_id = employee_id
#                     teacher.employee_code = employee_code
#                     teacher.full_name = full_name
#                     teacher.designation = designation
#                     teacher.department = department
#                     teacher.qualification = qualification
#                     teacher.date_of_joining = joining_date
#                     teacher.gender = gender
#                     teacher.employee_status_id = employee_status_id
#                     teacher.is_active = True if employee_status_id == "EX" else False
#                     teacher.save()
#                 else:
#                     Teacher.objects.create(
#                         teacher_id=teacher_id,
#                         branch=branch,
#                         employee_id=employee_id,
#                         employee_code=employee_code,
#                         full_name=full_name,
#                         designation=designation,
#                         department=department,
#                         qualification=qualification,
#                         date_of_joining=joining_date,
#                         gender=gender,
#                         employee_status_id=employee_status_id,
#                         is_active=True if employee_status_id == "EX" else False
#                     )
#             except Exception as inner_error:
#                 print(f"Error processing teacher {teacher_id}: {inner_error}")

#         return "Sync completed successfully"
#     except Exception as e:
#         return f"Error: {str(e)}"






# @shared_task
# def sync_scts_teachers_from_api(building_category_id, branch_id):
#     try:
#         branch = Branch.objects.get(branch_id=branch_id)
#         external_building_id = branch.external_building_id

#         try:
#             building_category = BuildingCategory.objects.get(building_category_id=building_category_id)
#         except BuildingCategory.DoesNotExist:
#             return {"error": f"BuildingCategory with ID {building_category_id} not found"}

#         url = f"http://192.168.0.6/varna_api/employee_master.php?token=chaitanya&branch_id={external_building_id}"
#         response = requests.get(url, timeout=20)
#         response.raise_for_status()
#         data = response.json()

#         if not data:
#             return {"message": "No data found"}

#         created_count, updated_count = 0, 0

#         for item in data:
#             external_id = item.get('id')
#             employee_name = item.get('employee_name')
#             if not external_id or not employee_name:
#                 continue

#             # Gender
#             gender_str = item.get('gender', '').lower()
#             gender_id = 1 if gender_str == 'male' else 2 if gender_str == 'female' else 3
#             gender = Gender.objects.filter(gender_id=gender_id).first()

#             # Department & Designation
#             department = Department.objects.filter(
#                 Q(external_id=item.get('departments_id')),
#                 Q(building_category_id=building_category_id)
#             ).first()
#             designation = Designation.objects.filter(
#                 Q(external_id=item.get('designation_id')),
#                 Q(building_category_id=building_category_id)
#             ).first()

#             # EX = active
#             is_active = item.get('employee_status_id') == "EX"

#             teacher_data = {
#                 "branch": branch,
#                 "employee_id": item.get('employee_id'),
#                 "employee_code": item.get('employee_code'),
#                 "full_name": employee_name,
#                 "designation": designation,
#                 "department": department,
#                 "qualification": item.get('qualification'),
#                 "date_of_joining": item.get('joining_date'),
#                 "gender": gender,
#                 "is_active": is_active
#             }

#             teacher = Teacher.objects.filter(
#                 Q(external_id=external_id), Q(building_category_id=building_category_id)
#             ).first()

#             if teacher:
#                 for field, value in teacher_data.items():
#                     setattr(teacher, field, value)
#                 teacher.save()
#                 updated_count += 1
#             else:
#                 Teacher.objects.create(
#                     external_id=external_id,
#                     building_category=building_category,
#                     **teacher_data
#                 )
#                 created_count += 1

#         return {
#             "message": "Task completed successfully",
#             "created": created_count,
#             "updated": updated_count
#         }

#     except Branch.DoesNotExist:
#         return {"error": f"Branch with ID {branch_id} not found"}
#     except requests.exceptions.RequestException as e:
#         return {"error": f"API request failed: {str(e)}"}
#     except Exception as e:
#         import logging
#         logger = logging.getLogger(__name__)
#         logger.exception(f"Unexpected error during teacher sync for branch {branch_id}")
#         return {"error": f"Unexpected error: {str(e)}"}





# @shared_task
# def sync_telangana_teachers_from_api(building_category_id, branch_id):
#     try:
#         branch = Branch.objects.get(branch_id=branch_id)
#         external_building_id = branch.external_building_id

#         try:
#             building_category = BuildingCategory.objects.get(building_category_id=building_category_id)
#         except BuildingCategory.DoesNotExist:
#             return {"error": f"BuildingCategory with ID {building_category_id} not found"}

#         url = f"http://192.168.0.6/varna_api/ets_employee_master.php?token=chaitanya&branch_id={external_building_id}"
#         response = requests.get(url, timeout=20)
#         response.raise_for_status()
#         data = response.json()

#         if not data:
#             return {"message": "No data found"}

#         created_count, updated_count = 0, 0

#         for item in data:
#             external_id = item.get('id')
#             employee_name = item.get('employee_name')
#             if not external_id or not employee_name:
#                 continue

#             # Gender
#             gender_str = item.get('gender', '').lower()
#             gender_id = 1 if gender_str == 'male' else 2 if gender_str == 'female' else 3
#             gender = Gender.objects.filter(gender_id=gender_id).first()

#             # Department & Designation
#             department = Department.objects.filter(
#                 Q(external_id=item.get('departments_id')),
#                 Q(building_category_id=building_category_id)
#             ).first()
#             designation = Designation.objects.filter(
#                 Q(external_id=item.get('designation_id')),
#                 Q(building_category_id=building_category_id)
#             ).first()

#             # EX = active
#             is_active = item.get('employee_status_id') == "EX"

#             teacher_data = {
#                 "branch": branch,
#                 "employee_id": item.get('employee_id'),
#                 "employee_code": item.get('employee_code'),
#                 "full_name": employee_name,
#                 "designation": designation,
#                 "department": department,
#                 "qualification": item.get('qualification'),
#                 "date_of_joining": item.get('joining_date'),
#                 "gender": gender,
#                 "is_active": is_active
#             }

#             teacher = Teacher.objects.filter(
#                 Q(external_id=external_id), Q(building_category_id=building_category_id)
#             ).first()

#             if teacher:
#                 for field, value in teacher_data.items():
#                     setattr(teacher, field, value)
#                 teacher.save()
#                 updated_count += 1
#             else:
#                 Teacher.objects.create(
#                     external_id=external_id,
#                     building_category=building_category,
#                     **teacher_data
#                 )
#                 created_count += 1

#         return {
#             "message": "Task completed successfully",
#             "created": created_count,
#             "updated": updated_count
#         }

#     except Branch.DoesNotExist:
#         return {"error": f"Branch with ID {branch_id} not found"}
#     except requests.exceptions.RequestException as e:
#         return {"error": f"API request failed: {str(e)}"}
#     except Exception as e:
#         import logging
#         logger = logging.getLogger(__name__)
#         logger.exception(f"Unexpected error during teacher sync for branch {branch_id}")
#         return {"error": f"Unexpected error: {str(e)}"}
    
    
#============================================================ Sync all branches Employees Data ===============================================================================

# @shared_task
# def sync_scts_teachers_for_all_branches():
#     building_category_id = 1
#     active_branches = Branch.objects.filter(building_category_id = building_category_id, is_active=True)
#     for branch in active_branches:
#         sync_scts_teachers_from_api.delay(building_category_id,branch.branch_id)
#     return "Scheduled sync for all active branches started"

# @shared_task
# def sync_telangana_teachers_for_all_branches():
#     building_category_id = 2
#     active_branches = Branch.objects.filter(building_category_id = building_category_id, is_active=True)
#     for branch in active_branches:
#         sync_telangana_teachers_from_api.delay(building_category_id,branch.branch_id)
#     return "Scheduled sync for all active branches started"

#============================================================= sync states from Varna  =========================================================================================
 
# @shared_task
# def sync_states_from_varna():
#     url = "http://192.168.0.1/sctsadmissions/asset_state_api.php?token=chaitanya"
#     response = requests.get(url,timeout=20)
#     try:
#         data = response.json().get('data', [])
#     except Exception as e:
#         return f"Error parsing response: {e}"

#     for i in data:
#         try:
#             if State.objects.filter(state_id=i['id']).exists():
#                 state = State(state_id=i["id"], name=i['state_name'])
#                 state.save()
#             elif not State.objects.filter(Q(state_id=i["id"]) & Q(name=i['state_name'])).exists():
#                 State.objects.update_or_create(state_id=i["id"], name=i['state_name'])
#         except Exception as e:
#             continue  # Optionally log the error
#     return "States sync complete"

#========================================================== Sync Zones From Varna ======================================================================
 

# @shared_task
# def sync_zones_from_varna():
#     url = "http://192.168.0.1/sctsadmissions/asset_zone_api.php?token=chaitanya"
#     try:
#         response = requests.get(url,timeout=20)
#         data = response.json().get('data', [])
#     except Exception as e:
#         return f"Error fetching or parsing zones: {e}"

#     for i in data:
#         try:
#             if Zone.objects.filter(zone_id=i['id']).exists():
#                 zone = Zone(zone_id=i["id"], state_id=i['state_id'], name=i['zone_name'])
#                 zone.save()
#             elif not Zone.objects.filter(Q(zone_id=i["id"]) & Q(name=i['zone_name'])).exists():
#                 Zone.objects.update_or_create(zone_id=i["id"], state_id=i['state_id'], name=i['zone_name'])
#         except Exception:
#             continue  # Optionally log the error
#     return "Zones sync complete"


#=======================================================  sync Branches from Varna  ======================================================================


# @shared_task
# def sync_branches_from_varna():
#     url = "http://192.168.0.1/sctsadmissions/asset_branch_api.php?token=chaitanya"
#     try:
#         response = requests.get(url,timeout=20)
#         data = response.json().get('data', [])
#     except Exception as e:
#         return f"Error fetching or parsing branches: {e}"

#     errors = []

#     for item in data:
#         try:
#             state = State.objects.filter(state_id=item['state_id']).first()
#             zone = Zone.objects.filter(zone_id=item['zone_id']).first()

#             if Branch.objects.filter(branch_id=item['id']).exists():
#                 branch = Branch(
#                     branch_id=item["id"],
#                     state=state,
#                     zone=zone,
#                     name=item['branch_name'],
#                     building_code=item['building_code'],
#                     location_incharge=item['principal_name'],
#                     email=item['branch_mailid'],
#                     phonenumber=item['principal_phno'],
#                     city=item['city'],
#                     address=item['address'],
#                     is_active=item['active_status'],
#                 )
#                 branch.save()
#             elif not Branch.objects.filter(Q(branch_id=item["id"]) | Q(name=item['branch_name'])).exists():
#                 Branch.objects.update_or_create(
#                     branch_id=item["id"],
#                     defaults={
#                         'state': state,
#                         'zone': zone,
#                         'name': item['branch_name'],
#                         'building_code': item['building_code'],
#                         'location_incharge': item['principal_name'],
#                         'email': item['branch_mailid'],
#                         'phonenumber': item['principal_phno'],
#                         'city': item['city'],
#                         'address': item['address'],
#                         'is_active': item['active_status'],
#                     }
#                 )
#             else:
#                 errors.append(f"Unhandled branch ID {item['id']}")
#         except Exception as e:
#             errors.append(f"Error processing branch ID {item['id']}: {str(e)}")

#     return {
#         "message": "Branch sync completed",
#         "errors": errors
#     }


#======================================================  Sync Orientations From Varna ===============================================================

 
# from django.db import IntegrityError

 

# @shared_task
# def sync_orientations_from_varna():
#     url = "http://192.168.0.6/varna_api/orientation.php?token=chaitanya"

#     try:
#         response = requests.get(url,timeout=20)
#         response.raise_for_status()
#         data = response.json()

#         if not data:
#             return {"message": "No data found", "status": 204}

#         created_count = 0
#         updated_count = 0

#         for item in data:
#             varna_orientation_id = item.get('id')
#             name = item.get('orientation_name')
#             short_code = item.get('short_code')
#             is_active = item.get('active_status') == "1"

#             if varna_orientation_id and name:
#                 try:
#                     obj, created = Orientation.objects.update_or_create(
#                         varna_orientation_id=varna_orientation_id,
#                         defaults={
#                             "name": name,
#                             "short_code": short_code,
#                             "is_active": is_active,
#                         }
#                     )
#                     if created:
#                         created_count += 1
#                         logger.info(f"Created Orientation: {name} (ID: {varna_orientation_id})")
#                     else:
#                         updated_count += 1
#                         logger.info(f"Updated Orientation: {name} (ID: {varna_orientation_id})")
#                 except IntegrityError as e:
#                     logger.error(f"DB error Orientation ID {varna_orientation_id}: {e}")
#                 except Exception as e:
#                     logger.error(f"Unexpected error Orientation ID {varna_orientation_id}: {e}")

#         return {
#             "message": "Sync completed",
#             "created": created_count,
#             "updated": updated_count
#         }

#     except requests.exceptions.RequestException as e:
#         logger.error(f"Request error: {e}")
#         return {"error": str(e), "status": 500}
