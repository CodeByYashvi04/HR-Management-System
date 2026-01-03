# main.py - FastAPI Backend for Dayflow HRMS
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime, timedelta, date
from passlib.context import CryptContext
from jose import JWTError, jwt
from pymongo import MongoClient
from bson import ObjectId
import os
from enum import Enum
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ============================================
# CONFIGURATION
# ============================================

app = FastAPI(title="Dayflow HRMS API", version="1.0.0")

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production-min-32-chars")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

# MongoDB Configuration
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
client = MongoClient(MONGODB_URL)
db = client.dayflow_hrms

# ============================================
# ENUMS
# ============================================

class UserRole(str, Enum):
    EMPLOYEE = "employee"
    ADMIN = "admin"

class UserStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"

class AttendanceStatus(str, Enum):
    PRESENT = "present"
    ABSENT = "absent"
    HALF_DAY = "half-day"
    LEAVE = "leave"

class LeaveType(str, Enum):
    PAID = "paid"
    SICK = "sick"
    UNPAID = "unpaid"

class LeaveStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

class PaymentStatus(str, Enum):
    PAID = "paid"
    PENDING = "pending"
    PROCESSING = "processing"

# ============================================
# PYDANTIC MODELS
# ============================================

# User Models
class UserBase(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None
    department: Optional[str] = None
    designation: Optional[str] = None

class UserCreate(UserBase):
    password: str
    role: UserRole = UserRole.EMPLOYEE

class UserUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    department: Optional[str] = None
    designation: Optional[str] = None
    status: Optional[UserStatus] = None

class UserResponse(UserBase):
    userId: str
    role: UserRole
    status: UserStatus
    avatar: Optional[str] = None
    createdAt: datetime
    updatedAt: datetime

    class Config:
        from_attributes = True

# Auth Models
class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    token: str
    user: dict

# Attendance Models
class AttendanceResponse(BaseModel):
    id: str
    employeeId: str
    date: str
    checkIn: Optional[str] = None
    checkOut: Optional[str] = None
    status: str
    totalHours: Optional[float] = None
    createdAt: str

# Leave Models
class LeaveCreate(BaseModel):
    leaveType: LeaveType
    startDate: str
    endDate: str
    reason: str

class LeaveUpdate(BaseModel):
    status: LeaveStatus
    adminComment: Optional[str] = None

class LeaveResponse(BaseModel):
    id: str
    employeeId: str
    employeeName: str
    leaveType: str
    startDate: str
    endDate: str
    days: int
    reason: str
    status: str
    adminComment: Optional[str] = None
    appliedOn: str

# Salary Models
class SalaryCreate(BaseModel):
    employeeId: str
    basicSalary: float
    housingAllowance: float = 0
    transportAllowance: float = 0
    medicalAllowance: float = 0
    otherAllowances: float = 0
    taxDeduction: float = 0
    insuranceDeduction: float = 0
    otherDeductions: float = 0

class SalaryResponse(BaseModel):
    id: str
    employeeId: str
    employeeName: str
    basicSalary: float
    housingAllowance: float
    transportAllowance: float
    medicalAllowance: float
    otherAllowances: float
    taxDeduction: float
    insuranceDeduction: float
    otherDeductions: float
    netSalary: float
    effectiveDate: str
    updatedAt: str

# ============================================
# HELPER FUNCTIONS
# ============================================

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    payload = decode_token(token)
    user_id = payload.get("userId")
    
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    
    user = db.users.find_one({"userId": user_id})
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return user

def get_current_admin(current_user: dict = Depends(get_current_user)):
    if current_user.get("role") != UserRole.ADMIN.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user

def generate_employee_id(role: UserRole) -> str:
    prefix = "ADM" if role == UserRole.ADMIN else "EMP"
    count = db.users.count_documents({})
    return f"{prefix}{str(count + 1).zfill(3)}"

def calculate_days(start_date_str: str, end_date_str: str) -> int:
    start = datetime.strptime(start_date_str, "%Y-%m-%d").date()
    end = datetime.strptime(end_date_str, "%Y-%m-%d").date()
    delta = end - start
    return delta.days + 1

def serialize_doc(doc: dict) -> dict:
    """Convert MongoDB document to JSON-serializable dict"""
    if doc is None:
        return None
    doc_copy = doc.copy()
    doc_copy["id"] = str(doc_copy.pop("_id"))
    
    # Convert datetime objects to strings
    for key, value in doc_copy.items():
        if isinstance(value, datetime):
            doc_copy[key] = value.isoformat()
        elif isinstance(value, date):
            doc_copy[key] = value.isoformat()
    
    return doc_copy

# ============================================
# ROUTES - Health Check
# ============================================

@app.get("/")
def root():
    return {
        "message": "Dayflow HRMS API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}

# ============================================
# ROUTES - Authentication
# ============================================

@app.post("/api/auth/register", status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate):
    """Register a new user"""
    
    # Check if user already exists
    existing_user = db.users.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )
    
    # Generate employee ID
    user_id = generate_employee_id(user_data.role)
    
    # Hash password
    hashed_password = hash_password(user_data.password)
    
    # Create user document
    user_doc = {
        "userId": user_id,
        "name": user_data.name,
        "email": user_data.email,
        "password": hashed_password,
        "role": user_data.role.value,
        "phone": user_data.phone,
        "department": user_data.department,
        "designation": user_data.designation,
        "avatar": f"https://ui-avatars.com/api/?name={user_data.name.replace(' ', '+')}&background=2563EB&color=fff",
        "status": UserStatus.ACTIVE.value,
        "createdAt": datetime.utcnow(),
        "updatedAt": datetime.utcnow()
    }
    
    result = db.users.insert_one(user_doc)
    user_doc["_id"] = result.inserted_id
    
    user_response = serialize_doc(user_doc)
    user_response.pop("password", None)
    
    return user_response

@app.post("/api/auth/login", response_model=TokenResponse)
def login(login_data: LoginRequest):
    """Login and get access token"""
    
    # Find user
    user = db.users.find_one({"email": login_data.email})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    # Verify password
    if not verify_password(login_data.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    # Check if user is active
    if user.get("status") != UserStatus.ACTIVE.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive"
        )
    
    # Create access token
    token_data = {
        "userId": user["userId"],
        "email": user["email"],
        "role": user["role"]
    }
    access_token = create_access_token(token_data)
    
    # Remove password from response
    user_response = serialize_doc(user)
    user_response.pop("password", None)
    
    return {
        "token": access_token,
        "user": user_response
    }

# ============================================
# ROUTES - Employee Management
# ============================================

@app.get("/api/employees")
def get_employees(
    department: Optional[str] = None,
    current_user: dict = Depends(get_current_admin)
):
    """Get all employees (Admin only)"""
    
    filter_query = {}
    if department:
        filter_query["department"] = department
    
    employees = list(db.users.find(filter_query))
    
    result = []
    for emp in employees:
        emp_data = serialize_doc(emp)
        emp_data.pop("password", None)
        result.append(emp_data)
    
    return result

@app.get("/api/employees/{employee_id}")
def get_employee(
    employee_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get single employee details"""
    
    # Users can only view their own data unless they're admin
    if current_user["role"] != UserRole.ADMIN.value and current_user["userId"] != employee_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    employee = db.users.find_one({"userId": employee_id})
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found"
        )
    
    emp_data = serialize_doc(employee)
    emp_data.pop("password", None)
    
    return emp_data

@app.put("/api/employees/{employee_id}")
def update_employee(
    employee_id: str,
    update_data: UserUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update employee information"""
    
    # Users can only update their own data unless they're admin
    if current_user["role"] != UserRole.ADMIN.value and current_user["userId"] != employee_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # Prepare update document
    update_dict = {k: v for k, v in update_data.dict().items() if v is not None}
    
    # Only admin can change status
    if "status" in update_dict and current_user["role"] != UserRole.ADMIN.value:
        del update_dict["status"]
    
    if not update_dict:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No valid fields to update"
        )
    
    update_dict["updatedAt"] = datetime.utcnow()
    
    result = db.users.find_one_and_update(
        {"userId": employee_id},
        {"$set": update_dict},
        return_document=True
    )
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found"
        )
    
    emp_data = serialize_doc(result)
    emp_data.pop("password", None)
    
    return emp_data

