from django.contrib.auth.models import User
from base.models import DoctorReview, Appointment, Doctor, Product, CustomUser, Order, OrderItem, ShippingAddress
from django.shortcuts import render
from django.http import JsonResponse
from rest_framework.permissions import IsAuthenticated,IsAdminUser
from rest_framework.decorators import api_view,permission_classes
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import status
from django.contrib.auth.hashers import make_password
from .serializer import DoctorReviewSerializer, AppointmentSerializer, DoctorSerializer, DoctorDetailSerializer, ProductSerializer,UserSerializer,UserSerializerWithToken,OrderSerializer
from datetime import datetime
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

@api_view(['GET'])
def getRoutes(request):
    return Response('Hello')

@api_view(['GET'])
def getProducts(request):
    products=Product.objects.all()
    serializer=ProductSerializer(products,many=True)
    return Response(serializer.data)

@api_view(['GET'])
def getProduct(request,pk):
    product=Product.objects.get(_id=pk)
    serializer=ProductSerializer(product,many=False)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def addOrderItems(request):
    user = request.user
    data = request.data

    orderItems = data['orderItems']

    if orderItems and len(orderItems) == 0:
        return Response({'detail': 'No Order Items'}, status=status.HTTP_400_BAD_REQUEST)
    
    # (1) Create order
    order = Order.objects.create(
        user=user,
        paymentMethod=data['paymentMethod'],
        taxPrice=data['taxPrice'],
        shippingPrice=data['shippingPrice'],
        totalPrice=data['totalPrice']
    )

    # (2) Create shipping address
    shipping = ShippingAddress.objects.create(
        order=order,
        address=data['shippingAddress']['address'],
        city=data['shippingAddress']['city'],
        postalCode=data['shippingAddress']['postalCode'],
        country=data['shippingAddress']['country'],
    )

    # (3) Create order items and set order to orderItem relationship
    for i in orderItems:
        product = Product.objects.get(_id=i['product'])

        item = OrderItem.objects.create(
            product=product,
            order=order,
            name=product.name,
            qty=i['qty'],
            price=i['price'],
            image=product.image.url
        )

        # (4) Update stock
        product.countInStock -= item.qty
        product.save()

    serializer = OrderSerializer(order, many=False)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getMyOrders(request):
    user = request.user
    orders = user.order_set.all()
    serializer = OrderSerializer(orders, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAdminUser])
