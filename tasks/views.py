from django.shortcuts import render,redirect
from rest_framework.views import APIView
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from rest_framework.response import Response
from .serializers import *
from .models import *
from django.db.utils import IntegrityError

# utils

def is_logged_in(request):
    if request.user.is_authenticated:
        return True
    return False 



class LoginHandler(APIView):

    def get(self,request):

        if request.user.is_authenticated:
            return redirect('homepage')
        
        return render(request,"auth/login.html")
    

    def post(self,request):

        data = request.data
        user = authenticate(username=data.get('username'),password=data.get('password'))
        if user is not None:

            login(request,user)
            return Response({"data":[],"status":"success","message":"redirecting in 2s"})
        
        return Response({"data":[],"status":"error","message":"Invalid username or password"})
    

class RegisterUser(APIView):
    
    def get(self,request):

        return render(request,"auth/register.html")
    
    def post(self,request):
        data = request.data
        
        if data.get('username') == "" and data.get('password')=="":
            return Response({
                "data":[],
                "message":"username and password are required",
                "status":"error",
            })
        elif data.get('password') == "":
            return Response({
                "data":[],
                "message":"password is required",
                "status":"error",
            })
        elif data.get('username') == "":
            return Response({
                "data":[],
                "message":"username is required",
                "status":"error",
            })

        existing_obj = User.objects.filter(username= data.get('username')).first()
        if existing_obj is not None:
            return Response({
                "data":[],
                "message":"Username already taken",
                "status":"error"
            })
        user = UserSerializer(data=data)
        if user.is_valid():
            user.save()
            return Response({
                "data":user.data,
                "message":"Redirecting in 2s",
                "status":"success"
            })
        
        return Response({
            "data":[],
            "message":"Server Error",
            "status":"error"
        })
    


def Homepage(request):
    if not(request.user.is_authenticated):
        return redirect('login')
    return render(request,'home/index.html')


def LogoutHandler(request):
    logout(request)
    return redirect('login')



class TaskAPI(APIView):

    def get(self,request):
        if request.user.is_authenticated:
            users = User.objects.all()
            return render(request,"new/task.html",{"users":users})
        return redirect('login')
    

    def post(self,request):
        try:
            data = request.data
            print(data)
            task = Task.objects.create(
                title = data.get('title'),
                description = data.get('description'),
                due_date = data.get('due_date'),
                status = data.get('status'),
            )
            users_list = list(data.get('allowed_users'))
            print("users =",users_list)
            for usr in users_list:
                if usr == ",":
                    pass
                else:
                    task.allowed_users.add(int(usr))
            
            task.save()
            return Response({
                "data":TaskSerializer(task).data,
                "message":"Task Created",
                "status":"success",
            })
        except IntegrityError:
            return Response({
                "data":[],
                "message":"Task Title Exists",
                "status":'error',
            })



class ModifyTaskAPI(APIView):
    
    def get(self,request,task_id):
        if is_logged_in(request):
            allowed_users = Task.objects.filter( id = task_id).first().allowed_users.all()
            print("users = ",allowed_users)
            if not(request.user.id in allowed_users) or not(request.user.is_superuser):
                return redirect('403')
            
            users = User.objects.all()
            task = Task.objects.filter(id = task_id).first()
            serializer_class = TaskSerializer(task,many=False)
            return render(request,"edit/task.html",{"task":task,"users":users,"task_id":task_id})
        return redirect('login')
    

    def put(self,request,task_id):

        if is_logged_in(request):
            allowed_users = Task.objects.filter( id = task_id).first().allowed_users.all()
            print("users = ",allowed_users)
            does_user_in_allowed_user = False
            for usr in allowed_users:
                if usr.id  == request.user.id or request.user.is_superuser:
                    does_user_in_allowed_user = True
            if not(does_user_in_allowed_user):
                return Response({
                        "data":[],
                        "message":"access denied",
                        "status":"error",
                        "redirect":"/403/",
                    }) 
                    
            task = Task.objects.filter( id = task_id).first()
            str_data = request.data.get('allowed_users', '')
        
            # Convert the string to a list of items
            list_data = str_data.split(',')  # Assuming the items are comma-separated
            
            # Update the request data with the converted list
            request.data['allowed_users'] = list_data
            serializer_class = TaskSerializer(instance=task,data=request.data)
            if serializer_class.is_valid():
                serializer_class.save()
                return Response({
                    "data":serializer_class.data,
                    "message":"Task Updated",
                    "status":"success"
                })
            return Response({
                "data":[],
                "message":f"{serializer_class.errors}",
                "status":"error"
            })
        return redirect('login')
        
        

    def delete(self,request,task_id):
        if not(request.user.id in Task.objects.filter( id = task_id).first().allowed_users):
            return redirect('403')
        task = Task.objects.filter(id = task_id)
        if task is not None:
            task.delete()
            return Response({
                "data":[],
                "message":"Task Deleted",
                "status":"success"
            })
        return Response({
            "data":[],
            "message":"No Task Found To Delete",
            "status":"error"
        })
        

class AssignTaskMembers(APIView):

    def post(self,request):

        data = request.data

        task = Task.objects.filter()
    


def AccessDenied403(request):
    return render(request,"error/403.html")


class GetAllTasks(APIView):

    def get(self,request):
        if is_logged_in(request):
            tasks = Task.objects.all()
            users = User.objects.all()
            task_serializer = TaskSerializer(tasks,many=True)
            user_serilaizer = AllUserSerializer(users,many=True)
            return Response({
                "tasks":task_serializer.data,
                "users":user_serilaizer.data,
                "status":"success",
                "message":"",
            })
        return redirect('login')
    
def AllTasks(request):
    if is_logged_in(request):
        return render(request,"all/tasks.html")
    return redirect('login')


def EditTask(request,task_id):
    _users = User.objects.all()
    task = Task.objects.filter(id = task_id).first()
    _allowed_users = task.allowed_users
    allowed_users = []
    for user in _users:
        for au in _allowed_users.all():
            if user.id == au.id:
                allowed_users.append(user)
    return render(request,"edit/task.html",{"task_id":task_id,"task":task,"users":_users,"allowed_users":allowed_users})


def ReadTask(request,task_id):

    task = Task.objects.filter(id = task_id).first()
    return render(request,"single/task.html",{"task_id":task_id,"task":task})