@app.delete("/api/employees/{employee_id}")
def delete_employee(
    employee_id: str,
    current_user: dict = Depends(get_current_admin)
):
    """Delete employee (Admin only)"""
    
    result = db.users.delete_one({"userId": employee_id})
    
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found"
        )
    
    return {"message": "Employee deleted successfully"}

# ============================================
# ROUTES - Attendance Management
# ============================================

@app.post("/api/attendance/checkin")
def check_in(current_user: dict = Depends(get_current_user)):
    """Check in for the day"""
    
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    
    # Check if already checked in today
    existing = db.attendance.find_one({
        "employeeId": current_user["userId"],
        "date": {"$gte": today}
    })
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Already checked in today"
        )
    
    check_in_time = datetime.utcnow().strftime("%I:%M %p")
    
    attendance_doc = {
        "employeeId": current_user["userId"],
        "date": datetime.utcnow(),
        "checkIn": check_in_time,
        "checkOut": None,
        "status": AttendanceStatus.PRESENT.value,
        "totalHours": None,
        "createdAt": datetime.utcnow()
    }
    
    db.attendance.insert_one(attendance_doc)
    
    return {
        "message": "Checked in successfully",
        "checkIn": check_in_time,
        "date": attendance_doc["date"].isoformat()
    }

@app.post("/api/attendance/checkout")
def check_out(current_user: dict = Depends(get_current_user)):
    """Check out for the day"""
    
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    
    attendance = db.attendance.find_one({
        "employeeId": current_user["userId"],
        "date": {"$gte": today}
    })
    
    if not attendance:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No check-in found for today"
        )
    
    if attendance.get("checkOut"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Already checked out"
        )
    
    check_out_time = datetime.utcnow().strftime("%I:%M %p")
    
    # Calculate hours worked
    try:
        check_in_dt = datetime.strptime(attendance["checkIn"], "%I:%M %p")
        check_out_dt = datetime.strptime(check_out_time, "%I:%M %p")
        hours_worked = (check_out_dt - check_in_dt).total_seconds() / 3600
        if hours_worked < 0:
            hours_worked += 24
        hours_worked = round(hours_worked, 1)
    except:
        hours_worked = 8.0
    
    db.attendance.update_one(
        {"_id": attendance["_id"]},
        {"$set": {
            "checkOut": check_out_time,
            "totalHours": hours_worked
        }}
    )
    
    return {
        "message": "Checked out successfully",
        "checkOut": check_out_time,
        "totalHours": hours_worked
    }