def getOrders(request):
    orders = Order.objects.all()
    serializer = OrderSerializer(orders, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getOrderById(request, pk):
    user = request.user

    try:
        order = Order.objects.get(_id=pk)
        if user.is_staff or order.user == user:
            serializer = OrderSerializer(order, many=False)
            return Response(serializer.data)
        else:
            return Response({'detail': 'Not authorized to view this order'},
                            status=status.HTTP_403_FORBIDDEN)
    except Order.DoesNotExist:
        return Response({'detail': 'Order does not exist'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def updateOrderToPaid(request, pk):
    try:
        order = Order.objects.get(_id=pk)
        order.isPaid = True
        order.paidAt = datetime.now()
        order.save()
        return Response({'detail': 'Order was paid'}, status=status.HTTP_200_OK)
    except Order.DoesNotExist:
        return Response({'detail': 'Order does not exist'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['PUT'])
@permission_classes([IsAdminUser])
def updateOrderToDelivered(request, pk):
    try:
        order = Order.objects.get(_id=pk)
        order.isDelivered = True
        order.deliveredAt = datetime.now()
        order.save()
        return Response({'detail': 'Order was delivered'}, status=status.HTTP_200_OK)
    except Order.DoesNotExist:
        return Response({'detail': 'Order does not exist'}, status=status.HTTP_404_NOT_FOUND)
    
class MyTokenObtainPairSerializer(TokenObtainPairSerializer):

    def validate(self,attrs):
        data=super().validate(attrs)
        serializer = UserSerializerWithToken(self.user).data
        for k,v in serializer.items():
            data[k]=v
    

        return data

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class=MyTokenObtainPairSerializer
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def  getUserProfile(request):
    user=request.user
    serializer=UserSerializer(user,many=False)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAdminUser])
def  getUsers(request):
    user=User.objects.all()
    serializer=UserSerializer(user,many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAdminUser])
def getUserById(request, pk):
    user = User.objects.get(id=pk)
    serializer = UserSerializer(user, many=False)
    return Response(serializer.data)

@api_view(['POST'])
def registerUser(request):
    data = request.data
    print(data)
    
    if CustomUser.objects.filter(email=data['email']).exists():
        message = {'details': 'User with this email already exists'}
        return Response(message, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = CustomUser.objects.create(
            first_name=data['name'],
            email=data['email'],
            password=make_password(data['password'])
        )
        serializer = UserSerializerWithToken(user, many=False)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    except Exception as e:
        print("Error creating user:", str(e))
        message = {'details': 'An error occurred while creating the user'}
        return Response(message, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def updateUserProfile(request):
    user = request.user
    serializer = UserSerializerWithToken(user, many=False)

    data = request.data
    user.first_name = data['name']
    user.email = data['email']

    if data['password'] != '':
        user.password = make_password(data['password'])

    user.save()

    return Response(serializer.data)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def updateUser(request, pk):
    user = User.objects.get(id=pk)

    data = request.data

    user.first_name = data['name']
    user.username = data['email']
    user.email = data['email']
    user.is_staff = data['isAdmin']

    user.save()

    serializer = UserSerializer(user, many=False)

    return Response(serializer.data)


@api_view(['DELETE'])
@permission_classes([IsAdminUser])
def deleteUser(request, pk):
    userForDeletion = User.objects.get(id=pk)
    userForDeletion.delete()
    return Response('User was deleted')

# !!!Doctors
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
def getAllDoctors(request):
    doctors = Doctor.objects.all()
    serializer = DoctorSerializer(doctors, many=True)
    return Response(serializer.data)

@api_view(['GET'])
# @permission_classes([IsAdminUser])
def getDoctorDetail(request, pk):
    try:
        doctor = Doctor.objects.get(user_id=pk)
        serializer = DoctorSerializer(doctor, many=False)
        return Response(serializer.data)
    except Doctor.DoesNotExist:
        return Response({'detail': 'Doctor not found'}, status=404)

@api_view(['POST'])
# @permission_classes([IsAuthenticated])
def create_appointment(request):
    print(request.data)  # Log the incoming request data
    if request.method == 'POST':
        serializer = AppointmentSerializer(data=request.data, context={'request': request})

        if serializer.is_valid():
            serializer.validated_data['user'] = request.user 
            
            doctor_id = request.data.get('doctor') 
            if doctor_id:
                try:
                    serializer.validated_data['doctor'] = Doctor.objects.get(id=doctor_id)
                except Doctor.DoesNotExist:
                    return Response({"detail": "Doctor not found."}, status=status.HTTP_404_NOT_FOUND)

            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            print(serializer.errors) 
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# !!Doctor & User Appointments
class UserAppointmentsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        
        appointments = Appointment.objects.filter(user=user)

        serializer = AppointmentSerializer(appointments, many=True)
        
        return Response(serializer.data, status=status.HTTP_200_OK)

class DoctorAppointmentsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            doctor = Doctor.objects.get(user=request.user) 
        except Doctor.DoesNotExist:
            return Response({"detail": "Doctor not found."}, status=status.HTTP_404_NOT_FOUND)

        appointments = Appointment.objects.filter(doctor=doctor)

        if appointments.exists():
            serializer = AppointmentSerializer(appointments, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({"message": "No appointments found for this doctor."}, status=status.HTTP_404_NOT_FOUND)

class DoctorUpdateAppointmentsView(APIView):
    # permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        try:
            doctor = Doctor.objects.get(user=request.user)
        except Doctor.DoesNotExist:
            return Response({"detail": "Doctor not found."}, status=status.HTTP_404_NOT_FOUND)

        appointment_id = request.data.get("appointment_id")
        google_meet_link = request.data.get("google_meet_link")

        try:
            appointment = Appointment.objects.get(id=appointment_id, doctor=doctor)
        except Appointment.DoesNotExist:
            return Response({"detail": "Appointment not found."}, status=status.HTTP_404_NOT_FOUND)

        appointment.google_meet_link = google_meet_link
        appointment.status = "Approved" 
        appointment.save()

        serializer = AppointmentSerializer(appointment)
        return Response(serializer.data, status=status.HTTP_200_OK)

class DoctorUpdateStatusToConsultedView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        try:
            doctor = Doctor.objects.get(user=request.user)
        except Doctor.DoesNotExist:
            return Response({"detail": "Doctor not found."}, status=status.HTTP_404_NOT_FOUND)

        appointment_id = request.data.get("appointment_id")

        try:
            appointment = Appointment.objects.get(id=appointment_id, doctor=doctor)
        except Appointment.DoesNotExist:
            return Response({"detail": "Appointment not found."}, status=status.HTTP_404_NOT_FOUND)

        # Update the status to "Consulted"
        appointment.status = "Consulted"
        appointment.save()

        serializer = AppointmentSerializer(appointment)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
# !!Appointments
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getAppointmentById(request, pk):
    try:
        appointment = Appointment.objects.get(id=pk)
        serializer = AppointmentSerializer(appointment)
        return Response(serializer.data)
    except Appointment.DoesNotExist:
        return Response({'detail': 'Appointment does not exist'}, status=404)
    
@api_view(['PUT'])
# @permission_classes([IsAuthenticated])
def updateAppointmentToPaid(request, pk):
    try:
        appointment = Appointment.objects.get(id=pk)
        appointment.isPaid = True
        appointment.status = 'Approved'
        appointment.paidAt = datetime.now()
        appointment.save()
        return Response({'detail': 'Appointment was paid'}, status=status.HTTP_200_OK)
    except Appointment.DoesNotExist:
        return Response({'detail': 'Appointment does not exist'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['PUT'])
# @permission_classes([IsAuthenticated])
def updateAppointmentToReviewed(request, pk):
    try:
        appointment = Appointment.objects.get(id=pk)
        appointment.isReviewed = True
        appointment.status = 'Reviewed'
        appointment.save()
        return Response({'detail': 'Appointment was reviewed'}, status=status.HTTP_200_OK)
    except Appointment.DoesNotExist:
        return Response({'detail': 'Appointment does not exist'}, status=status.HTTP_404_NOT_FOUND)

# !!Doctor Reviews
@api_view(['POST'])
@permission_classes([AllowAny])
def createDoctorReview(request, pk):
    user = request.user

    try:
        doctor = Doctor.objects.get(id=pk)
    except Doctor.DoesNotExist:
        return Response({'detail': 'Doctor not found'}, status=status.HTTP_404_NOT_FOUND)

    data = request.data

    if not Appointment.objects.filter(user=user, doctor=doctor).exists():
        return Response({'detail': 'You must consult this doctor before leaving a review.'}, status=status.HTTP_400_BAD_REQUEST)

    if data.get('rating') == 0:
        return Response({'detail': 'Please select a rating'}, status=status.HTTP_400_BAD_REQUEST)

    review = DoctorReview.objects.create(
        user=user,
        doctor=doctor,
        rating=data['rating'],
        comment=data.get('comment', '')
    )

    reviews = doctor.reviews.all()
    doctor.numReviews = reviews.count()

    total = sum([rev.rating for rev in reviews])
    doctor.rating = total / doctor.numReviews if doctor.numReviews > 0 else 0
    doctor.save()

    return Response({'detail': 'Review added'}, status=status.HTTP_201_CREATED)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def doctor_review_list(request, doctor_id):
    try:
        doctor = Doctor.objects.get(user__id=doctor_id)
    except Doctor.DoesNotExist:
        return Response({"detail": "Doctor not found."}, status=404)
    
    reviews = DoctorReview.objects.filter(doctor=doctor)
    serializer = DoctorReviewSerializer(reviews, many=True)
    return Response(serializer.data)
