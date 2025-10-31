# from .models import *
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.decorators import api_view,permission_classes
from rest_framework.response import Response
from django.db.models import Q
# from rest_framework.decorators import parser_classes
from django.db.models import Q
from branches.models import *
import requests
from students.models import *
import logging
from django.db import transaction
from datetime import datetime
from django.db import IntegrityError
from branches.models import *
from apibridge.tasks import *

# Set up logging
logger = logging.getLogger(__name__)

# Create your views here.
# # ================================================================= Varna States ======================================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_states_varna(request):
    # url ="http://13.127.177.12/api/state/?ordering=id"
    url = "http://192.168.0.1/sctsadmissions/asset_state_api.php?token=chaitanya"
    # response = requests.get(url,headers=headers)
    response = requests.get(url,timeout=20)
    data = response.json()['data']
    errors = []
    for i in data:        
        # if (State.objects.filter(id=i['id']).exists()) & (not State.objects.filter(name=i['state_name']).exists()):
        if State.objects.filter(state_id=i['id']).exists():
            try:
                state = State(state_id =i["id"],name=i['state_name'])
                state.save()
            except:
                pass
        elif not State.objects.filter(Q(state_id =i["id"]) & Q(name=i['state_name'])).exists():
             
            try:
                State.objects.update_or_create(state_id =i["id"],name=i['state_name'])
            except:
                pass        
        else:
            pass
    context= {"message":"task over"}
    return Response(context, status=status.HTTP_200_OK)

# """

# #  New 

# @api_view(['GET'])
# @permission_classes([IsAuthenticated])
# def get_states_from_scts_school_api(request):

#     building_category_id = 1

#     url = "http://192.168.0.1/sctsadmissions/asset_state_api.php?token=chaitanya"
#     try:
#         building_category = BuildingCategory.objects.get(building_category_id = building_category_id)
    
#         # response = requests.get(url,headers=headers)
#         response = requests.get(url)
#         response.raise_for_status()
#         data = response.json()['data']

#         if not data:
#             return Response({"message": "No data found"}, status=status.HTTP_204_NO_CONTENT)

#         # Process state data directly within the view
#         for item in data:     
#             external_state_id = item.get('id')
#             state_name = item.get('state_name')

#             if external_state_id and state_name:
#                 existing_state = State.objects.filter(Q(external_state_id = external_state_id) & Q(building_category_id = building_category_id)).first()
#                 if existing_state:
#                     if existing_state.name != state_name:
#                         existing_state.name = state_name
#                         existing_state.save()
#                         print(f"Updated state: {state_name} (ID: {external_state_id})")
#                     else:
#                         print(f"Duplicate state found, skipping: {state_name} (ID: {external_state_id})")
#                 else:
#                     try:
#                         State.objects.create(
#                             external_state_id=external_state_id,
#                             name=state_name,
#                             building_category=building_category,
#                             is_active=True
#                         )
#                         print(f"Created new state: {state_name} (ID: {external_state_id})")
#                     except Exception as e:
#                         print(f"Error creating state {state_name} (ID: {external_state_id}): {e}")

#         return Response({"message": "Task completed successfully"}, status=status.HTTP_200_OK)

#     except BuildingCategory.DoesNotExist:
#         return Response({"error": "BuildingCategory with ID 1 not found"}, status=status.HTTP_404_NOT_FOUND)

#     except requests.exceptions.RequestException as e:
#         return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# # ================================================================= Varna zones ======================================================

 
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_zones_varna(request):
    url = "http://192.168.0.1/sctsadmissions/asset_zone_api.php?token=chaitanya"
    response = requests.get(url)
    data = response.json()['data']
    errors = []
    for i in data:        
        # if (Zone.objects.filter(id=i['id']).exists()) & (not Zone.objects.filter(name=i['zone_name']).exists()):
        if Zone.objects.filter(zone_id=i['id']).exists():
          
            try:
                zone = Zone(state_id=i['state_id'],name=i['zone_name'])
                zone.save()
            except:
                pass
        elif not Zone.objects.filter(Q(zone_id =i["id"]) & Q(name=i['zone_name'])).exists():
            try:
                Zone.objects.update_or_create(zone_id =i["id"],state_id=i['state_id'],name=i['zone_name'])
            except:
                pass
        else:
            pass
    context= {"message":"task over"}
    return Response(context, status=status.HTTP_200_OK)
 

# #Mew one 
# @api_view(['GET'])
# @permission_classes([IsAuthenticated])
# def get_zones_from_scts_school_api(request):

   
#     url = 'http://192.168.0.1/sctsadmissions/asset_zone_api.php?token=chaitanya'
#     try:
#         building_category_id = 1 
#         building_category = BuildingCategory.objects.get(building_category_id = building_category_id  )

#         response = requests.get(url)
#         response.raise_for_status()  # Will raise an HTTPError if the status is 4xx/5xx
#         data = response.json().get('data', [])

#         if not data:
#             return Response({"message": "No data found"}, status=status.HTTP_204_NO_CONTENT)
        
#         for item in data:
#             external_zone_id = item.get('id')
#             zone_name = item.get('zone_name')
#             state_external_id = item.get('state_id')

#             # Fetch the associated state with the external_state_id and category filter
#             state = State.objects.filter(Q(external_state_id=state_external_id) & Q(building_category_id = building_category_id)).first()

#             if external_zone_id and zone_name and state:

#                 existing_zone = Zone.objects.filter(Q(external_zone_id=external_zone_id) & Q(building_category_id = building_category_id)).first()

#                 if existing_zone:
#                     # If zone name differs, update it
#                     if existing_zone.name != zone_name:
#                         existing_zone.name = zone_name
#                         existing_zone.state=state
#                         existing_zone.save()
#                         print(f"Updated zone: {zone_name} (ID: {external_zone_id})")
#                     else:
#                         print(f"Duplicate zone found, skipping: {zone_name} (ID: {external_zone_id})")
#                 else:
#                     # Create a new zone if not already existing
#                     Zone.objects.create(
#                         external_zone_id=external_zone_id,
#                         name=zone_name,
#                         state=state,
#                         building_category=building_category,
#                         is_active=True
#                     )
#                     print(f"Created new zone: {zone_name} (ID: {external_zone_id})")

#         return Response({"message": "Task completed successfully"}, status=status.HTTP_200_OK)

#     except BuildingCategory.DoesNotExist:
#         return Response({"error": "Building Category not found"}, status=status.HTTP_404_NOT_FOUND)

#     except requests.HTTPError as http_err:
#         return Response({"error": f"HTTP error occurred: {http_err}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#     except json.JSONDecodeError as json_err:
#         return Response({"error": f"Error decoding JSON: {json_err}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#     except Exception as e:
#         return Response({"error": f"An unexpected error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