@app.get("/api/attendance")
def get_attendance(
    employee_id: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Get attendance records"""
    
    filter_query = {}
    
    # Non-admin users can only view their own attendance
    if current_user["role"] == UserRole.ADMIN.value and employee_id:
        filter_query["employeeId"] = employee_id
    else:
        filter_query["employeeId"] = current_user["userId"]
    
    records = list(db.attendance.find(filter_query).sort("date", -1).limit(100))
    
    return [serialize_doc(record) for record in records]

# ============================================
# ROUTES - Leave Management
# ============================================

@app.post("/api/leaves", status_code=status.HTTP_201_CREATED)
def apply_leave(
    leave_data: LeaveCreate,
    current_user: dict = Depends(get_current_user)
):
    """Apply for leave"""
    
    days = calculate_days(leave_data.startDate, leave_data.endDate)
    
    leave_doc = {
        "employeeId": current_user["userId"],
        "employeeName": current_user["name"],
        "leaveType": leave_data.leaveType.value,
        "startDate": leave_data.startDate,
        "endDate": leave_data.endDate,
        "days": days,
        "reason": leave_data.reason,
        "status": LeaveStatus.PENDING.value,
        "adminComment": None,
        "appliedOn": datetime.utcnow(),
        "reviewedAt": None,
        "reviewedBy": None
    }
    
    result = db.leaves.insert_one(leave_doc)
    leave_doc["_id"] = result.inserted_id
    
    return serialize_doc(leave_doc)

@app.get("/api/leaves")
def get_leaves(
    employee_id: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Get leave requests"""
    
    filter_query = {}
    
    # Non-admin users can only view their own leaves
    if current_user["role"] == UserRole.ADMIN.value:
        if employee_id:
            filter_query["employeeId"] = employee_id
    else:
        filter_query["employeeId"] = current_user["userId"]
    
    leaves = list(db.leaves.find(filter_query).sort("appliedOn", -1))
    
    return [serialize_doc(leave) for leave in leaves]

@app.put("/api/leaves/{leave_id}")
def update_leave(
    leave_id: str,
    update_data: LeaveUpdate,
    current_user: dict = Depends(get_current_admin)
):
    """Approve/Reject leave request (Admin only)"""
    
    update_dict = {
        "status": update_data.status.value,
        "reviewedAt": datetime.utcnow(),
        "reviewedBy": current_user["userId"]
    }
    
    if update_data.adminComment:
        update_dict["adminComment"] = update_data.adminComment
    
    try:
        result = db.leaves.find_one_and_update(
            {"_id": ObjectId(leave_id)},
            {"$set": update_dict},
            return_document=True
        )
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid leave ID"
        )
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Leave request not found"
        )
    
    return serialize_doc(result)