# # ================================================================= SCTS  Branches ======================================================
 

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_branches_varna(request):
    url = "http://192.168.0.1/sctsadmissions/asset_branch_api.php?token=chaitanya"
    response = requests.get(url)
    data = response.json()['data']
    errors = []

    for item in data:
        if Branch.objects.filter(branch_id=item['id']).exists():
            try:
                branch = Branch(
                    # branch_id=item["id"],
                    state=State.objects.get(state_id=item['state_id']),
                    zone=Zone.objects.get(zone_id=item['zone_id']),
                    name=item['branch_name'],
                    building_code=item['building_code'],
                    location_incharge=item['principal_name'],
                    email=item['branch_mailid'],
                    phonenumber=item['principal_phno'],
                    city=item['city'],
                    address=item['address'],
                    is_active=item['active_status'],
                )
                branch.save()
            except Exception as e:
                # pass
                errors.append(f"Error updating branch ID {item['id']}: {str(e)}")
        elif not Branch.objects.filter(Q(branch_id=item["id"]) or Q(name = item['branch_name'])).exists():
            try:
                Branch.objects.update_or_create(
                    branch_id=item["id"],
                    defaults={
                        # 'state' : item['state_id'],
                        # 'zone': item['zone_id'],
                        'state': State.objects.get(state_id=item['state_id']),
                        'zone': Zone.objects.get(zone_id=item['zone_id']),
                        'name': item['branch_name'],
                        'building_code': item['building_code'],
                        'location_incharge': item['principal_name'],
                        'email': item['branch_mailid'],
                        'phonenumber': item['principal_phno'],
                        'city': item['city'],
                        'address': item['address'],
                        'is_active': item['active_status'],
                    }
                )
            except Exception as e:
                # pass
                errors.append(f"Error creating branch ID 2 {item['id']}: {str(e)}")
        else:
            # pass
            errors.append(f"Unhandled branch ID {item['id']}")

    # if errors:
    
        # return Response({'message': 'Errors occurred', 'errors': errors}, status=status.HTTP_400_BAD_REQUEST)
    return Response({'message': 'Task completed successfully'}, status=status.HTTP_200_OK)

 

# # NEW ONE 
# @api_view(['GET'])
# @permission_classes([IsAuthenticated])
# def get_branches_from_scts_school_api(request):

#     url = 'http://192.168.0.1/sctsadmissions/asset_branch_api.php?token=chaitanya'
#     try:
#         building_category_id =  1
#         building_category = BuildingCategory.objects.get(building_category_id = building_category_id)

         
     
#         response = requests.get(url)     
#         response.raise_for_status()   
#         data = response.json().get('data', [])

#         if not data:
#             return Response({"message": "No data found"}, status=status.HTTP_204_NO_CONTENT)

#         for item in data:
#             external_building_id = item.get('id')
#             external_state_id = item.get('state_id')
#             external_zone_id = item.get('zone_id')
#             branch_name = item.get('branch_name')
#             building_code = item.get('building_code')
#             incharge_name = item.get('principal_name')
#             incharge_phno = item.get('principal_phno')
#             incharge_email = item.get('principal_mailid')
#             # building_email = item.get('branch_mailid')
#             address = item.get('address')
#             city = item.get('city')
#             # active_status = item.get('active_status')
#             # los_id        = item.get('los_id')
#             # head_id        = item.get('head_id')
#             # fusion_building_code = item.get('fusion_building_code')
#             # agm_name        = item.get('agm_name')
#             # ri_name       = item.get('ri_name')
#             # board       = item.get('board')
#             # branch_type       = item.get('branch_type')

 
#             # Fetch the associated state and zone
#             state = State.objects.filter(Q(external_state_id=external_state_id) & Q(building_category_id = building_category_id)).first()
#             zone = Zone.objects.filter(Q(external_zone_id=external_zone_id) & Q(building_category_id = building_category_id)).first()

            
#             if external_building_id and state and zone:
#                 existing_building = Branch.objects.filter(Q(external_building_id=external_building_id) & Q(building_category_id = building_category_id)).first()
#                 try:
#                     if existing_building:
#                         # Update existing building details
#                         existing_building.name = branch_name
#                         existing_building.location_incharge = incharge_name
#                         existing_building.phonenumber = incharge_phno
#                         existing_building.email = incharge_email
#                         existing_building.building_code = building_code
#                         existing_building.city = city
#                         existing_building.address = address                 
#                         existing_building.state =  state
#                         existing_building.zone  =   zone
#                         existing_building.save()
                    
#                         print(f"Updated building: {branch_name} (ID: {external_building_id})")
#                     else:
#                         # Create a new building entry

#                         new_building = Branch.objects.create(
#                                                             external_building_id=external_building_id,
#                                                             state=state,
#                                                             zone=zone,
#                                                             building_category=building_category,
#                                                             name=branch_name,
#                                                             location_incharge = incharge_name,
#                                                             phonenumber =incharge_phno,
#                                                             email=incharge_email,
#                                                             building_code=building_code,
#                                                             city=city,
#                                                             address=address,
#                                                             is_active=True,
#                                                         )
#                         # new_building.entities.set(entities)
#                         print(f"Created new building: {branch_name} (ID: {external_building_id})")
#                 except:
#                     pass

#         return Response({"message": "Task completed successfully"}, status=status.HTTP_200_OK)

#     except BuildingCategory.DoesNotExist:
#         return Response({"error": "Building Category not found"}, status=status.HTTP_404_NOT_FOUND)

#     except requests.HTTPError as http_err:
#         return Response({"error": f"HTTP error occurred: {http_err}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#     except json.JSONDecodeError as json_err:
#         return Response({"error": f"Error decoding JSON: {json_err}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#     except Exception as e:
#         return Response({"error": f"An unexpected error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



# #====================================================================  Academic Year    ===================================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_academic_years(request):
    url = "http://192.168.0.6/varna_api/academic_year.php?token=chaitanya"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        if not data:
            return Response({"message": "No data found"}, status=status.HTTP_204_NO_CONTENT)

        updated_count = 0
        created_count = 0

        with transaction.atomic():
            for item in data:
                academic_year_id = item.get('id')
                start_date = item.get('start_date')
                end_date = item.get('end_date')
                name = item.get('academic_year_name')
                is_active = True if item.get('active_status') == "1" else False

                if academic_year_id and name:
                    try:
                        # Parse dates if they exist
                        start_date = datetime.strptime(start_date, '%Y-%m-%d').date() if start_date else None
                        end_date = datetime.strptime(end_date, '%Y-%m-%d').date() if end_date else None

                        # Get or create the AcademicYear
                        academic_year, created = AcademicYear.objects.get_or_create(
                            academic_year_id=academic_year_id,
                            defaults={
                                'start_date': start_date,
                                'end_date': end_date,
                                'name': name,
                                'is_active': is_active,
                            },
                        )
                        if not created:
                            # Update existing record if necessary
                            academic_year.start_date = start_date
                            academic_year.end_date = end_date
                            academic_year.name = name
                            academic_year.is_active = is_active
                            academic_year.save()
                            updated_count += 1
                        else:
                            created_count += 1
                    except Exception as e:
                        print(f"Error processing Academic Year ID {academic_year_id}: {e}")

        return Response({
            "message": "Task completed successfully",
            "updated_count": updated_count,
            "created_count": created_count,
        }, status=status.HTTP_200_OK)

    except requests.RequestException as e:
        return Response({"error": f"Failed to fetch data from external API: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception as e:
        return Response({"error": f"An unexpected error occurred: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



# #=======================================  Orientation   =============================================================================



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_orientations_varna_api(request):
    url = "http://192.168.0.6/varna_api/orientation.php?token=chaitanya"
    
    try:
        response = requests.get(url,timeout=20)
        response.raise_for_status()
        data = response.json()

        if not data:
            return Response({"message": "No data found"}, status=status.HTTP_204_NO_CONTENT)

        created_count = 0
        updated_count = 0

        for item in data:
            varna_orientation_id = item.get('id')
            name = item.get('orientation_name')
            short_code = item.get('short_code')
            is_active = item.get('active_status') == "1"

            if varna_orientation_id and name:
                try:
                    obj, created = Orientation.objects.update_or_create(
                        varna_orientation_id=varna_orientation_id,
                        defaults={
                            "name": name,
                            "short_code": short_code,
                            "is_active": is_active,
                        }
                    )
                    if created:
                        created_count += 1
                        logger.info(f"Created new Orientation: {name} (ID: {varna_orientation_id})")
                    else:
                        updated_count += 1
                        logger.info(f"Updated Orientation: {name} (ID: {varna_orientation_id})")
                except IntegrityError as e:
                    logger.error(f"Database error for Orientation ID {varna_orientation_id}: {e}")
                except Exception as e:
                    logger.error(f"Unexpected error for Orientation ID {varna_orientation_id}: {e}")

        message = f"Task completed successfully. Created: {created_count}, Updated: {updated_count}"
        return Response({"message": message}, status=status.HTTP_200_OK)

    except requests.exceptions.RequestException as e:
        logger.error(f"Request error: {e}")
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



# # # Orientations
# # @api_view(['GET'])
# # @permission_classes([IsAuthenticated])
# # def get_orientations_school_api(request):
# #     url = "http://192.168.0.6/varna_api/orientation.php?token=chaitanya"

# #     try:
        
# #         response = requests.get(url)
# #         response.raise_for_status()
# #         data = response.json()
# #         # data = response.json().get('data', [])

# #         if not data:
# #             return Response({"message": "No data found"}, status=status.HTTP_204_NO_CONTENT)

# #         # Process state data directly within the view
# #         for item in data:    
# #             varna_orientation_id = item.get('id')
# #             name = item.get('orientation_name')
# #             short_code = item.get('short_code')
# #             is_active = True if item.get('active_status') == "1" else False
            
# #             if varna_orientation_id and name:
# #                 existing_orientation = Orientation.objects.get(varna_orientation_id = varna_orientation_id)
# #                 if existing_orientation:
# #                     existing_orientation.name = name
# #                     existing_orientation.short_code = short_code
# #                     existing_orientation.is_active = is_active
# #                     existing_orientation.save()
# #                     print(f"Updated Orientation: {name} (ID: {varna_orientation_id})")
# #                 else:
# #                     try:
# #                         Orientation.objects.create(
# #                             varna_orientation_id = varna_orientation_id,
# #                             name=name,
# #                             short_code=short_code,   
# #                             is_active = is_active,
# #                         )
# #                         print(f"Created new Orientation: {name} (ID: {varna_orientation_id})")
# #                     except Exception as e:
# #                         pass
# #                         # print(f"Error creating Department {name} (ID: {external_id}): {e}")

# #         return Response({"message": "Task completed successfully"}, status=status.HTTP_200_OK)
    
# #     except requests.exceptions.RequestException as e:
# #         return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
 


# #=========================================  Class Names     ====================================================

 

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_class_names_school_api(request):
    url = "http://192.168.0.6/varna_api/class.php?token=chaitanya"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        if not data:
            return Response({"message": "No data found"}, status=status.HTTP_204_NO_CONTENT)

        # Prepare for batch updates/creates
        to_create = []
        for item in data:
            varna_class_id = item.get('id')
            name = item.get('class_name')

            if varna_class_id and name:
                # Update or create the ClassName object
                obj, created = ClassName.objects.update_or_create(
                    varna_class_id=varna_class_id,
                    defaults={
                        "name": name,
                        "is_active": True,
                    },
                )
                action = "Created" if created else "Updated"
                print(f"{action} Class Name: {name} (ID: {varna_class_id})")

        return Response({"message": "Task completed successfully"}, status=status.HTTP_200_OK)

    except requests.exceptions.RequestException as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    except Exception as e:
        return Response({"error": f"An unexpected error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



# # @api_view(['GET'])
# # @permission_classes([IsAuthenticated])
# # def get_class_names_school_api(request):

# #     url = "http://192.168.0.6/varna_api/class.php?token=chaitanya"
# #     try:
# #         response = requests.get(url)
# #         response.raise_for_status()
# #         data = response.json()

# #         if not data:
# #             return Response({"message": "No data found"}, status=status.HTTP_204_NO_CONTENT)

# #         # Process state data directly within the view
# #         for item in data:    
# #             varna_class_id = item.get('id')
# #             name  = item.get('class_name') 

# #             if varna_class_id and name:
# #                 existing_class_name = ClassName.objects.get(varna_class_id  = varna_class_id)
# #                 if existing_class_name:
# #                     existing_class_name.name = name                   
# #                     existing_class_name.save() 

# #                     print(f"Updated Class Name: {name} (ID: {varna_class_id})")
                    
# #                 else:
# #                     try:
# #                         ClassName.objects.create(
# #                            varna_class_id = varna_class_id,
# #                             name=name,
# #                             is_active=True
# #                         )
# #                         print(f"Created new Class Name: {name} (ID: {varna_class_id})")
# #                     except Exception as e:
# #                         print(f"Error creating Class Name {name} (ID: {varna_class_id}): {e}")

# #         return Response({"message": "Task completed successfully"}, status=status.HTTP_200_OK)
    
# #     except requests.exceptions.RequestException as e:
# #         return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# from callhub.tasks import *
# from django.shortcuts import render
# from django.http import HttpResponse

# def test(request):
#     test_func.delay()
#     return HttpResponse("Done")



# #============================================== Sections ====================================================================

# #========================================================= Sections ==================================================

import requests
from django.shortcuts import get_object_or_404

def process_sections_for_branch(branch_id):
    try:
        # Retrieve branch object
        branch = Branch.objects.filter(branch_id = branch_id).first()
        if not branch:
            return {"error": f"Branch with ID {branch_id} not found"}
        current_academic_year =  AcademicYear.objects.filter(is_current_academic_year = True , is_active = True).first()
        if not current_academic_year:
             return {"error": f"Current Academic Year Not Fount"}
        academic_year_name = current_academic_year.name
 
        # API request
        # url = f"http://192.168.0.6/varna_api/section.php?token=chaitanya&academic_year={academic_year_name}&branch_id={branch_id}"
        
        #this api with Student Count
        url = f"http://192.168.0.6/varna_api/section_std_count.php/?token=chaitanya&academic_year={academic_year_name}&branch_id={branch_id}"
        response = requests.get(url,timeout=10)
        response.raise_for_status()  # This will raise an exception for 4xx/5xx responses
        data = response.json()
      
        if not data:
            return {"message": f"No data found for branch ID {branch_id}"}

        for item in data:
            varna_section_id = item.get('id')
            academic_year_id = item.get('academic_year_id')
            class_name_id = item.get('class_id')
            section_name = item.get('section_name')
            
            is_active = True if item.get('active_status') == "1" else False
            orientation_id = item.get('orientation')
            student_count_str = item.get("student_count", "0")

            try:
                student_count = int(student_count_str)
            except (TypeError, ValueError):
                student_count = 0

            has_students = student_count > 0

            # Fetch related objects, handle missing ones gracefully
            academic_year = AcademicYear.objects.filter(academic_year_id=academic_year_id).first()
            class_name = ClassName.objects.filter(varna_class_id=class_name_id).first()
            orientation = Orientation.objects.filter(varna_orientation_id=orientation_id).first()

            if not (academic_year and class_name and orientation and varna_section_id and section_name):
                continue  # Skip if required fields are missing or invalid

            # Update or create section
            existing_section = Section.objects.filter(varna_section_id = varna_section_id).first()
            if existing_section:
                existing_section.name = section_name
                existing_section.is_active = is_active
                existing_section.orientation = orientation
                existing_section.class_name = class_name
                existing_section.branch = branch
                existing_section.academic_year = academic_year
                existing_section.has_students = has_students
                existing_section.strength = student_count
                existing_section.save()
            else:
                Section.objects.create(
                    varna_section_id = varna_section_id,
                    academic_year=academic_year,
                    branch=branch,
                    class_name=class_name,
                    orientation=orientation,
                    name=section_name,
                    strength=student_count,
                    has_students = has_students,
                    is_active = is_active
                )

        return {"message": f"Processed sections for branch ID {branch_id}"}

    except requests.exceptions.RequestException as e:
        return {"error": f"Request error: {str(e)}"}
    except Exception as e:
        return {"error": f"An unexpected error occurred: {str(e)}"}





@api_view(['GET'])
@permission_classes([IsAuthenticated])
def trigger_process_all_branches_sections(request):
    process_all_branches_sections.delay()  # Trigger the Celery task asynchronously
    return Response({"message": "Processing of all branches started."}, status=202)


# #=======================================================================================================================================================================
# #==============================================================     Students    ========================================================================================
# #=======================================================================================================================================================================

def process_students_for_branch(branch_id):
    try:
        # Retrieve branch object
        branch = Branch.objects.filter(branch_id = branch_id).first()
        if not branch:
            return {"error": f"Branch with ID {branch_id} not found"}

        current_academic_year =  AcademicYear.objects.filter(is_current_academic_year = True , is_active = True).first()
        if not current_academic_year:
             return {"error": f"Current Academic Year Not Fount"}
        AcademicYearId = current_academic_year.academic_year_id

        # print("AcademicYearId :",AcademicYearId)

        # API request
        url = f"http://192.168.0.6/varna_api/student_master_data.php?token=chaitanya&academic_year_id={AcademicYearId}&branch_id={branch_id}"

        response = requests.get(url,timeout=30)
        response.raise_for_status()  # This will raise an exception for 4xx/5xx responses
        data = response.json()

        # print("Date :",data)

        if not data:
            return {"message": f"No data found for branch ID {branch_id}"}

        for item in data:
            varna_student_id = item.get('student_id')
            academic_year_id = item.get('acadecmic_year_id')
            SCS_Number = item.get('admission_number')
            name = item.get('student_name')
            student_class_id = item.get('class_id')
            orientation_id = item.get('orientation_id')
            # previous_orientation_id = item.get('previous_orientation_id')
            # student_type_id = item.get('student_type_id')
            section_id = item.get('section_id')
            gender = Gender.objects.filter(name__iexact=item.get('gender', '').strip()).first()
            admission_status  = AdmissionStatus.objects.filter(short_code__iexact=item.get('student_status', '').strip()).first()
             
            # is_active = True if item.get('active_status') == "1" else False
            

            # Fetch related objects, handle missing ones gracefully
            academic_year = AcademicYear.objects.filter(academic_year_id = academic_year_id).first()
            student_class = ClassName.objects.filter(varna_class_id = student_class_id).first()
            orientation = Orientation.objects.filter(varna_orientation_id = orientation_id).first()
            section = Section.objects.filter(varna_section_id = section_id ).first()

            # previous_orientation = Orientation.objects.filter(varna_orientation_id = previous_orientation_id).first()

            if not (academic_year and student_class and orientation and section):
                continue  # Skip if required fields are missing or invalid

            # Update or create section
            existing_student = Student.objects.filter(Q(varna_student_id = varna_student_id) & Q(SCS_Number = SCS_Number)).first()
            if existing_student:
                existing_student.academic_year = academic_year 
                existing_student.name = name
                existing_student.student_class = student_class
                existing_student.orientation = orientation
                existing_student.section = section
                existing_student.branch =branch
                existing_student.gender = gender
                existing_student.admission_status = admission_status
                # existing_student.previous_orientation = previous_orientation
                existing_student.save()
            else:
                Student.objects.create(
                    varna_student_id = varna_student_id,
                    academic_year = academic_year ,
                    SCS_Number = SCS_Number,
                    name = name,
                    branch = branch,
                    orientation = orientation,
                    student_class = student_class,
                    section = section,    
                    gender = gender,
                    admission_status = admission_status,
                    # previous_orientation = previous_orientation,
                    is_active = True,
                )

        return {"message": f"Processed students for branch ID {branch_id}"}

    except requests.exceptions.RequestException as e:
        return {"error": f"Request error: {str(e)}"}
    except Exception as e:
        return {"error": f"An unexpected error occurred: {str(e)}"}
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def trigger_process_all_branches_students(request):
    process_all_branches_students.delay()  # Trigger the Celery task asynchronously
    return Response({"message": "Processing of all branches started."}, status=202)



# #  TESTING 

# # @api_view(['GET'])
# # @permission_classes([IsAuthenticated])
# # def process_sections_api(request, branch_id):
# #     try:
# #         result = process_students_for_branch(branch_id)
# #         return Response({"message": result}, status=status.HTTP_200_OK)
# #     except Exception as e:
# #         return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# #======================================================    DEPARTMENTS  ====================================================================================
# # @api_view(['GET'])
# # @permission_classes([IsAuthenticated])
# # def get_departments_from_varna(request):
# #     result = sync_departments_from_varna()
# #     return Response({"message": result}, status=status.HTTP_200_OK)



# def convert_active_status(active_status):
#     return True if active_status == "1" else False

# # departments old one 
# # @api_view(['GET'])
# # @permission_classes([IsAuthenticated])
# # def get_departments_from_varna(request):
# #     url = "http://192.168.0.6/varna_api/staff_department.php?token=chaitanya"

# #     try:
# #         response = requests.get(url,timeout=30)
# #         response.raise_for_status()
# #         data = response.json()

# #         if not data:
# #             return Response({"message": "No data found"}, status=status.HTTP_204_NO_CONTENT)

# #         for item in data:
# #             department_id = item.get('id')
# #             name = item.get('name')
# #             division_id = item.get('division_id')
# #             active_status = item.get('active_status')

# #             if department_id and name:
# #                 # Use get_or_create to simplify logic and avoid checking existence manually
# #                 department, created = Department.objects.update_or_create(
# #                     department_id=department_id,
# #                     defaults={
# #                         'name': name,
# #                         'division_id': division_id,
# #                         'is_active': convert_active_status(active_status),
# #                     }
# #                 )

# #                 if created:
# #                     logger.info(f"Created new Department: {name} (ID: {department_id})")
# #                 else:
# #                     logger.info(f"Updated Department: {name} (ID: {department_id})")

# #         return Response({"message": "Task completed successfully"}, status=status.HTTP_200_OK)

# #     except requests.exceptions.RequestException as e:
# #         logger.error(f"Error fetching data: {e}")
# #         return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
# #     except Exception as e:
# #         logger.error(f"Unexpected error: {e}")
# #         return Response({"error": "An unexpected error occurred."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# # @api_view(['GET'])
# # @permission_classes([IsAuthenticated])
# # def get_departments_api(request):
# #     url = "http://192.168.0.6/varna_api/staff_department.php?token=chaitanya"

# #     try:
# #         response = requests.get(url)
# #         response.raise_for_status()
# #         data = response.json()
# #         # data = response.json().get('data', [])

# #         if not data:
# #             return Response({"message": "No data found"}, status=status.HTTP_204_NO_CONTENT)

# #         # Process state data directly within the view
# #         for item in data:    
# #             department_id = item.get('id')
# #             name = item.get('name')
# #             division_id = item.get('division_id')
# #             active_status = item.get('active_status')
            
# #             if department_id and name:
# #                 existing_department = Department.objects.filter(Q(department_id = department_id)).first()
# #                 if existing_department:
# #                     existing_department.name = name
# #                     existing_department.division_id = division_id
# #                     existing_department.is_active = True if active_status == "1" else False
# #                     existing_department.save()
# #                     # print(f"Updated department: {name} (ID: {external_id})")
                    
# #                 else:
# #                     try:
# #                         Department.objects.create(
# #                             department_id = department_id,
# #                             name=name,
# #                             division_id = division_id,
# #                             is_active = True if active_status == "1" else False
# #                         )
# #                         # print(f"Created new Department: {name} (ID: {external_id})")
# #                     except Exception as e:
# #                         pass
# #                         # print(f"Error creating Department {name} (ID: {external_id}): {e}")

# #         return Response({"message": "Task completed successfully"}, status=status.HTTP_200_OK)

# #     except requests.exceptions.RequestException as e:
# #         return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
# #     except Exception as e:
# #         logger.error(f"Unexpected error: {e}")
# #         return Response({"error": "An unexpected error occurred."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# # DEPARTMENTS New one 
# @api_view(['GET'])
# @permission_classes([IsAuthenticated])
# def get_departments_from_scts_school_api(request):
#     url = "http://192.168.0.6/varna_api/staff_department.php?token=chaitanya"

#     try:
#         building_category_id = 1
#         building_category = BuildingCategory.objects.get(building_category_id = building_category_id)

#         response = requests.get(url)
#         response.raise_for_status()
#         data = response.json()
#         # data = response.json().get('data', [])

#         if not data:
#             return Response({"message": "No data found"}, status=status.HTTP_204_NO_CONTENT)

#         # Process state data directly within the view
#         for item in data:    
#             external_id = item.get('id')
#             name = item.get('name')
#             division_id = item.get('division_id')
#             active_status = item.get('active_status')
            

#             if external_id and name:
#                 existing_department = Department.objects.filter(Q(external_id=external_id) & Q(building_category_id = building_category_id)).first()
#                 if existing_department:
#                     existing_department.name = name
#                     existing_department.is_active = True if active_status == "1" else False
#                     existing_department.division_id = division_id
#                     existing_department.save()
#                     # print(f"Updated department: {name} (ID: {external_id})")
                    
#                 else:
#                     try:
#                         Department.objects.create(
#                             external_id=external_id,
#                             name=name,
#                             building_category=building_category,
#                             division_id = division_id,
#                             is_active = True if active_status == "1" else False
#                         )
#                         # print(f"Created new Department: {name} (ID: {external_id})")
#                     except Exception as e:
#                         pass
#                         # print(f"Error creating Department {name} (ID: {external_id}): {e}")

#         return Response({"message": "Task completed successfully"}, status=status.HTTP_200_OK)

#     except BuildingCategory.DoesNotExist:
#         return Response({"error": "BuildingCategory with ID 2 not found"}, status=status.HTTP_404_NOT_FOUND)

#     except requests.exceptions.RequestException as e:
#         return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

# #==========================================================  DESIGNATIONS   ========================================================================================================

# # @api_view(['GET'])
# # @permission_classes([IsAuthenticated])
# # def get_designation_from_varna(request):
# #     result = sync_designations_from_varna()
# #     return Response({"message": result}, status=status.HTTP_200_OK)

# #==========================================================      old one    =========================================================================================
# # @api_view(['GET'])
# # @permission_classes([IsAuthenticated])
# # def get_designation_from_varna(request):
# #     url = "http://192.168.0.6/varna_api/staff_designations.php?token=chaitanya"
    
# #     try:
# #         response = requests.get(url, timeout=20)
# #         response.raise_for_status()
# #         data = response.json()

# #         if not data:
# #             return Response({"message": "No data found"}, status=status.HTTP_204_NO_CONTENT)
# #         for item in data:    
# #             designation_id = item.get('id')
# #             short_code = item.get('short_code')
# #             name = item.get('designation')
# #             division_id = item.get('division_id')
# #             departments_id = item.get('departments_id')            
# #             active_status = item.get('active_status')

# #             if not designation_id or not name:
# #                 continue   
# #             department = Department.objects.filter(department_id=departments_id).first()
# #             existing_designation = Designation.objects.filter(designation_id=designation_id).first()
# #             if existing_designation:
# #                 existing_designation.name = name
# #                 existing_designation.department = department
# #                 existing_designation.short_code = short_code
# #                 existing_designation.division_id = division_id
# #                 existing_designation.is_active = True if active_status == "1" else False
# #                 existing_designation.save()
# #             else:
# #                 try:
# #                     Designation.objects.create(
# #                         designation_id=designation_id,
# #                         name=name,
# #                         department=department,
# #                         division_id=division_id,
# #                         short_code=short_code,
# #                         is_active=True if active_status == "1" else False
# #                     )
# #                 except:
# #                     continue       # pass or continue      
# #         return Response({"message": "Task completed successfully"}, status=status.HTTP_200_OK)

# #     except requests.exceptions.RequestException as e:
# #         return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# #==================================================================     NEW ONE  =================================================================================

# # DESIGNATIONS
# @api_view(['GET'])
# @permission_classes([IsAuthenticated])
# def get_designation_from_scts_school_api(request):
#     url = "http://192.168.0.6/varna_api/staff_designations.php?token=chaitanya"

#     try:
#         building_category_id = 1
#         building_category = BuildingCategory.objects.get(building_category_id = building_category_id)
#         response = requests.get(url)
#         response.raise_for_status()
#         data = response.json()
#         # data = response.json().get('data', [])

#         if not data:
#             return Response({"message": "No data found"}, status=status.HTTP_204_NO_CONTENT)

#         # Process state data directly within the view
#         for item in data:    
#             external_id = item.get('id')
#             name = item.get('designation')
#             departments_id = item.get('departments_id')
#             short_code = item.get('short_code')
#             active_status = item.get('active_status')
#             division_id = item.get('division_id')
            
#             department = Department.objects.filter(Q(external_id = departments_id) & Q(building_category_id = building_category_id)).first()

#             if external_id and name:
#                 existing_designation = Designation.objects.filter(Q(external_id = external_id) & Q(building_category_id = building_category_id)).first()
#                 if existing_designation:
#                     existing_designation.name = name
#                     existing_designation.department = department
#                     existing_designation.short_code = short_code
#                     existing_designation.is_active = True if active_status == "1" else False
#                     existing_designation.division_id = division_id
#                     existing_designation.save()
#                     print(f"Updated designation: {name} (ID: {external_id})")
                    
#                 else:
#                     try:
#                         Designation.objects.create(
#                             external_id=external_id,
#                             name=name,
#                             building_category=building_category,
#                             department = department,
#                             short_code =  short_code,
#                             division_id=division_id,
#                             is_active = True if active_status == "1" else False
                            
#                         )
#                         print(f"Created new designation: {name} (ID: {external_id})")
#                     except Exception as e:
#                         pass
#                         print(f"Error creating designation {name} (ID: {external_id}): {e}")

#         return Response({"message": "Task completed successfully"}, status=status.HTTP_200_OK)

#     except BuildingCategory.DoesNotExist:
#         return Response({"error": "BuildingCategory with ID 2 not found"}, status=status.HTTP_404_NOT_FOUND)

#     except requests.exceptions.RequestException as e:
#         return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# # @api_view(['GET'])
# # @permission_classes([IsAuthenticated])
# # def get_designation_from_varna(request):
# #     url = "http://192.168.0.6/varna_api/staff_designations.php?token=chaitanya"
# #     try:
# #         response = requests.get(url,timeout=20)
# #         response.raise_for_status()
# #         data = response.json()

# #         if not data:
# #             return Response({"message": "No data found"}, status=status.HTTP_204_NO_CONTENT)

# #         # Process state data directly within the view
# #         for item in data:    
# #             designation_id = item.get('id')
# #             short_code = item.get('short_code')
# #             name = item.get('designation')
# #             division_id = item.get('division_id')
# #             departments_id = item.get('departments_id')            
# #             active_status = item.get('active_status')
            
# #             department = Department.objects.get(department_id = departments_id)

# #             if designation_id and name:
# #                 existing_designation = Designation.objects.get(designation_id = designation_id)
# #                 if existing_designation:
# #                     existing_designation.name = name
# #                     existing_designation.department = department
# #                     existing_designation.short_code = short_code
# #                     existing_designation.division_id = division_id
# #                     existing_designation.is_active = True if active_status == "1" else False
# #                     existing_designation.save()
# #                     # print(f"Updated department: {name} (ID: {external_id})")
                    
# #                 else:
# #                     try:
# #                         Designation.objects.create(
# #                             designation_id = designation_id,
# #                             name=name,
# #                             department = department,
# #                             division_id = division_id,
# #                             short_code =  short_code,
# #                             is_active = True if active_status == "1" else False
# #                         )
# #                     except Exception as e:
# #                         pass
                        
# #         return Response({"message": "Task completed successfully"}, status=status.HTTP_200_OK)
# #     except requests.exceptions.RequestException as e:
# #         return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# #=======================================================   Get Single Branch  Employees     ===========================================================================================



# # @api_view(['GET'])
# # @permission_classes([IsAuthenticated])
# # def get_scts_teachers_from_varna(request, branch_id=None):
# #     if not branch_id:
# #         return Response({"message": "No Branch ID"}, status=status.HTTP_204_NO_CONTENT)

# #     url = f"http://192.168.0.6/varna_api/employee_master.php?token=chaitanya&branch_id={branch_id}"

# #     try:
# #         branch = Branch.objects.get(branch_id=branch_id)
# #         response = requests.get(url)
# #         response.raise_for_status()
# #         data = response.json()

# #         if not data:
# #             return Response({"message": "No data found"}, status=status.HTTP_204_NO_CONTENT)

# #         for item in data:
# #             try:
# #                 teacher_id = item.get('id')
# #                 full_name = item.get('employee_name')
# #                 employee_id = item.get('employee_id')
# #                 employee_code = item.get('employee_code')
# #                 designation_id = item.get('designation_id')
# #                 departments_id = item.get('departments_id')
# #                 qualification = item.get('qualification')
# #                 joining_date = item.get('joining_date')
# #                 gender_str = item.get('gender', '').lower()
# #                 employee_status_id = item.get('employee_status_id')

# #                 if not (teacher_id and full_name):
# #                     continue

# #                 gender_id = 1 if gender_str == 'male' else 2 if gender_str == 'female' else 3
# #                 gender = Gender.objects.filter(gender_id=gender_id).first()
# #                 department = Department.objects.filter(department_id=departments_id).first()
# #                 designation = Designation.objects.filter(designation_id=designation_id).first()

# #                 teacher = Teacher.objects.filter(teacher_id=teacher_id).first()

# #                 if teacher:
# #                     teacher.branch = branch
# #                     teacher.employee_id = employee_id
# #                     teacher.employee_code = employee_code
# #                     teacher.full_name = full_name
# #                     teacher.designation = designation
# #                     teacher.department = department
# #                     teacher.qualification = qualification
# #                     teacher.date_of_joining = joining_date
# #                     teacher.gender = gender
# #                     teacher.employee_status_id = employee_status_id
# #                     teacher.is_active = True if employee_status_id == "EX" else False
# #                     teacher.save()
# #                 else:
# #                     Teacher.objects.create(
# #                         teacher_id=teacher_id,
# #                         branch=branch,
# #                         employee_id=employee_id,
# #                         employee_code=employee_code,
# #                         full_name=full_name,
# #                         designation=designation,
# #                         department=department,
# #                         qualification=qualification,
# #                         date_of_joining=joining_date,
# #                         gender=gender,
# #                         employee_status_id=employee_status_id,
# #                         is_active=True if employee_status_id == "EX" else False
# #                     )

# #             except Exception as inner_error:
# #                 print(f"Error processing teacher {teacher_id}: {inner_error}")

# #         return Response({"message": "Task completed successfully"}, status=status.HTTP_200_OK)

# #     except Branch.DoesNotExist:
# #         return Response({"error": "Branch not found"}, status=status.HTTP_404_NOT_FOUND)
# #     except requests.exceptions.RequestException as e:
# #         return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# # ====================================================================== Get All branches Employees  ========================================================
 
# @api_view(['GET'])   
# @permission_classes([IsAuthenticated])
# def trigger_all_scts_branches_teacher_sync(request):
#     sync_scts_teachers_for_all_branches.delay()
#     return Response({"message": "Teacher sync task for all branches has started."}, status=status.HTTP_202_ACCEPTED)

# @api_view(['GET'])   
# @permission_classes([IsAuthenticated])
# def trigger_all_telangana_branches_teacher_sync(request):
#     sync_telangana_teachers_for_all_branches.delay()
#     return Response({"message": "Teacher sync task for all branches has started."}, status=status.HTTP_202_ACCEPTED)


# #===========================================================================================================================================================================================================
# #==============================================================================     ETS School Data sync start   =================================================================================================
# #============================================================================================================================================================================================================

# # States

# @api_view(['GET'])
# @permission_classes([IsAuthenticated])
# def get_states_from_telangana_school_api(request):
   
#     url = 'http://10.100.100.21/tsctsadmissions/asset_state_api.php?token=chaitanya'
#     try:
#         building_category_id = 2 

#         building_category = BuildingCategory.objects.get(building_category_id = building_category_id)

#         response = requests.get(url)
#         response.raise_for_status()
#         data = response.json()['data']

#         if not data:
#             return Response({"message": "No data found"}, status=status.HTTP_204_NO_CONTENT)

#         # Process state data directly within the view
#         for item in data:     

#             external_state_id = item.get('id')
#             state_name = item.get('state_name')

#             if external_state_id and state_name:
#                 existing_state = State.objects.filter(Q(external_state_id=external_state_id) & Q(building_category_id = building_category_id)).first()
#                 if existing_state:
#                     if existing_state.name != state_name:
#                         existing_state.name = state_name
#                         existing_state.save()
#                         print(f"Updated state: {state_name} (ID: {external_state_id})")
#                     else:
#                         print(f"Duplicate state found, skipping: {state_name} (ID: {external_state_id})")
#                 else:
#                     try:
#                         State.objects.create(
#                             external_state_id=external_state_id,
#                             name=state_name,
#                             building_category=building_category,
#                             is_active=True
#                         )
#                         print(f"Created new state: {state_name} (ID: {external_state_id})")
#                     except Exception as e:
#                         print(f"Error creating state {state_name} (ID: {external_state_id}): {e}")

#         return Response({"message": "Task completed successfully"}, status=status.HTTP_200_OK)

#     except BuildingCategory.DoesNotExist:
#         return Response({"error": "BuildingCategory with ID 1 not found"}, status=status.HTTP_404_NOT_FOUND)

#     except requests.exceptions.RequestException as e:
#         return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# # Zones 

# @api_view(['GET'])
# @permission_classes([IsAuthenticated])
# def get_zones_from_telangana_school_api(request):

#     url = 'http://10.100.100.21/tsctsadmissions/asset_zone_api.php?token=chaitanya'
#     try:
        
#         building_category_id = 2

#         building_category = BuildingCategory.objects.get(building_category_id = building_category_id)
#         response = requests.get(url)
#         response.raise_for_status() 
#         data = response.json().get('data', [])

#         if not data:
#             return Response({"message": "No data found"}, status=status.HTTP_204_NO_CONTENT)
        
#         for item in data:
#             external_zone_id = item.get('id')
#             zone_name = item.get('zone_name')
#             state_external_id = item.get('state_id')

#             # Fetch the associated state with the external_state_id and category filter
#             state = State.objects.filter(Q(external_state_id = state_external_id) & Q(building_category_id = building_category_id)).first()

#             if external_zone_id and zone_name and state:
#                 existing_zone = Zone.objects.filter(Q(external_zone_id=external_zone_id) & Q(building_category_id = building_category_id) & Q(state_id=state.state_id)).first()

#                 if existing_zone:
#                     # If zone name differs, update it
#                     if existing_zone.name != zone_name:
#                         existing_zone.name = zone_name
#                         existing_zone.save()
#                         print(f"Updated zone: {zone_name} (ID: {external_zone_id})")
#                     else:
#                         print(f"Duplicate zone found, skipping: {zone_name} (ID: {external_zone_id})")
#                 else:
#                     # Create a new zone if not already existing
#                     Zone.objects.create(
#                         external_zone_id=external_zone_id,
#                         name=zone_name,
#                         state=state,
#                         building_category=building_category,
#                         is_active=True
#                     )
#                     print(f"Created new zone: {zone_name} (ID: {external_zone_id})")

#         return Response({"message": "Task completed successfully"}, status=status.HTTP_200_OK)

#     except BuildingCategory.DoesNotExist:
#         return Response({"error": "Building Category not found"}, status=status.HTTP_404_NOT_FOUND)

#     except requests.HTTPError as http_err:
#         return Response({"error": f"HTTP error occurred: {http_err}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#     except json.JSONDecodeError as json_err:
#         return Response({"error": f"Error decoding JSON: {json_err}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#     except Exception as e:
#         return Response({"error": f"An unexpected error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# # ets buildings

# @api_view(['GET'])
# @permission_classes([IsAuthenticated])
# def get_branches_from_telangana_school_api(request):

#     url = 'http://10.100.100.21/tsctsadmissions/asset_branch_api.php?token=chaitanya'
#     try:
        
#         building_category_id = 2 
#         building_category = BuildingCategory.objects.get(building_category_id = building_category_id)
#         response = requests.get(url) 
#         response.raise_for_status()   
#         data = response.json().get('data', [])
 
#         if not data:
#             return Response({"message": "No data found"}, status=status.HTTP_204_NO_CONTENT)

#         for item in data:
#             external_building_id = item.get('id')
#             external_state_id = item.get('state_id')
#             external_zone_id = item.get('zone_id')
#             branch_name = item.get('branch_name')
#             building_code = item.get('building_code')
#             incharge_name = item.get('principal_name')
#             incharge_phno = item.get('principal_phno')
#             incharge_email = item.get('principal_mailid')
#             # building_email = item.get('branch_mailid')
#             address = item.get('address')
#             city = item.get('city')
#             # active_status = item.get('active_status')

#             # Fetch the associated state and zone
#             state = State.objects.filter(Q(external_state_id=external_state_id) & Q(building_category_id = building_category_id)).first()
#             zone = Zone.objects.filter(Q(external_zone_id=external_zone_id) & Q(building_category_id = building_category_id)).first()

#             if external_building_id and state and zone:
#                 existing_building = Branch.objects.filter(
#                     Q(external_building_id=external_building_id) & Q(building_category_id = building_category_id) &
#                     Q(state_id=state.state_id) & Q(zone_id=zone.zone_id)
#                 ).first()

#                 if existing_building:
#                     # Update existing building details
#                     existing_building.name = branch_name
#                     existing_building.location_incharge = incharge_name
#                     existing_building.phonenumber = incharge_phno
#                     existing_building.email = incharge_email
#                     existing_building.building_code = building_code
#                     existing_building.city = city
#                     existing_building.address = address                 
#                     existing_building.state =  state
#                     existing_building.zone  =   zone
#                     existing_building.save()

#                     print(f"Updated building: {branch_name} (ID: {external_building_id})")
#                 else:
#                     # Create a new building entry
#                     Branch.objects.create(
#                                             external_building_id=external_building_id,
#                                             state=state,
#                                             zone=zone,
#                                             building_category=building_category,
#                                             name=branch_name,
#                                             location_incharge = incharge_name,
#                                             phonenumber =incharge_phno,
#                                             email=incharge_email,
#                                             building_code=building_code,
#                                             city=city,
#                                             address=address,
#                                             is_active=True,
#                     )
#                     print(f"Created new building: {branch_name} (ID: {external_building_id})")

#         return Response({"message": "Task completed successfully"}, status=status.HTTP_200_OK)

#     except BuildingCategory.DoesNotExist:
#         return Response({"error": "Building Category not found"}, status=status.HTTP_404_NOT_FOUND)

#     except requests.HTTPError as http_err:
#         return Response({"error": f"HTTP error occurred: {http_err}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#     except json.JSONDecodeError as json_err:
#         return Response({"error": f"Error decoding JSON: {json_err}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#     except Exception as e:
#         return Response({"error": f"An unexpected error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
 
# # DEPARTMENTS New one 
# @api_view(['GET'])
# @permission_classes([IsAuthenticated])
# def get_departments_from_telangana_school_api(request):
#     url = "http://192.168.0.6/varna_api/ets_staff_department.php?token=chaitanya"

#     try:
#         building_category_id = 2
#         building_category = BuildingCategory.objects.get(building_category_id = building_category_id)

#         response = requests.get(url)
#         response.raise_for_status()
#         data = response.json()
#         # data = response.json().get('data', [])

#         if not data:
#             return Response({"message": "No data found"}, status=status.HTTP_204_NO_CONTENT)

#         # Process state data directly within the view
#         for item in data:    
#             external_id = item.get('id')
#             name = item.get('name')
#             division_id = item.get('division_id')
#             active_status = item.get('active_status')
            

#             if external_id and name:
#                 existing_department = Department.objects.filter(Q(external_id=external_id) & Q(building_category_id = building_category_id)).first()
#                 if existing_department:
#                     existing_department.name = name
#                     existing_department.is_active = True if active_status == "1" else False
#                     existing_department.division_id = division_id
#                     existing_department.save()
#                     # print(f"Updated department: {name} (ID: {external_id})")
                    
#                 else:
#                     try:
#                         Department.objects.create(
#                             external_id=external_id,
#                             name=name,
#                             building_category=building_category,
#                             division_id = division_id,
#                             is_active = True if active_status == "1" else False
#                         )
#                         # print(f"Created new Department: {name} (ID: {external_id})")
#                     except Exception as e:
#                         pass
#                         # print(f"Error creating Department {name} (ID: {external_id}): {e}")

#         return Response({"message": "Task completed successfully"}, status=status.HTTP_200_OK)

#     except BuildingCategory.DoesNotExist:
#         return Response({"error": "BuildingCategory with ID 2 not found"}, status=status.HTTP_404_NOT_FOUND)

#     except requests.exceptions.RequestException as e:
#         return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# @api_view(['GET'])
# @permission_classes([IsAuthenticated])
# def get_designation_from_telangana_school_api(request):
#     url = "http://192.168.0.6/varna_api/ets_staff_designations.php?token=chaitanya"

#     try:
#         building_category_id = 2
#         building_category = BuildingCategory.objects.get(building_category_id = building_category_id)
#         response = requests.get(url)
#         response.raise_for_status()
#         data = response.json()
#         # data = response.json().get('data', [])

#         if not data:
#             return Response({"message": "No data found"}, status=status.HTTP_204_NO_CONTENT)

#         # Process state data directly within the view
#         for item in data:    
#             external_id = item.get('id')
#             name = item.get('designation')
#             departments_id = item.get('departments_id')
#             short_code = item.get('short_code')
#             active_status = item.get('active_status')
#             division_id = item.get('division_id')
            
#             department = Department.objects.filter(Q(external_id = departments_id) & Q(building_category_id = building_category_id)).first()

#             if external_id and name:
#                 existing_designation = Designation.objects.filter(Q(external_id = external_id) & Q(building_category_id = building_category_id)).first()
#                 if existing_designation:
#                     existing_designation.name = name
#                     existing_designation.department = department
#                     existing_designation.short_code = short_code
#                     existing_designation.is_active = True if active_status == "1" else False
#                     existing_designation.division_id = division_id
#                     existing_designation.save()
#                     print(f"Updated designation: {name} (ID: {external_id})")
                    
#                 else:
#                     try:
#                         Designation.objects.create(
#                             external_id=external_id,
#                             name=name,
#                             building_category=building_category,
#                             department = department,
#                             short_code =  short_code,
#                             division_id=division_id,
#                             is_active = True if active_status == "1" else False
                            
#                         )
#                         print(f"Created new designation: {name} (ID: {external_id})")
#                     except Exception as e:
#                         pass
#                         print(f"Error creating designation {name} (ID: {external_id}): {e}")

#         return Response({"message": "Task completed successfully"}, status=status.HTTP_200_OK)

#     except BuildingCategory.DoesNotExist:
#         return Response({"error": "BuildingCategory with ID 2 not found"}, status=status.HTTP_404_NOT_FOUND)

#     except requests.exceptions.RequestException as e:
#         return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



# #===========================================================================================================================================================================================================
# #==============================================================================     ETS School Data sync end    =================================================================================================
# #============================================================================================================================================================================================================


# #update score centers 


# def update_scts_branch_score_centers(request):
#     token = "token"  # store in settings for security
#     url = f"http://192.168.0.6/varna_api/score_centers.php?token=chaitanya"

#     building_category_id = 1


#     try:
#         response = requests.get(url, timeout=20)
#         response.raise_for_status()
#         centers = response.json()
#     except Exception as e:
#         return JsonResponse({"status": "error", "message": f"API request failed: {str(e)}"}, status=500)

#     updated_count = 0
#     skipped = []

#     with transaction.atomic():
#         for center in centers:
#             external_building_id = center.get("branch_id")
#             branch_name = center.get("branch")
            
#             if not external_building_id:
#                 continue

#             try:
#                 branch = Branch.objects.get(building_category_id = building_category_id , external_building_id = external_building_id )
#                 # ✅ Only update if BranchDetail exists
#                 if hasattr(branch, "branch_detail"):
#                     if not branch.branch_detail.is_score:
#                         branch.branch_detail.is_score = True
#                         branch.branch_detail.save(update_fields=["is_score"])
#                         updated_count += 1
#                 else:
#                     skipped.append({"external_building_id": external_building_id, "branch_name": branch_name})
#             except Branch.DoesNotExist:
#                 skipped.append({"external_building_id": external_building_id, "branch_name": branch_name})

#     return JsonResponse({
#         "status": "success",
#         "message": f"Score centers sync completed. {updated_count} branches updated.",
#         "skipped": skipped,
#     })



# def update_telangana_branch_score_centers(request):
#     token = "token"  # store in settings for security
#     url = f"http://192.168.0.6/varna_api/ets_score_centers.php?token=chaitanya"

#     building_category_id = 2


#     try:
#         response = requests.get(url, timeout=20)
#         response.raise_for_status()
#         centers = response.json()
#     except Exception as e:
#         return JsonResponse({"status": "error", "message": f"API request failed: {str(e)}"}, status=500)

#     updated_count = 0
#     skipped = []

#     with transaction.atomic():
#         for center in centers:
#             external_building_id = center.get("branch_id")
#             branch_name = center.get("branch")
            
#             if not external_building_id:
#                 continue

#             try:
#                 branch = Branch.objects.get(building_category_id = building_category_id , external_building_id = external_building_id )
#                 # ✅ Only update if BranchDetail exists
#                 if hasattr(branch, "branch_detail"):
#                     if not branch.branch_detail.is_score:
#                         branch.branch_detail.is_score = True
#                         branch.branch_detail.save(update_fields=["is_score"])
#                         updated_count += 1
#                 else:
#                     skipped.append({"external_building_id": external_building_id, "branch_name": branch_name})
#             except Branch.DoesNotExist:
#                 skipped.append({"external_building_id": external_building_id, "branch_name": branch_name})

#     return JsonResponse({
#         "status": "success",
#         "message": f"Score centers sync completed. {updated_count} branches updated.",
#         "skipped": skipped,
#     })




#======================================================== collect users from varna  ========================================================================
import requests
from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import UserProfile, VarnaProfiles

User = get_user_model()


class SyncAllVarnaProfilesUsersAPIView(APIView):
    """
    Fetch and sync users for all active VarnaProfiles from the Varna API.
    """

    def get(self, request):
        base_url = "http://192.168.0.6/varna_api/academics_user_management.php"
        token = "chaitanya"

        total_created = 0
        total_updated = 0
        profile_summary = []

        active_profiles = VarnaProfiles.objects.filter(is_active=True)

        for profile in active_profiles:
            profile_code = profile.varna_profile_short_code

            params = {
                "token": token,
                "type": "users",
                "profile_short_code": profile_code,
            }

            try:
                response = requests.get(base_url, params=params, timeout=10)
                response.raise_for_status()
                users_data = response.json()
            except requests.exceptions.RequestException as e:
                profile_summary.append({
                    "profile_short_code": profile_code,
                    "status": "failed",
                    "error": str(e)
                })
                continue

            created_count = 0
            updated_count = 0

            for item in users_data:
                varna_user_id = item.get("user_id")
                username = item.get("login")
                varna_profile_short_code = item.get("profile_id")

                if not username or not varna_user_id:
                    continue

                # Create or get User
                user, created_user = User.objects.get_or_create(
                    username=username,
                    defaults={"is_active": True}
                )

                # Set default password if newly created
                if created_user:
                    user.set_password("password123")
                    user.save()

                # Create or update UserProfile
                user_profile, created_profile = UserProfile.objects.get_or_create(
                    user=user,
                    defaults={
                        "varna_user": True,
                        "varna_user_id": varna_user_id,
                        "varna_profile_short_code": varna_profile_short_code,
                        "varna_profile": profile,
                        "must_change_password": True,
                    },
                )

                if not created_profile:
                    user_profile.varna_user = True
                    user_profile.varna_user_id = varna_user_id
                    user_profile.varna_profile_short_code = varna_profile_short_code
                    user_profile.varna_profile = profile
                    user_profile.save()
                    updated_count += 1
                else:
                    created_count += 1

            total_created += created_count
            total_updated += updated_count
            profile_summary.append({
                "profile_short_code": profile_code,
                "created": created_count,
                "updated": updated_count,
                "status": "success"
            })

        return Response({
            "message": "Varna user synchronization completed successfully.",
            "total_profiles_processed": len(active_profiles),
            "total_users_created": total_created,
            "total_users_updated": total_updated,
            "details": profile_summary
        }, status=status.HTTP_200_OK)