# ============================================
# ROUTES - Salary Management
# ============================================

@app.get("/api/salary/{employee_id}")
def get_salary(
    employee_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get salary information"""
    
    # Users can only view their own salary unless they're admin
    if current_user["role"] != UserRole.ADMIN.value and current_user["userId"] != employee_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    salary = db.salaries.find_one({"employeeId": employee_id})
    if not salary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Salary information not found"
        )
    
    return serialize_doc(salary)

@app.get("/api/salaries")
def get_all_salaries(current_user: dict = Depends(get_current_admin)):
    """Get all salaries (Admin only)"""
    
    salaries = list(db.salaries.find())
    
    return [serialize_doc(salary) for salary in salaries]

@app.post("/api/salary", status_code=status.HTTP_201_CREATED)
def create_or_update_salary(
    salary_data: SalaryCreate,
    current_user: dict = Depends(get_current_admin)
):
    """Create or update salary information (Admin only)"""
    
    # Check if employee exists
    employee = db.users.find_one({"userId": salary_data.employeeId})
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found"
        )
    
    # Calculate net salary
    total_allowances = (
        salary_data.housingAllowance +
        salary_data.transportAllowance +
        salary_data.medicalAllowance +
        salary_data.otherAllowances
    )
    
    total_deductions = (
        salary_data.taxDeduction +
        salary_data.insuranceDeduction +
        salary_data.otherDeductions
    )
    
    net_salary = salary_data.basicSalary + total_allowances - total_deductions
    
    salary_doc = {
        "employeeId": salary_data.employeeId,
        "employeeName": employee["name"],
        "basicSalary": salary_data.basicSalary,
        "housingAllowance": salary_data.housingAllowance,
        "transportAllowance": salary_data.transportAllowance,
        "medicalAllowance": salary_data.medicalAllowance,
        "otherAllowances": salary_data.otherAllowances,
        "taxDeduction": salary_data.taxDeduction,
        "insuranceDeduction": salary_data.insuranceDeduction,
        "otherDeductions": salary_data.otherDeductions,
        "netSalary": net_salary,
        "effectiveDate": datetime.utcnow(),
        "updatedAt": datetime.utcnow()
    }
    
    # Upsert
    result = db.salaries.find_one_and_update(
        {"employeeId": salary_data.employeeId},
        {"$set": salary_doc},
        upsert=True,
        return_document=True
    )
    
    return serialize_doc(result)

# ============================================
# ROUTES - Dashboard Statistics
# ============================================

@app.get("/api/stats/admin")
def get_admin_stats(current_user: dict = Depends(get_current_admin)):
    """Get admin dashboard statistics"""
    
    total_employees = db.users.count_documents({"role": UserRole.EMPLOYEE.value})
    
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    present_today = db.attendance.count_documents({
        "date": {"$gte": today},
        "status": AttendanceStatus.PRESENT.value
    })
    
    pending_leaves = db.leaves.count_documents({"status": LeaveStatus.PENDING.value})
    
    # Calculate monthly payroll
    salaries = list(db.salaries.find())
    monthly_payroll = sum(s.get("netSalary", 0) for s in salaries)
    
    return {
        "totalEmployees": total_employees,
        "presentToday": present_today,
        "pendingLeaves": pending_leaves,
        "monthlyPayroll": round(monthly_payroll, 2)
    }

@app.get("/api/stats/employee")
def get_employee_stats(current_user: dict = Depends(get_current_user)):
    """Get employee dashboard statistics"""
    
    # Get current month attendance
    first_day = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    attendance_count = db.attendance.count_documents({
        "employeeId": current_user["userId"],
        "date": {"$gte": first_day},
        "status": AttendanceStatus.PRESENT.value
    })
    
    # Calculate total hours
    records = list(db.attendance.find({
        "employeeId": current_user["userId"],
        "date": {"$gte": first_day},
        "totalHours": {"$exists": True}
    }))
    total_hours = sum(r.get("totalHours", 0) for r in records)
    
    # Get leave counts
    approved_leaves = db.leaves.count_documents({
        "employeeId": current_user["userId"],
        "status": LeaveStatus.APPROVED.value
    })
    
    pending_leaves = db.leaves.count_documents({
        "employeeId": current_user["userId"],
        "status": LeaveStatus.PENDING.value
    })
    
    return {
        "attendanceThisMonth": attendance_count,
        "totalHours": round(total_hours, 1),
        "leavesTaken": approved_leaves,
        "pendingLeaves": pending_leaves
    }

# ============================================
# MAIN ENTRY POINT
# ============================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=True
    )